from __future__ import annotations

import re
import subprocess
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import urlencode

import requests

from app.config.settings import Settings
from app.domain.errors import AppError
from app.domain.models import Scene


_ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_SENSITIVE_LOG_VALUE = re.compile(r"(?i)\b(api[_-]?key|token|secret|authorization)\s*[=:]\s*\S+")


class RunpodComfyLogTailer:
    """Forward a bounded, redacted subset of ComfyUI logs to an AutoClip job."""

    def __init__(self, settings: Settings, emit):
        self.settings = settings
        self.emit = emit
        self._process: subprocess.Popen[str] | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        remote = self.settings.runpod_f5
        key_path = remote.ssh_key_path.expanduser()
        if not remote.ssh_host or not key_path.is_file():
            return
        command = [
            "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
            "-o", "ServerAliveInterval=15", "-i", str(key_path),
            "-p", str(remote.ssh_port), f"{remote.ssh_user}@{remote.ssh_host}",
            "tail -n 0 -F -- /workspace/comfyui.log",
        ]
        try:
            self._process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        except OSError as exc:
            self.emit(f"RunPod log stream unavailable: {exc}")
            return
        self._thread = threading.Thread(target=self._read, name="autoclip-runpod-log", daemon=True)
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


class ComfyWanClient:
    """Small, explicit client for a local-only ComfyUI Wan 2.2 endpoint."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = (settings.wan.comfy_url or "").rstrip("/")
        self.timeout = settings.wan.request_timeout_seconds

    def check_connection(self) -> None:
        if not self.settings.wan.enabled or not self.base_url:
            raise AppError("WAN_NOT_CONFIGURED", "Wan 2.2 ยังไม่ได้เชื่อมต่อกับ AutoClip กรุณาเลือก FFmpeg Motion หรือกำหนด RunPod connector ก่อน")
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise AppError("WAN_CONNECTION_FAILED", "AutoClip เชื่อมต่อ ComfyUI บน RunPod ไม่สำเร็จ") from exc

    def render_scene(self, job_id: str, scene: Scene, image: Path, output: Path, width: int | None = None, height: int | None = None, frames: int | None = None) -> Path:
        if scene.wan is None:
            raise AppError("WAN_SCENE_CONFIG_MISSING", f"Scene {scene.id} ยังไม่มี Wan prompt")
        target_w = width or getattr(self.settings.wan, "width", 704)
        target_h = height or getattr(self.settings.wan, "height", 1280)
        target_frames = frames or scene.wan.frames or 81
        uploaded_name = self._upload_image(job_id, scene.id, image)
        prompt_id = self._queue(self._workflow(job_id, scene, uploaded_name, target_w, target_h, target_frames))
        result = self._wait_for_output(prompt_id)
        return self._download_output(result, output)

    def _upload_image(self, job_id: str, scene_id: str, image: Path) -> str:
        safe_name = f"autoclip-{job_id[:8]}-{scene_id}{image.suffix.lower()}"
        try:
            with image.open("rb") as stream:
                response = requests.post(
                    f"{self.base_url}/upload/image",
                    files={"image": (safe_name, stream, "image/png")},
                    data={"overwrite": "true"},
                    timeout=self.timeout,
                )
            response.raise_for_status()
            body = response.json()
            return f"{body.get('subfolder', '').strip('/')}/{body['name']}".lstrip("/")
        except (OSError, KeyError, ValueError, requests.RequestException) as exc:
            raise AppError("WAN_IMAGE_UPLOAD_FAILED", f"ไม่สามารถส่งภาพของ {scene_id} ไปยัง Wan ได้") from exc

    def _queue(self, workflow: dict) -> str:
        try:
            response = requests.post(f"{self.base_url}/prompt", json={"prompt": workflow, "client_id": f"autoclip-{uuid.uuid4()}"}, timeout=self.timeout)
            response.raise_for_status()
            body = response.json()
            if body.get("node_errors"):
                raise ValueError("workflow validation failed")
            return str(body["prompt_id"])
        except (KeyError, ValueError, requests.RequestException) as exc:
            raise AppError("WAN_WORKFLOW_REJECTED", "ComfyUI ไม่รับ workflow Wan 2.2") from exc

    def _wait_for_output(self, prompt_id: str) -> dict:
        deadline = time.monotonic() + self.settings.wan.generation_timeout_seconds
        while time.monotonic() < deadline:
            try:
                response = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=self.timeout)
                response.raise_for_status()
                history = response.json().get(prompt_id)
            except requests.RequestException as exc:
                raise AppError("WAN_CONNECTION_FAILED", "การเชื่อมต่อ ComfyUI หลุดระหว่างรอ render") from exc
            if history:
                status = history.get("status", {})
                if status.get("status_str") == "success":
                    outputs = None
                    for node_out in history.get("outputs", {}).values():
                        if "images" in node_out and node_out["images"]:
                            outputs = node_out["images"]
                            break
                    if outputs:
                        return outputs[0]
                    raise AppError("WAN_OUTPUT_MISSING", "Wan render เสร็จแล้ว แต่ไม่พบไฟล์วิดีโอ")
                messages = status.get("messages", [])
                if any(message and message[0] == "execution_error" for message in messages):
                    raise AppError("WAN_RENDER_FAILED", "Wan 2.2 render ไม่สำเร็จ")
            time.sleep(self.settings.wan.poll_interval_seconds)
        raise AppError("WAN_RENDER_TIMEOUT", "Wan 2.2 ใช้เวลานานเกินกว่าที่กำหนด")

    def _download_output(self, result: dict, output: Path) -> Path:
        params = urlencode({"filename": result["filename"], "subfolder": result.get("subfolder", ""), "type": result.get("type", "output")})
        try:
            response = requests.get(f"{self.base_url}/view?{params}", timeout=self.timeout, stream=True)
            response.raise_for_status()
            with output.open("wb") as stream:
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        stream.write(chunk)
        except (KeyError, OSError, requests.RequestException) as exc:
            raise AppError("WAN_DOWNLOAD_FAILED", "ไม่สามารถรับวิดีโอ Wan กลับจาก ComfyUI ได้") from exc
        if output.stat().st_size == 0:
            raise AppError("WAN_DOWNLOAD_FAILED", "วิดีโอ Wan ที่ได้รับมีขนาดเป็นศูนย์")
        return output

    def _workflow(self, job_id: str, scene: Scene, uploaded_name: str, width: int = 704, height: int = 1280, frames: int = 81) -> dict:
        wan = scene.wan
        assert wan is not None
        # Native Wan 2.2 TI2V workflow confirmed against ComfyUI templates.
        # Wan 2.2 uses 48-channel latents generated by Wan22ImageToVideoLatent,
        # ModelSamplingSD3 with shift 8.0, and positive/negative text conditioning
        # routed directly from CLIPTextEncode to KSampler.
        steps = wan.steps if wan.steps is not None else self.settings.wan.steps
        cfg = getattr(self.settings.wan, "cfg", 5.0)
        sampler_name = getattr(self.settings.wan, "sampler_name", "uni_pc")
        return {
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.2_ti2v_5B_fp16.safetensors", "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan", "device": "default"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "wan2.2_vae.safetensors"}},
            "4": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": 8.0}},
            "5": {"class_type": "LoadImage", "inputs": {"image": uploaded_name}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": wan.prompt, "clip": ["2", 0]}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": wan.negative_prompt, "clip": ["2", 0]}},
            "8": {"class_type": "Wan22ImageToVideoLatent", "inputs": {"vae": ["3", 0], "start_image": ["5", 0], "width": width, "height": height, "length": frames, "batch_size": 1}},
            "9": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "seed": wan.seed if wan.seed is not None else 0, "steps": steps, "cfg": cfg, "sampler_name": sampler_name, "scheduler": "simple", "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["8", 0], "denoise": 1.0}},
            "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["3", 0]}},
            "11": {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "fps": 16.0}},
            "12": {"class_type": "SaveVideo", "inputs": {"video": ["11", 0], "filename_prefix": f"autoclip/{job_id}/{scene.id}", "format": "mp4", "codec": "h264"}},
        }
