from __future__ import annotations

import os
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Callable

from app.config.settings import Settings
from app.domain.errors import AppError
from app.domain.models import Scene

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_SENSITIVE_LOG_VALUE = re.compile(r"(?i)\b(api[_-]?key|token|secret|authorization)\s*[=:]\s*\S+")


class RunpodMuseTalkLogTailer:
    """Forward a bounded, redacted subset of RunPod MuseTalk logs to an AutoClip job."""

    def __init__(self, settings: Settings, emit: Callable[[str], None], log_file: str = "/workspace/musetalk/logs/latest-inference.log"):
        self.settings = settings
        self.emit = emit
        self.log_file = log_file
        self._process: subprocess.Popen[str] | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        cfg = getattr(self.settings, "musetalk", None)
        ltx = getattr(self.settings, "ltx", None)
        f5 = self.settings.runpod_f5
        ssh_host = getattr(cfg, "ssh_host", "") or getattr(ltx, "ssh_host", "") or f5.ssh_host
        ssh_port = (getattr(cfg, "ssh_port", None) if getattr(cfg, "ssh_host", "") else None) or (getattr(ltx, "ssh_port", None) if getattr(ltx, "ssh_host", "") else None) or f5.ssh_port or 22
        ssh_user = (getattr(cfg, "ssh_user", None) if getattr(cfg, "ssh_host", "") else None) or (getattr(ltx, "ssh_user", None) if getattr(ltx, "ssh_host", "") else None) or f5.ssh_user or "root"
        key_path = ((getattr(cfg, "ssh_key_path", None) if getattr(cfg, "ssh_host", "") else None) or (getattr(ltx, "ssh_key_path", None) if getattr(ltx, "ssh_host", "") else None) or f5.ssh_key_path).expanduser()
        if not ssh_host or not key_path.is_file():
            return
        command = [
            "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
            "-o", "ServerAliveInterval=15",
            "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-i", str(key_path),
            "-p", str(ssh_port), f"{ssh_user}@{ssh_host}",
            f"tail -n 0 -F -- {self.log_file} 2>/dev/null",
        ]
        try:
            self._process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        except OSError as exc:
            self.emit(f"RunPod MuseTalk log stream unavailable: {exc}")
            return
        self._thread = threading.Thread(target=self._read, name="autoclip-musetalk-log", daemon=True)
        self._thread.start()

    def _read(self) -> None:
        if self._process is None or self._process.stdout is None:
            return
        try:
            for raw_line in self._process.stdout:
                line = _ANSI_ESCAPE.sub("", raw_line).strip()
                if not line or line.startswith(("#", "//", "/*")):
                    continue
                if _SENSITIVE_LOG_VALUE.search(line):
                    continue
                self.emit(line)
        except Exception:
            pass

    def stop(self) -> None:
        if self._process is not None:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
            self._process = None


class RunpodMuseTalkClient:
    """Client for rendering Audio-driven Lip-sync via MuseTalk on RunPod."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.config = getattr(settings, "musetalk", None) or getattr(settings, "ltx", None)

    @property
    def ssh_host(self) -> str:
        cfg_host = getattr(self.config, "ssh_host", "")
        if cfg_host:
            return cfg_host
        ltx_host = getattr(self.settings.ltx, "ssh_host", "")
        if ltx_host:
            return ltx_host
        return self.settings.runpod_f5.ssh_host

    @property
    def ssh_port(self) -> int:
        if getattr(self.config, "ssh_host", ""):
            return getattr(self.config, "ssh_port", 22)
        if getattr(self.settings.ltx, "ssh_host", ""):
            return getattr(self.settings.ltx, "ssh_port", 22)
        return self.settings.runpod_f5.ssh_port

    @property
    def ssh_user(self) -> str:
        if getattr(self.config, "ssh_host", ""):
            return getattr(self.config, "ssh_user", "root")
        if getattr(self.settings.ltx, "ssh_host", ""):
            return getattr(self.settings.ltx, "ssh_user", "root")
        return self.settings.runpod_f5.ssh_user

    @property
    def key_path(self) -> Path:
        if getattr(self.config, "ssh_host", "") and getattr(self.config, "ssh_key_path", None):
            return Path(self.config.ssh_key_path).expanduser()
        if getattr(self.settings.ltx, "ssh_host", "") and getattr(self.settings.ltx, "ssh_key_path", None):
            return Path(self.settings.ltx.ssh_key_path).expanduser()
        return Path(self.settings.runpod_f5.ssh_key_path).expanduser()

    def check_connection(self) -> None:
        enabled = getattr(self.config, "enabled", True)
        if not enabled or not self.ssh_host or not self.key_path.is_file():
            raise AppError("MUSE_TALK_NOT_CONFIGURED", "MuseTalk Lip-sync ยังไม่ได้กำหนด RunPod connector")

        try:
            self._ssh(["test", "-d", str(getattr(self.config, "musetalk_root", "/workspace/musetalk"))])
        except Exception as exc:
            raise AppError("MUSE_TALK_CONNECTION_FAILED", "AutoClip เชื่อมต่อ RunPod MuseTalk ไม่สำเร็จ") from exc

    def sync_lips(
        self,
        job_id: str,
        scene: Scene,
        input_media: Path,
        audio: Path,
        output: Path,
        bbox_shift: int | None = None,
    ) -> Path:
        """Run MuseTalk lip-sync on RunPod given input video/image and audio .wav."""
        if not input_media.is_file():
            raise AppError("MUSE_TALK_INPUT_MISSING", f"Input media not found for scene {scene.id}")
        if not audio.is_file():
            raise AppError("MUSE_TALK_AUDIO_MISSING", f"Audio not found for scene {scene.id}")

        musetalk_root = str(getattr(self.config, "musetalk_root", "/workspace/musetalk"))
        remote_input_dir = f"{musetalk_root}/input/{job_id[:8]}"
        remote_output_dir = f"{musetalk_root}/output/{job_id[:8]}/{scene.id}"
        remote_log_dir = f"{musetalk_root}/logs"

        safe_media_name = f"scene-{scene.id}{input_media.suffix.lower()}"
        safe_audio_name = f"scene-{scene.id}{audio.suffix.lower()}"
        remote_media_path = f"{remote_input_dir}/{safe_media_name}"
        remote_audio_path = f"{remote_input_dir}/{safe_audio_name}"
        run_name = f"autoclip-{job_id[:8]}-{scene.id}"

        shift = bbox_shift if bbox_shift is not None else getattr(self.config, "bbox_shift", 0)

        try:
            self._ssh(["mkdir", "-p", remote_input_dir, remote_output_dir, remote_log_dir])
            self._scp_to(input_media, remote_media_path)
            self._scp_to(audio, remote_audio_path)

            remote_task_yaml = f"{remote_input_dir}/task_{scene.id}.yaml"
            yaml_content = f"""task_0:
  video_path: "{remote_media_path}"
  audio_path: "{remote_audio_path}"
  bbox_shift: {shift}
  result_dir: "{remote_output_dir}"
