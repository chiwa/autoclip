from __future__ import annotations

import base64
import json
import logging
import shutil
import threading
import uuid
import zipfile
from pathlib import Path
from typing import Protocol
import re

import requests

from app.config.settings import Settings
from app.domain.ai_models import AiChatMessage, AiProgressEntry, AiProject, AiProjectStatus, AiScene
from app.domain.errors import AppError
from app.domain.models import Script
from app.services.package_service import PackageService
from app.services.persistence import Persistence

logger = logging.getLogger("autoclip.ai")

BRAND_NARRATION = "ค้นพบโลก ค้นพบใจ กับ Mamase"
BRAND_SUBTITLE = "Mamase\nจักรวาลของใจ"
MOTIONS = {"none", "auto", "slow_zoom_in", "slow_zoom_out", "pan_left_to_right", "pan_right_to_left", "pan_up", "pan_down", "zoom_in", "zoom_out", "zoom_in_top_left", "zoom_in_top_right", "zoom_in_bottom_left", "zoom_in_bottom_right", "pan_left_to_right_zoom_in", "pan_right_to_left_zoom_in", "pan_up_zoom_in", "pan_down_zoom_in", "drift_top_left", "drift_top_right", "drift_bottom_left", "drift_bottom_right", "cinematic_push_in", "cinematic_pull_out", "gentle_float", "documentary_pan"}
TRANSITIONS = {"none", "fade", "dissolve", "fade_black", "fade_white", "wipe_left", "wipe_right", "wipe_up", "wipe_down", "slide_left", "slide_right", "slide_up", "slide_down", "smooth_left", "smooth_right", "smooth_up", "smooth_down", "zoom_in", "pixelize", "radial"}

AUTO_PACKAGE_INSTRUCTIONS = """You are Mamase จักรวาลของใจ's automatic package planner.
Create a factual, engaging Thai short-form science, mystery, world, or trending-news video package.
Return JSON only: {"scenes":[...]}. Create 8-11 scenes including the final brand outro.
Every scene needs id, narration, tts_text when the narration has English or scientific names,
subtitle, image_prompt, motion, transition, estimated_duration, and wan.
Write tts_text as smooth connected speech. Ellipses (...) are allowed sparingly for a natural playful beat,
for example "เฮ้ย... จริงดิ?", but never scatter them through every sentence.
Scene 1 must be a premium 9:16 science-documentary key art: the recurring Mamase anime presenter,
the same black tousled hair and rectangular glasses, an outfit appropriate to the topic, a natural
expression, a readable Thai topic title and a separate short Thai hook. Reserve lower-center space
for subtitles. Other scenes use narration-specific documentary b-roll with no text or watermark.
Keep each scene visually distinct and about 4-6 seconds. Use only supported motions and transitions:
motion one of slow_zoom_in, slow_zoom_out, cinematic_push_in, cinematic_pull_out, documentary_pan,
gentle_float, pan_left_to_right, pan_right_to_left; transition one of fade, dissolve, smooth_left,
smooth_right, fade_black, none. For every scene include a wan object with prompt, negative_prompt,
seed, frames=81, lip_sync=false. Hook scene sets character_id=mamase-presenter-v1 and steps=25;
ordinary scenes omit steps. The final brand outro is added by AutoClip, so do not include it.
Never state unverified claims as facts. Keep the Thai narration friendly, curious, playful, and natural,
not like a news anchor."""


class ChatProvider(Protocol):
    def reply(self, messages: list[AiChatMessage]) -> tuple[str, list[AiScene] | None]: ...


class ImageProvider(Protocol):
    def generate(self, prompt: str, output: Path) -> Path: ...


class OpenAIChatProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
        if not settings.openai_api_key:
            raise AppError("AI_NOT_CONFIGURED", "ยังไม่ได้ตั้งค่า OPENAI_API_KEY")

    def reply(self, messages: list[AiChatMessage]) -> tuple[str, list[AiScene] | None]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.settings.openai_api_key, timeout=90)
            response = client.responses.create(model=self.settings.openai_model, instructions=self.settings.ai_instructions, input=[{"role": m.role, "content": m.content} for m in messages])
            text = response.output_text
        except AppError:
            raise
        except Exception as exc:
            status_code = getattr(exc, "status_code", None)
            error_code = getattr(exc, "code", None)
            if status_code == 401:
                raise AppError("AI_AUTH_FAILED", "OPENAI_API_KEY ไม่ถูกต้องหรือหมดอายุ") from exc
            if status_code == 429 and error_code in {"insufficient_quota", "credit_balance_exhausted"}:
                raise AppError("AI_QUOTA_EXHAUSTED", "OpenAI ไม่มีเครดิตเหลือสำหรับสร้างข้อความ กรุณาเติมเครดิตก่อนใช้งาน") from exc
            if status_code == 429:
                raise AppError("AI_RATE_LIMITED", "คำขอ AI มากเกินไปชั่วคราว กรุณาลองใหม่อีกครั้ง") from exc
            raise AppError("AI_REQUEST_FAILED", "ไม่สามารถติดต่อผู้ช่วย AI ได้") from exc
        try:
            data = json.loads(text)
            scenes = [AiScene.model_validate(item) for item in data.get("scenes", [])] if isinstance(data, dict) and data.get("scenes") else None
            return str(data.get("message", text) if isinstance(data, dict) else text), scenes
        except (json.JSONDecodeError, TypeError, ValueError):
            return text, None


class OpenAIImageProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
        if not settings.openai_api_key:
            raise AppError("AI_NOT_CONFIGURED", "ยังไม่ได้ตั้งค่า OPENAI_API_KEY")

    def generate(self, prompt: str, output: Path) -> Path:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.settings.openai_api_key, timeout=120)
            result = client.images.generate(model=self.settings.image_model, prompt=f"Vertical 9:16 documentary image, no text, no watermark. {prompt}", size="1024x1536", response_format="b64_json")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(base64.b64decode(result.data[0].b64_json))
            return output
        except AppError:
            raise
        except Exception as exc:
            raise AppError("AI_IMAGE_GENERATION_FAILED", "สร้างภาพฉากนี้ไม่สำเร็จ") from exc


