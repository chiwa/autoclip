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

from app.config.settings import Settings
from app.domain.ai_models import AiChatMessage, AiProject, AiProjectStatus, AiScene
from app.domain.errors import AppError
from app.domain.models import Script
from app.services.package_service import PackageService
from app.services.persistence import Persistence

logger = logging.getLogger("autoclip.ai")

BRAND_NARRATION = "ค้นพบโลก ค้นพบใจ กับ Mamase"
BRAND_SUBTITLE = "Mamase\nจักรวาลของใจ"
MOTIONS = {"none", "auto", "slow_zoom_in", "slow_zoom_out", "pan_left_to_right", "pan_right_to_left", "pan_up", "pan_down", "zoom_in", "zoom_out", "zoom_in_top_left", "zoom_in_top_right", "zoom_in_bottom_left", "zoom_in_bottom_right", "pan_left_to_right_zoom_in", "pan_right_to_left_zoom_in", "pan_up_zoom_in", "pan_down_zoom_in", "drift_top_left", "drift_top_right", "drift_bottom_left", "drift_bottom_right", "cinematic_push_in", "cinematic_pull_out", "gentle_float", "documentary_pan"}
TRANSITIONS = {"none", "fade", "dissolve", "fade_black", "fade_white", "wipe_left", "wipe_right", "wipe_up", "wipe_down", "slide_left", "slide_right", "slide_up", "slide_down", "zoom_in", "pixelize", "radial"}


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
        return bool(self.settings.openai_api_key)

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
        allowed = {"narration", "subtitle", "show_subtitle", "image_prompt", "motion", "transition", "estimated_duration"}
        scene = scene.model_copy(update={k: v for k, v in changes.items() if k in allowed})
        project.scenes[project.scenes.index(next(s for s in project.scenes if s.id == scene_id))] = scene
        project.invalidate_confirmation(); return self._save(project)

    def regenerate_image(self, project_id: str, scene_id: str) -> AiProject:
        project = self.get(project_id); scene = next((s for s in project.scenes if s.id == scene_id), None)
        if not scene: raise AppError("SCENE_NOT_FOUND", "ไม่พบฉากที่ระบุ")
        provider = self.image_provider or OpenAIImageProvider(self.settings)
        path = self.root / project_id / "preview-images" / f"{scene.id}.png"; provider.generate(scene.image_prompt, path); scene.image_path = f"preview-images/{scene.id}.png"; project.invalidate_confirmation(); return self._save(project)

    def confirm(self, project_id: str) -> AiProject:
        project = self.get(project_id)
        if not project.scenes or any(not s.image_path or not (self.root / project_id / s.image_path).is_file() for s in project.scenes):
            raise AppError("PREVIEW_NOT_READY", "Scene Preview ยังมีภาพไม่ครบ")
        project.confirmed_revision = project.revision; project.status = AiProjectStatus.PREVIEW_CONFIRMED; return self._save(project)

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
            scenes.append({"id": scene.id, "image": f"images/{target.name}", "narration": scene.narration, "subtitle": scene.subtitle, "show_subtitle": scene.show_subtitle, "motion": scene.motion, "transition": scene.transition, "motion_speed": "slow"})
        script = {"project": {"id": project_id, "title": project.topic or "Mamase AI Project", "language": "th-TH", "resolution": "1080x1920", "fps": 30}, "voice": {"provider": "local", "voice": "thai-male-01", "speed": 1.0}, "scenes": scenes}
        (package_root / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
        zip_path = self.root / project_id / f"{project_id}-v{len(project.package_versions)+1}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in package_root.rglob("*"):
                if path.is_file(): archive.write(path, path.relative_to(package_root).as_posix())
        PackageService(self.settings.app.max_extracted_mb * 1024 * 1024).extract_and_validate(zip_path, self.root / project_id / "validated")
        project.package_versions.append(zip_path.name); project.status = AiProjectStatus.PACKAGE_READY; self._save(project); return zip_path