"""
            self._ssh([f"cat << 'EOF' > {remote_task_yaml}\n{yaml_content}\nEOF"])

            cmd = (
                f"cd {musetalk_root} && "
                f"export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 && "
                f"{musetalk_root}/.venv/bin/python -m scripts.inference "
                f"--inference_config {remote_task_yaml} "
                f"--result_dir {remote_output_dir} "
                f"--use_float16 "
                f"> {remote_log_dir}/{run_name}-inference.log 2>&1"
            )
            self._ssh([cmd])

            remote_find = self._ssh_output([
                f"ls -t {remote_output_dir}/*.mp4 2>/dev/null | head -n 1"
            ]).strip()

            if not remote_find:
                remote_find = self._ssh_output([
                    f"find {remote_output_dir} -name '*.mp4' | head -n 1"
                ]).strip()

            if not remote_find:
                raise AppError("MUSE_TALK_OUTPUT_MISSING", f"MuseTalk Lip-sync เสร็จแล้ว แต่ไม่พบไฟล์วิดีโอของ {scene.id}")

            output.parent.mkdir(parents=True, exist_ok=True)
            self._scp_from(remote_find, output)
            return output

        except AppError:
            raise
        except subprocess.TimeoutExpired as exc:
            raise AppError("MUSE_TALK_TIMEOUT", f"MuseTalk Lip-sync หมดเวลา (timeout) สำหรับ {scene.id}") from exc
        except Exception as exc:
            raise AppError("MUSE_TALK_FAILED", f"MuseTalk Lip-sync scene {scene.id} ไม่สำเร็จ: {exc}") from exc

    def _ssh_base_cmd(self) -> list[str]:
        return [
            "ssh",
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout=10",
            "-o", "ServerAliveInterval=30",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-i", str(self.key_path),
            "-p", str(self.ssh_port),
            f"{self.ssh_user}@{self.ssh_host}",
        ]

    def _ssh(self, remote_cmd: list[str]) -> None:
        timeout = getattr(self.config, "timeout_seconds", 600)
        cmd = [*self._ssh_base_cmd(), " ".join(remote_cmd) if len(remote_cmd) == 1 else subprocess.list2cmdline(remote_cmd)]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if res.returncode != 0:
            raise AppError("MUSE_TALK_COMMAND_FAILED", f"RunPod MuseTalk remote command failed (code {res.returncode}): {res.stderr.strip() or res.stdout.strip()}")

    def _ssh_output(self, remote_cmd: list[str]) -> str:
        timeout = getattr(self.config, "timeout_seconds", 600)
        cmd = [*self._ssh_base_cmd(), " ".join(remote_cmd) if len(remote_cmd) == 1 else subprocess.list2cmdline(remote_cmd)]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return res.stdout.strip()

    def _scp_to(self, local_path: Path, remote_path: str) -> None:
        cmd = [
            "scp",
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-i", str(self.key_path),
            "-P", str(self.ssh_port),
            str(local_path),
            f"{self.ssh_user}@{self.ssh_host}:{remote_path}",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode != 0:
            raise AppError("MUSE_TALK_SCP_FAILED", f"Failed to upload to RunPod ({local_path.name}): {res.stderr.strip()}")

    def _scp_from(self, remote_path: str, local_path: Path) -> None:
        cmd = [
            "scp",
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-i", str(self.key_path),
            "-P", str(self.ssh_port),
            f"{self.ssh_user}@{self.ssh_host}:{remote_path}",
            str(local_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode != 0:
            raise AppError("MUSE_TALK_SCP_FAILED", f"Failed to download from RunPod ({local_path.name}): {res.stderr.strip()}")