class GeminiAutoProvider:
    """Server-only Gemini provider for the no-chat automatic package flow."""

    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, settings: Settings):
        self.settings = settings
        if not settings.gemini_api_key:
            raise AppError("AI_NOT_CONFIGURED", "ยังไม่ได้ตั้งค่า GEMINI_API_KEY")

    def _generate(self, model: str, body: dict, timeout: int) -> dict:
        try:
            response = requests.post(
                self.endpoint.format(model=model),
                headers={"x-goog-api-key": self.settings.gemini_api_key, "Content-Type": "application/json"},
                json=body,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise AppError("AI_REQUEST_FAILED", "ไม่สามารถเชื่อมต่อ Gemini ได้") from exc
        if response.status_code in {401, 403}:
            raise AppError("AI_AUTH_FAILED", "GEMINI_API_KEY ใช้งานไม่ได้หรือไม่มีสิทธิ์ใช้โมเดลนี้")
        if response.status_code == 429:
            raise AppError("AI_RATE_LIMITED", "Gemini ใช้งานเกินโควต้าชั่วคราว กรุณาลองใหม่")
        if not response.ok:
            try:
                detail = str(response.json().get("error", {}).get("message", "")).strip()
            except ValueError:
                detail = ""
            # API messages are useful for model/quota diagnosis but do not
            # contain the server-only credential. Keep them short for the UI.
            suffix = f" ({detail[:240]})" if detail else ""
            raise AppError("AI_REQUEST_FAILED", f"Gemini ปฏิเสธคำขอ HTTP {response.status_code}{suffix}")
        try:
            return response.json()
        except ValueError as exc:
            raise AppError("AI_REQUEST_FAILED", "Gemini ตอบกลับในรูปแบบที่อ่านไม่ได้") from exc

    def plan(self, topic: str, concept: str) -> tuple[list[AiScene], list[str]]:
        request_text = f"{AUTO_PACKAGE_INSTRUCTIONS}\n\nหัวข้อ: {topic}\nแนวคิดจากผู้ใช้: {concept or '-'}"
        data = self._generate(self.settings.gemini_text_model, {
            "contents": [{"parts": [{"text": request_text}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }, 120)
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts)
        try:
            payload = json.loads(text.removeprefix("```json").removesuffix("```").strip())
            raw_scenes = payload.get("scenes", [])
            if not isinstance(raw_scenes, list):
                raise ValueError("scenes is not a list")
            fallback_notes: list[str] = []
            scenes = [self._normalise_scene(raw, index, fallback_notes) for index, raw in enumerate(raw_scenes, 1)]
            return scenes, fallback_notes
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise AppError("AI_OUTPUT_INVALID", "Gemini วางโครงสร้าง scene ไม่ถูกต้อง กรุณาลองใหม่") from exc

    def _normalise_scene(self, raw: object, index: int, notes: list[str]) -> AiScene:
        if not isinstance(raw, dict):
            raise ValueError("scene is not an object")
        narration = str(raw.get("narration", "")).strip()
        if not narration:
            raise ValueError("scene has no narration")
        raw_id = str(raw.get("id", "")).strip()
        safe_id = re.sub(r"[^A-Za-z0-9._-]+", "-", raw_id).strip("-.")
        if not safe_id:
            safe_id = f"scene-{index:02d}"
        if safe_id != raw_id:
            notes.append(f"Scene {index}: ปรับ id เป็น {safe_id}")
        motion = str(raw.get("motion", "cinematic_push_in")).strip()
        if motion not in MOTIONS:
            notes.append(f"Scene {index}: motion '{motion}' ไม่รองรับ จึงใช้ cinematic_push_in")
            motion = "cinematic_push_in"
        transition = str(raw.get("transition", "fade")).strip()
        if transition not in TRANSITIONS:
            notes.append(f"Scene {index}: transition '{transition}' ไม่รองรับ จึงใช้ fade")
            transition = "fade"
        try:
            duration = float(raw.get("estimated_duration", 5.0))
        except (TypeError, ValueError):
            duration = 5.0
            notes.append(f"Scene {index}: ปรับระยะเวลาเป็น 5 วินาที")
        clamped = min(120.0, max(0.5, duration))
        if clamped != duration:
            notes.append(f"Scene {index}: ปรับระยะเวลาให้อยู่ในช่วงปลอดภัย")
        image_prompt = str(raw.get("image_prompt", "")).strip() or f"Cinematic documentary image matching this narration: {narration}"
        if not str(raw.get("image_prompt", "")).strip():
            notes.append(f"Scene {index}: สร้าง image prompt จากบทบรรยาย")
        wan = raw.get("wan") if isinstance(raw.get("wan"), dict) else {}
        if not wan:
            notes.append(f"Scene {index}: เติม Wan plan มาตรฐาน")
        wan = {
            "prompt": str(wan.get("prompt", image_prompt)).strip() or image_prompt,
            "negative_prompt": str(wan.get("negative_prompt", "text, subtitles, watermark, logo, flicker, jitter, distorted hands")).strip(),
            "seed": wan.get("seed", 1000 + index),
            "frames": 81,
            "lip_sync": bool(wan.get("lip_sync", False)),
            **({"steps": 25, "character_id": "mamase-presenter-v1"} if index == 1 else ({"steps": wan["steps"]} if isinstance(wan.get("steps"), int) and 10 <= wan["steps"] <= 50 else {})),
        }
        tts_text = str(raw["tts_text"]).strip() if raw.get("tts_text") else None
        return AiScene(
            id=safe_id,
            narration=narration,
            tts_text=tts_text,
            subtitle=str(raw["subtitle"]).strip() if raw.get("subtitle") else narration,
            show_subtitle=bool(raw.get("show_subtitle", True)),
            image_prompt=image_prompt,
            motion=motion,
            transition=transition,
            estimated_duration=clamped,
            wan=wan,
        )

    def image(self, prompt: str, output: Path, aspect_ratio: str = "9:16", reference: Path | None = None) -> Path:
        parts: list[dict] = [{"text": prompt}]
        if reference and reference.is_file():
            parts.insert(0, {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(reference.read_bytes()).decode("ascii")}})
        data = self._generate(self.settings.gemini_image_model, {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                # Gemini's REST API expects image settings directly as
                # generationConfig.imageConfig.  responseFormat belongs to a
                # different API surface and makes otherwise valid 9:16 image
                # requests fail with HTTP 400.
                "imageConfig": {"aspectRatio": aspect_ratio, "imageSize": "1K"},
            },
        }, 180)
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        inline = next((part.get("inlineData") for part in parts if part.get("inlineData", {}).get("data")), None)
        if not inline:
            raise AppError("AI_IMAGE_GENERATION_FAILED", "Gemini ไม่ได้ส่งภาพกลับมาสำหรับฉากนี้")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(base64.b64decode(inline["data"]))
        return output


class AiProjectService:
    def __init__(self, settings: Settings, chat_provider: ChatProvider | None = None, image_provider: ImageProvider | None = None, persistence: Persistence | None = None):
        self.settings = settings
        self.root = settings.app.workspace / "ai-projects"
        self.root.mkdir(parents=True, exist_ok=True)
        self.chat_provider = chat_provider
        self.image_provider = image_provider
        self._lock = threading.RLock()
        self.persistence = persistence

    @property
    def configured(self) -> bool:
        return bool(self.settings.gemini_api_key or self.settings.openai_api_key)

    def _log(self, project: AiProject, progress: int, step: str, message: str, level: str = "INFO") -> AiProject:
        project.progress = progress
        project.current_step = step
        project.logs.append(AiProgressEntry(level=level, message=message))
        # Keep response payloads bounded while retaining enough context to
        # investigate a failed automatic package job from the UI.
        project.logs = project.logs[-150:]
        return self._save(project)

    def _wait_with_heartbeat(self, project_id: str, step: str, message: str, action):
        """Run a blocking provider call without leaving the browser silent."""
        done = threading.Event()
        result: list[object] = []
        failure: list[BaseException] = []

        def invoke() -> None:
            try:
                result.append(action())
            except BaseException as exc:  # re-raised in the owning worker
                failure.append(exc)
            finally:
                done.set()

        threading.Thread(target=invoke, daemon=True, name=f"autoclip-provider-{project_id[:8]}").start()
        waited = 0
        while not done.wait(10):
            waited += 10
            project = self.get(project_id)
            self._log(project, project.progress, step, f"{message} · ยังทำงานอยู่ ({waited} วินาที)", "HEARTBEAT")
        if failure:
            raise failure[0]
        return result[0]

    def _path(self, project_id: str) -> Path:
        if not project_id or Path(project_id).name != project_id or project_id in {".", ".."}:
            raise AppError("AI_PROJECT_NOT_FOUND", "ไม่พบโปรเจกต์ AI")
        return self.root / project_id / "project.json"

    def _save(self, project: AiProject) -> AiProject:
        path = self._path(project.project_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        project.updated_at = __import__("app.domain.events", fromlist=["local_now"]).local_now()
        path.write_text(project.model_dump_json(indent=2), encoding="utf-8")
        if self.persistence:
            self.persistence.upsert_project(project)
        return project

    def create(self, topic: str = "") -> AiProject:
        project = AiProject(project_id=str(uuid.uuid4()), topic=topic[:500])
        project.messages.append(AiChatMessage(role="assistant", content="สวัสดีครับ เล่า topic หรือแนววิดีโอที่ต้องการได้เลย ผมจะช่วยจัดทำ Scene Preview ให้ตรวจสอบก่อนสร้าง ZIP"))
        return self._save(project)

    def create_automatic(self, topic: str, concept: str = "") -> AiProject:
        topic = topic.strip()
        concept = concept.strip()
        if not topic:
            raise AppError("AI_INPUT_INVALID", "กรุณาระบุหัวข้อ")
        if len(topic) > 500 or len(concept) > 4000:
            raise AppError("AI_INPUT_INVALID", "หัวข้อหรือแนวคิดยาวเกินไป")
        if not self.settings.gemini_api_key:
            raise AppError("AI_NOT_CONFIGURED", "ยังไม่ได้ตั้งค่า GEMINI_API_KEY สำหรับสร้าง ZIP อัตโนมัติ")
        project = AiProject(project_id=str(uuid.uuid4()), topic=topic, status=AiProjectStatus.SCRIPT_GENERATING)
        project.messages = []
        self._log(project, 1, "กำลังเตรียมบท", "เริ่มวาง script และ shot plan จากหัวข้อและแนวคิด")
        thread = threading.Thread(target=self._automatic_worker, args=(project.project_id, concept), daemon=True, name=f"autoclip-ai-{project.project_id[:8]}")
        thread.start()
        return project

    def _automatic_worker(self, project_id: str, concept: str) -> None:
        try:
            project = self.get(project_id)
            self._log(project, 8, "กำลังวางบทและ shot plan", "Gemini กำลังใช้มาตรฐาน Mamase เพื่อวางเรื่องและลำดับ scene")
            provider = GeminiAutoProvider(self.settings)
            planned_scenes, fallback_notes = self._wait_with_heartbeat(
                project_id,
                "กำลังวางบทและ shot plan",
                "กำลังรอผลจาก Gemini",
                lambda: provider.plan(project.topic, concept),
            )
            scenes = self._validate_scenes(planned_scenes)
            project.scenes = scenes
            project.revision += 1
            self._save(project)
            self._log(project, 18, "ตรวจโครงสร้าง scene", f"ได้ {len(scenes)} scenes ตามลำดับที่จะอยู่ใน script.json")
            for note in fallback_notes:
                self._log(project, 18, "ใช้ค่า fallback", note, "WARNING")
            project = self.get(project_id)
            project.status = AiProjectStatus.SCRIPT_READY
            self._save(project)
            self._log(project, 25, "บทพร้อมให้ตรวจ", "ตรวจและแก้บท/shot plan ก่อนกดสร้างภาพ")
        except AppError as exc:
            project = self.get(project_id)
            project.status = AiProjectStatus.FAILED
            project.error = {"code": exc.code, "message": exc.message}
            self._log(project, project.progress, "สร้างบทไม่สำเร็จ", exc.message, "ERROR")
        except Exception:
            logger.exception("automatic AI package failed project_id=%s", project_id)
            project = self.get(project_id)
            project.status = AiProjectStatus.FAILED
            project.error = {"code": "AI_PACKAGE_FAILED", "message": "ระบบสร้าง ZIP ไม่สำเร็จ กรุณาลองใหม่"}
            self._log(project, project.progress, "สร้างบทไม่สำเร็จ", "เกิดข้อผิดพลาดภายใน โปรดตรวจ technical log", "ERROR")

    def start_image_generation(self, project_id: str) -> AiProject:
        project = self.get(project_id)
        # A provider can reject a single image request after the script was
        # already planned correctly.  Keep that work reviewable/retryable;
        # users should not need to create a new project or re-plan the story.
        if project.status not in {AiProjectStatus.SCRIPT_READY, AiProjectStatus.FAILED} or not project.scenes:
            raise AppError("SCRIPT_NOT_APPROVED", "กรุณาตรวจบทให้เสร็จก่อนสร้างภาพ")
        project.status = AiProjectStatus.IMAGES_GENERATING
        project.error = None
        self._log(project, 28, "กำลังเริ่มสร้างภาพ", "บทได้รับการอนุมัติแล้ว กำลังสร้างภาพตามแต่ละ scene")
        thread = threading.Thread(target=self._image_worker, args=(project_id,), daemon=True, name=f"autoclip-images-{project_id[:8]}")
        thread.start()
        return project

    def _image_worker(self, project_id: str) -> None:
        try:
            provider = GeminiAutoProvider(self.settings)
            project = self.get(project_id)
            preview_dir = self.root / project_id / "preview-images"
            total = len(project.scenes)
            for index, scene in enumerate(project.scenes, 1):
                project = self.get(project_id)
                current = next(item for item in project.scenes if item.id == scene.id)
                existing = self.root / project_id / current.image_path if current.image_path else None
                if existing and existing.is_file():
                    self._log(project, min(90, 28 + int(index / total * 62)), f"ใช้ภาพเดิม Scene {index}/{total}", f"พบภาพ {current.id} ที่สร้างสำเร็จแล้ว จึงไม่สร้างซ้ำ")
                    continue
                if current.id.endswith("brand-outro"):
                    self._log(project, 88, "เตรียมภาพ branding", "กำลังนำ outro มาตรฐาน Mamase เข้า package")
                    target = preview_dir / f"{current.id}.png"
                    self._copy_brand_outro(target)
                else:
                    progress = 28 + int(index / total * 55)
                    self._log(project, progress, f"กำลังสร้างภาพ Scene {index}/{total}", f"Gemini กำลังสร้างภาพที่ตรงกับบทของ {current.id}")
                    target = preview_dir / f"{current.id}.png"
                    reference = Path(__file__).parents[2] / "assets" / "characters" / "mamase-presenter-v1.png" if index == 1 else None
                    self._wait_with_heartbeat(
                        project_id,
                        f"กำลังสร้างภาพ Scene {index}/{total}",
                        f"Gemini กำลังสร้างภาพ {current.id}",
                        lambda: provider.image(current.image_prompt, target, reference=reference),
                    )
                project = self.get(project_id)
                target_scene = next(item for item in project.scenes if item.id == scene.id)
                target_scene.image_path = f"preview-images/{scene.id}.png"
                self._save(project)
                self._log(project, min(90, 28 + int(index / total * 62)), f"ตรวจภาพ Scene {index}/{total}", f"รับภาพ {scene.id} แล้ว")
            project = self.get(project_id)
            project.status = AiProjectStatus.PREVIEW_NEEDS_REVIEW
            self._save(project)
            self._log(project, 90, "พร้อมให้ตรวจภาพ", "แก้และสร้างภาพใหม่เฉพาะ scene ได้ ก่อนกดอนุมัติสร้าง ZIP")
        except AppError as exc:
            project = self.get(project_id)
            project.status = AiProjectStatus.FAILED
            project.error = {"code": exc.code, "message": exc.message}
            self._log(project, project.progress, "สร้างภาพไม่สำเร็จ", exc.message, "ERROR")
        except Exception:
            logger.exception("AI image generation failed project_id=%s", project_id)
            project = self.get(project_id)
            project.status = AiProjectStatus.FAILED
            project.error = {"code": "AI_IMAGE_GENERATION_FAILED", "message": "ระบบสร้างภาพไม่สำเร็จ กรุณาลองใหม่"}
            self._log(project, project.progress, "สร้างภาพไม่สำเร็จ", "เกิดข้อผิดพลาดภายใน โปรดตรวจ technical log", "ERROR")

    def _copy_brand_outro(self, target: Path) -> None:
        archive_path = Path(__file__).parents[2] / "dist" / "mamase-roman-space-telescope-wan-v2.zip"
        if not archive_path.is_file():
            raise AppError("BRAND_ASSET_MISSING", "ไม่พบภาพ outro มาตรฐาน Mamase")
        with zipfile.ZipFile(archive_path) as archive:
            script = json.loads(archive.read("script.json"))
            final_scene = script["scenes"][-1]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(final_scene["image"]))

    def get(self, project_id: str) -> AiProject:
        path = self._path(project_id)
        if not path.is_file():
            raise AppError("AI_PROJECT_NOT_FOUND", "ไม่พบโปรเจกต์ AI")
        try:
            return AiProject.model_validate_json(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise AppError("INTERNAL_ERROR", "ข้อมูลโปรเจกต์เสียหาย") from exc

    def duplicate(self, project_id: str) -> AiProject:
        source = self.get(project_id)
        clone = AiProject(project_id=str(uuid.uuid4()), topic=source.topic, scenes=[s.model_copy(deep=True) for s in source.scenes])
        clone.messages = [m.model_copy(deep=True) for m in source.messages]
        clone.invalidate_confirmation() if clone.scenes else None
        return self._save(clone)

    def message(self, project_id: str, content: str) -> AiProject:
        project = self.get(project_id)
        if len(content.strip()) > 8000 or not content.strip():
            raise AppError("AI_INPUT_INVALID", "ข้อความต้องมีความยาวเหมาะสม")
        project.messages.append(AiChatMessage(role="user", content=content.strip()))
        provider = self.chat_provider or OpenAIChatProvider(self.settings)
        reply, scenes = provider.reply(project.messages)
        project.messages.append(AiChatMessage(role="assistant", content=reply))
        if scenes:
            project.scenes = self._validate_scenes(scenes)
            project.invalidate_confirmation()
        return self._save(project)

    def create_preview(self, project_id: str) -> AiProject:
        project = self.get(project_id)
        if not project.scenes:
            provider = self.chat_provider or OpenAIChatProvider(self.settings)
            reply, scenes = provider.reply(project.messages + [AiChatMessage(role="user", content="สร้าง Scene Preview แบบครบถ้วน 7 ฉากเนื้อหาและ 1 ฉากแบรนด์ Mamase")])
            if not scenes:
                raise AppError("AI_OUTPUT_INVALID", "ผู้ช่วย AI ยังไม่ได้ส่งโครงสร้างฉากที่ถูกต้อง")
            project.messages.append(AiChatMessage(role="assistant", content=reply))
            project.scenes = self._validate_scenes(scenes)
        project.status = AiProjectStatus.PREVIEW_GENERATING
        project = self._save(project)
        image_provider = self.image_provider or OpenAIImageProvider(self.settings)
        preview_dir = self.root / project_id / "preview-images"
        for scene in project.scenes:
            if scene.image_path and (self.root / project_id / scene.image_path).is_file():
                continue
            if scene.id.endswith("brand-outro"):
                brand = Path(__file__).parents[1] / "../.codex/skills/autoclip-content/assets/mamase-brand-outro.png"
                if not brand.is_file():
                    brand = Path(".codex/skills/autoclip-content/assets/mamase-brand-outro.png")
                target = preview_dir / f"{scene.id}.png"; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(brand, target)
            else:
                image_provider.generate(scene.image_prompt, preview_dir / f"{scene.id}.png")
            scene.image_path = f"preview-images/{scene.id}.png"
        project.status = AiProjectStatus.PREVIEW_READY
        project.revision += 1
        return self._save(project)

    def _validate_scenes(self, scenes: list[AiScene]) -> list[AiScene]:
        if not 1 <= len(scenes) <= 20:
            raise AppError("AI_OUTPUT_INVALID", "จำนวนฉากต้องอยู่ระหว่าง 1 ถึง 20")
        seen = set()
        for scene in scenes:
            if scene.id in seen or scene.motion not in MOTIONS or (scene.transition and scene.transition not in TRANSITIONS):
                raise AppError("AI_OUTPUT_INVALID", "ข้อมูลฉากมี motion/transition หรือ id ไม่ถูกต้อง")
            seen.add(scene.id)
        if not any(s.id.endswith("brand-outro") for s in scenes):
            scenes.append(AiScene(id=f"scene-{len(scenes)+1:02d}-brand-outro", narration=BRAND_NARRATION, subtitle=BRAND_SUBTITLE, image_prompt="Mamase brand outro", motion="none", transition="none"))
        else:
            brand = next(s for s in scenes if s.id.endswith("brand-outro")); scenes = [s for s in scenes if s is not brand] + [brand]
        return scenes

    def update_scene(self, project_id: str, scene_id: str, changes: dict) -> AiProject:
        project = self.get(project_id); scene = next((s for s in project.scenes if s.id == scene_id), None)
        if not scene: raise AppError("SCENE_NOT_FOUND", "ไม่พบฉากที่ระบุ")
        allowed = {"narration", "tts_text", "subtitle", "show_subtitle", "image_prompt", "motion", "transition", "estimated_duration", "wan"}
        scene = scene.model_copy(update={k: v for k, v in changes.items() if k in allowed})
        project.scenes[project.scenes.index(next(s for s in project.scenes if s.id == scene_id))] = scene
        project.confirmed_revision = None
        project.revision += 1
        has_complete_images = bool(project.scenes) and all(
            item.image_path and (self.root / project_id / item.image_path).is_file()
            for item in project.scenes
        )
        project.status = AiProjectStatus.PREVIEW_NEEDS_REVIEW if has_complete_images else AiProjectStatus.SCRIPT_READY
        return self._save(project)

    def regenerate_image(self, project_id: str, scene_id: str) -> AiProject:
        project = self.get(project_id); scene = next((s for s in project.scenes if s.id == scene_id), None)
        if not scene: raise AppError("SCENE_NOT_FOUND", "ไม่พบฉากที่ระบุ")
        if self.settings.gemini_api_key:
            provider = GeminiAutoProvider(self.settings)
            reference = Path(__file__).parents[2] / "assets" / "characters" / "mamase-presenter-v1.png" if project.scenes.index(scene) == 0 else None
            path = self.root / project_id / "preview-images" / f"{scene.id}.png"
            provider.image(scene.image_prompt, path, reference=reference)
        else:
            provider = self.image_provider or OpenAIImageProvider(self.settings)
            path = self.root / project_id / "preview-images" / f"{scene.id}.png"
            provider.generate(scene.image_prompt, path)
        scene.image_path = f"preview-images/{scene.id}.png"
        project.invalidate_confirmation()
        self._log(project, 90, "อัปเดต Scene Preview", f"สร้างภาพใหม่สำหรับ {scene.id} แล้ว")
        return self.get(project_id)

    def confirm(self, project_id: str) -> AiProject:
        project = self.get(project_id)
        if not project.scenes or any(not s.image_path or not (self.root / project_id / s.image_path).is_file() for s in project.scenes):
            raise AppError("PREVIEW_NOT_READY", "Scene Preview ยังมีภาพไม่ครบ")
        project.confirmed_revision = project.revision; project.status = AiProjectStatus.PREVIEW_CONFIRMED; return self._save(project)

    def approve_and_build_package(self, project_id: str) -> Path:
        project = self.confirm(project_id)
        self._log(project, 94, "กำลังสร้าง ZIP", "Scene Preview ได้รับการอนุมัติ กำลังตรวจและประกอบ package")
        path = self.build_package(project_id)
        project = self.get(project_id)
        self._log(project, 100, "ZIP พร้อมดาวน์โหลด", f"ตรวจ package สำเร็จ: {path.name}")
        return path

    def build_package(self, project_id: str) -> Path:
        project = self.get(project_id)
        if project.status != AiProjectStatus.PREVIEW_CONFIRMED or project.confirmed_revision != project.revision:
            raise AppError("PREVIEW_NOT_CONFIRMED", "ต้องกดยืนยัน Scene Preview ก่อนสร้าง ZIP")
        project.status = AiProjectStatus.PACKAGING; self._save(project)
        package_root = self.root / project_id / f"package-v{len(project.package_versions)+1}"
        images = package_root / "images"; images.mkdir(parents=True, exist_ok=True)
        scenes = []
        for i, scene in enumerate(project.scenes, 1):
            target = images / f"scene-{i:02d}.png"; shutil.copyfile(self.root / project_id / scene.image_path, target)
            payload = {"id": scene.id, "image": f"images/{target.name}", "narration": scene.narration, "subtitle": scene.subtitle, "show_subtitle": scene.show_subtitle, "motion": scene.motion, "transition": scene.transition, "motion_speed": "slow"}
            if scene.tts_text:
                payload["tts_text"] = scene.tts_text
            if scene.wan:
                payload["wan"] = scene.wan
            scenes.append(payload)
        script = {"project": {"id": project_id, "title": project.topic or "Mamase AI Project", "language": "th-TH", "resolution": "1080x1920", "fps": 30}, "voice": {"provider": "google-gemini", "voice": self.settings.tts.google_voice, "speed": self.settings.tts.google_speaking_rate, "style_prompt": self.settings.tts.google_style_prompt}, "scenes": scenes}
        (package_root / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
        metadata = {"title": project.topic or "Mamase AI Project", "description": f"{project.topic}\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n#Mamase #จักรวาลของใจ"}
        (package_root / "video-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        zip_path = self.root / project_id / f"{project_id}-v{len(project.package_versions)+1}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in package_root.rglob("*"):
                if path.is_file(): archive.write(path, path.relative_to(package_root).as_posix())
        PackageService(self.settings.app.max_extracted_mb * 1024 * 1024).extract_and_validate(zip_path, self.root / project_id / "validated")
        project.package_versions.append(zip_path.name)
        project.package_path = str(zip_path)
        project.package_summary = {
            "filename": zip_path.name,
            "sceneCount": len(scenes),
            "imageCount": len(scenes),
            "resolution": script["project"]["resolution"],
            "ttsProvider": script["voice"]["provider"],
            "ttsVoice": script["voice"]["voice"],
            "wanReadyScenes": sum(1 for scene in scenes if scene.get("wan")),
            "validated": True,
        }
        project.status = AiProjectStatus.PACKAGE_READY
        self._save(project)
        if self.persistence:
            self.persistence.add_package(project_id, project.revision, zip_path, "VALID")
        return zip_path
