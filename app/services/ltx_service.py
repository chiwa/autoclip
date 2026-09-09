from __future__ import annotations

import math
import os
import re
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from app.config.settings import Settings
from app.domain.errors import AppError
from app.domain.models import Scene, WanSceneOptions

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_SENSITIVE_LOG_VALUE = re.compile(r"(?i)\b(api[_-]?key|token|secret|authorization)\s*[=:]\s*\S+")

LTX_DEFAULT_FPS = 15
LTX_DEFAULT_STEPS = 8
LTX_DEFAULT_WIDTH = 448
LTX_DEFAULT_HEIGHT = 768


def ltx_frames_for_duration(duration_seconds: float, requested_frames: int | None = None, fps: int = LTX_DEFAULT_FPS) -> int:
    """Return an LTX-compatible 8n+1 frame count that strictly covers narration duration.

    LTX requires frame counts in the form 8n+1 (e.g., 9, 17, 25, ..., 49, 121).
    Frames are rounded up so the generated video is never shorter than the speech.
    """
    raw_audio_frames = math.ceil(max(0.0, float(duration_seconds)) * fps)
    required_n = max(1, math.ceil((raw_audio_frames - 1) / 8))
    if requested_frames is not None and requested_frames > 0:
        requested_n = max(1, math.ceil((requested_frames - 1) / 8))
        n = max(required_n, requested_n)
    else:
        n = required_n
    return n * 8 + 1


