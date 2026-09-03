from __future__ import annotations

import time
import uuid
from pathlib import Path
from urllib.parse import urlencode

import requests

from app.config.settings import Settings
from app.domain.errors import AppError
from app.domain.models import Scene


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

    def render_scene(self, job_id: str, scene: Scene, image: Path, output: Path) -> Path:
        if scene.wan is None:
            raise AppError("WAN_SCENE_CONFIG_MISSING", f"Scene {scene.id} ยังไม่มี Wan prompt")
        uploaded_name = self._upload_image(job_id, scene.id, image)
        prompt_id = self._queue(self._workflow(job_id, scene, uploaded_name))
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
                    outputs = history.get("outputs", {}).get("11", {}).get("images", [])
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

    @staticmethod
    def _workflow(job_id: str, scene: Scene, uploaded_name: str) -> dict:
        wan = scene.wan
        assert wan is not None
        # Native Wan 2.2 workflow confirmed against this Pod's /object_info.
        # WanImageToVideo outputs conditioned positive/negative and latent at
        # indices 0/1/2 respectively; using the raw text encodes loses image
        # conditioning and using index 0 as latent is invalid.
        return {
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.2_ti2v_5B_fp16.safetensors", "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan", "device": "default"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "wan2.2_vae.safetensors"}},
            "4": {"class_type": "LoadImage", "inputs": {"image": uploaded_name}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"text": wan.prompt, "clip": ["2", 0]}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": wan.negative_prompt, "clip": ["2", 0]}},
            "7": {"class_type": "WanImageToVideo", "inputs": {"positive": ["5", 0], "negative": ["6", 0], "vae": ["3", 0], "width": 352, "height": 640, "length": wan.frames or 81, "batch_size": 1, "start_image": ["4", 0]}},
            "8": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "seed": wan.seed if wan.seed is not None else 0, "steps": 12, "cfg": 5.0, "sampler_name": "euler", "scheduler": "simple", "positive": ["7", 0], "negative": ["7", 1], "latent_image": ["7", 2], "denoise": 1.0}},
            "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
            "10": {"class_type": "CreateVideo", "inputs": {"images": ["9", 0], "fps": 16.0}},
            "11": {"class_type": "SaveVideo", "inputs": {"video": ["10", 0], "filename_prefix": f"autoclip/{job_id}/{scene.id}", "format": "mp4", "codec": "h264"}},
        }