class RunpodLtxLogTailer:
    """Forward a bounded, redacted subset of RunPod LTX logs to an AutoClip job."""

    def __init__(self, settings: Settings, emit: Callable[[str], None], log_file: str = "/workspace/ltx-video-poc/logs/latest-inference.log"):
        self.settings = settings
        self.emit = emit
        self.log_file = log_file
        self._process: subprocess.Popen[str] | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        remote = getattr(self.settings, "ltx", None) or self.settings.runpod_f5
        key_path = remote.ssh_key_path.expanduser()
        if not remote.ssh_host or not key_path.is_file():
            return
        command = [
            "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
            "-o", "ServerAliveInterval=15",
            "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-i", str(key_path),
            "-p", str(remote.ssh_port), f"{remote.ssh_user}@{remote.ssh_host}",
            f"tail -n 0 -F -- {self.log_file} 2>/dev/null",
        ]
        try:
            self._process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        except OSError as exc:
            self.emit(f"RunPod LTX log stream unavailable: {exc}")
            return
        self._thread = threading.Thread(target=self._read, name="autoclip-ltx-log", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._process.kill()

    def _read(self) -> None:
        assert self._process and self._process.stdout
        for raw in self._process.stdout:
            if message := self._sanitize(raw):
                self.emit(message)

    @staticmethod
    def _sanitize(raw: str) -> str:
        value = _ANSI_ESCAPE.sub("", raw.rsplit("\r", 1)[-1])
        value = _SENSITIVE_LOG_VALUE.sub(r"\1=[redacted]", value)
        value = " ".join(value.split())
        return value if value and len(value) <= 1000 else ""


class RunpodLtxClient:
    """Client for executing LTX-Video 2B Distilled on RunPod via SSH/SCP."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.config = getattr(settings, "ltx", None) or settings.wan
        self.remote = getattr(settings, "ltx", None) or settings.runpod_f5

    def check_connection(self) -> None:
        enabled = getattr(self.config, "enabled", False) or getattr(self.settings.wan, "enabled", False)
        ssh_host = getattr(self.remote, "ssh_host", "") or self.settings.runpod_f5.ssh_host
        key_path = (getattr(self.remote, "ssh_key_path", None) or self.settings.runpod_f5.ssh_key_path).expanduser()

        if not enabled or not ssh_host or not key_path.is_file():
            raise AppError("LTX_NOT_CONFIGURED", "LTX Video ยังไม่ได้เชื่อมต่อกับ AutoClip กรุณาเลือก FFmpeg Motion หรือกำหนด RunPod connector ก่อน")

        try:
            self._ssh(["test", "-d", str(getattr(self.config, "poc_root", "/workspace/ltx-video-poc"))])
        except Exception as exc:
            raise AppError("LTX_CONNECTION_FAILED", "AutoClip เชื่อมต่อ RunPod LTX ไม่สำเร็จ") from exc

    def render_scene(
        self,
        job_id: str,
        scene: Scene,
        image: Path,
        output: Path,
        width: int | None = None,
        height: int | None = None,
        frames: int | None = None,
        fps: int | None = None,
        duration_seconds: float | None = None,
    ) -> Path:
        motion_plan = getattr(scene, "ltx", None) or scene.wan
        if motion_plan is None:
            raise AppError("LTX_SCENE_CONFIG_MISSING", f"Scene {scene.id} ยังไม่มี LTX/Wan prompt")

        target_fps = fps or getattr(self.config, "fps", LTX_DEFAULT_FPS)
        target_w = width or getattr(self.config, "width", LTX_DEFAULT_WIDTH)
        target_h = height or getattr(self.config, "height", LTX_DEFAULT_HEIGHT)

        if frames is not None:
            target_frames = frames
        elif duration_seconds is not None:
            target_frames = ltx_frames_for_duration(duration_seconds, motion_plan.frames, fps=target_fps)
        else:
            target_frames = motion_plan.frames or 49

        poc_root = str(getattr(self.config, "poc_root", "/workspace/ltx-video-poc"))
        remote_input_dir = f"{poc_root}/input"
        remote_output_dir = f"{poc_root}/output"
        remote_log_dir = f"{poc_root}/logs"

        safe_img_name = f"autoclip-{job_id[:8]}-{scene.id}{image.suffix.lower()}"
        remote_img_path = f"{remote_input_dir}/{safe_img_name}"
        run_name = f"autoclip-{job_id[:8]}-{scene.id}"

        remote_scene_output_dir = f"{poc_root}/output/{job_id[:8]}/{scene.id}"

        try:
            self._ssh(["mkdir", "-p", remote_input_dir, remote_scene_output_dir, remote_log_dir])
            self._scp_to(image, remote_img_path)

            # Execute inference on RunPod
            seed = motion_plan.seed if motion_plan.seed is not None else getattr(self.config, "seed", 171198)
            prompt = motion_plan.prompt
            negative_prompt = motion_plan.negative_prompt

            cli_args = [
                f"{poc_root}/.venv/bin/python",
                f"{poc_root}/LTX-Video/inference.py",
                "--prompt", prompt,
                "--conditioning_media_paths", remote_img_path,
                "--conditioning_start_frames", "0",
                "--height", str(target_h),
                "--width", str(target_w),
                "--num_frames", str(target_frames),
                "--frame_rate", str(target_fps),
                "--seed", str(seed),
                "--pipeline_config", f"{poc_root}/ltxv-2b-distilled-poc.yaml",
                "--output_path", remote_scene_output_dir,
            ]
            if negative_prompt:
                cli_args.extend(["--negative_prompt", negative_prompt])

            cmd = (
                f"cd {poc_root}/LTX-Video && "
                f"export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 && "
                f"{subprocess.list2cmdline(cli_args)} "
                f"> {remote_log_dir}/{run_name}-inference.log 2>&1"
            )

            self._ssh([cmd])

            # Find the generated video in remote output directory
            remote_find = self._ssh_output([
                f"ls -t {remote_scene_output_dir}/*.mp4 2>/dev/null | head -n 1"
            ]).strip()

            if not remote_find:
                raise AppError("LTX_OUTPUT_MISSING", f"LTX render เสร็จแล้ว แต่ไม่พบไฟล์วิดีโอของ {scene.id}")

            output.parent.mkdir(parents=True, exist_ok=True)
            self._scp_from(remote_find, output)

        except AppError:
            raise
        except Exception as exc:
            raise AppError("LTX_RENDER_FAILED", f"LTX Video render scene {scene.id} ไม่สำเร็จ: {exc}") from exc

        if not output.is_file() or output.stat().st_size == 0:
            raise AppError("LTX_DOWNLOAD_FAILED", f"วิดีโอ LTX ที่ได้รับจาก scene {scene.id} มีขนาดเป็นศูนย์หรือไม่พบไฟล์")

        return output

    def _ssh(self, remote_args: list[str]) -> None:
        ssh_host = getattr(self.remote, "ssh_host", "") or self.settings.runpod_f5.ssh_host
        ssh_port = getattr(self.remote, "ssh_port", 22) or self.settings.runpod_f5.ssh_port
        ssh_user = getattr(self.remote, "ssh_user", "root") or self.settings.runpod_f5.ssh_user
        key_path = (getattr(self.remote, "ssh_key_path", None) or self.settings.runpod_f5.ssh_key_path).expanduser()
        timeout = getattr(self.config, "timeout_seconds", 900)

        command = [
            "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-i", str(key_path), "-p", str(ssh_port),
            f"{ssh_user}@{ssh_host}", *remote_args
        ]
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout, check=False)
        if completed.returncode != 0:
            raise AppError("LTX_COMMAND_FAILED", f"RunPod LTX remote command failed (code {completed.returncode}): {completed.stderr.strip() or completed.stdout.strip()}")

    def _ssh_output(self, remote_args: list[str]) -> str:
        ssh_host = getattr(self.remote, "ssh_host", "") or self.settings.runpod_f5.ssh_host
        ssh_port = getattr(self.remote, "ssh_port", 22) or self.settings.runpod_f5.ssh_port
        ssh_user = getattr(self.remote, "ssh_user", "root") or self.settings.runpod_f5.ssh_user
        key_path = (getattr(self.remote, "ssh_key_path", None) or self.settings.runpod_f5.ssh_key_path).expanduser()
        timeout = getattr(self.config, "timeout_seconds", 900)

        command = [
            "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-i", str(key_path), "-p", str(ssh_port),
            f"{ssh_user}@{ssh_host}", *remote_args
        ]
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout, check=False)
        if completed.returncode != 0:
            raise AppError("LTX_COMMAND_FAILED", f"RunPod LTX remote command failed: {completed.stderr.strip()}")
        return completed.stdout

    def _scp_to(self, source: Path, remote_path: str) -> None:
        ssh_host = getattr(self.remote, "ssh_host", "") or self.settings.runpod_f5.ssh_host
        ssh_port = getattr(self.remote, "ssh_port", 22) or self.settings.runpod_f5.ssh_port
        ssh_user = getattr(self.remote, "ssh_user", "root") or self.settings.runpod_f5.ssh_user
        key_path = (getattr(self.remote, "ssh_key_path", None) or self.settings.runpod_f5.ssh_key_path).expanduser()
        timeout = getattr(self.config, "timeout_seconds", 900)

        command = [
            "scp", "-P", str(ssh_port), "-i", str(key_path),
            "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            str(source), f"{ssh_user}@{ssh_host}:{remote_path}"
        ]
        if subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout, check=False).returncode != 0:
            raise AppError("LTX_UPLOAD_FAILED", f"ไม่สามารถส่งไฟล์ {source.name} ไปยัง RunPod LTX ได้")

    def _scp_from(self, remote_path: str, output: Path) -> None:
        ssh_host = getattr(self.remote, "ssh_host", "") or self.settings.runpod_f5.ssh_host
        ssh_port = getattr(self.remote, "ssh_port", 22) or self.settings.runpod_f5.ssh_port
        ssh_user = getattr(self.remote, "ssh_user", "root") or self.settings.runpod_f5.ssh_user
        key_path = (getattr(self.remote, "ssh_key_path", None) or self.settings.runpod_f5.ssh_key_path).expanduser()
        timeout = getattr(self.config, "timeout_seconds", 900)

        command = [
            "scp", "-P", str(ssh_port), "-i", str(key_path),
            "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            f"{ssh_user}@{ssh_host}:{remote_path}", str(output)
        ]
        if subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout, check=False).returncode != 0:
            raise AppError("LTX_DOWNLOAD_FAILED", f"ไม่สามารถรับไฟล์วิดีโอจาก RunPod LTX ({remote_path}) ได้")
