from __future__ import annotations

import json
import zipfile
import logging
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.config.settings import Settings
from app.domain.enums import JobStatus
from app.domain.errors import AppError, public_error
from app.domain.events import JobEvent, JobEventPublisher, JobEventType, local_now
from app.domain.models import JobRecord
from app.infrastructure.ffmpeg import FfmpegRunner, FfprobeRunner
from app.infrastructure.filesystem import Workspace, WorkspaceManager
from app.infrastructure.tts import create_tts_provider
from app.services.package_service import PackageService
from app.services.pronunciation_service import PronunciationService
from app.services.bgm_service import ensure_default_bgm
from app.services.video_service import SceneRenderer, SubtitleRenderer, VideoComposer
from app.services.persistence import Persistence
from app.services.wan_service import ComfyWanClient

logger = logging.getLogger("autoclip.jobs")
SUPPORTED_RENDER_ENGINES = {"ffmpeg_motion", "wan2.2"}


class JobRegistry:
    def __init__(self):
        self._jobs: dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    def create(self, job_id: str) -> JobRecord:
        return self.set(JobRecord(job_id=job_id, status=JobStatus.RECEIVED, progress=0, current_step="Upload received"))

    def set(self, record: JobRecord) -> JobRecord:
        with self._lock:
            self._jobs[record.job_id] = record
        return record

    def update(self, job_id: str, status: JobStatus, progress: int, step: str, error: dict | None = None) -> None:
        with self._lock:
            current = self._jobs[job_id]
            self._jobs[job_id] = current.model_copy(update={"status": status, "progress": progress, "current_step": step, "error": error})

    def add_log(self, job_id: str, level: str, message: str, limit: int = 200) -> dict:
        entry = {"timestamp": local_now().isoformat(), "level": level, "message": message}
        with self._lock:
            current = self._jobs[job_id]
            self._jobs[job_id] = current.model_copy(update={"logs": [*current.logs, entry][-limit:]})
        return entry

    def set_project(self, job_id: str, project_id: str) -> None:
        with self._lock:
            current = self._jobs[job_id]
            self._jobs[job_id] = current.model_copy(update={"project_id": project_id})

    def set_metadata(self, job_id: str, metadata: dict) -> None:
        with self._lock:
            current = self._jobs[job_id]
            self._jobs[job_id] = current.model_copy(update={"metadata": metadata})

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)


class JobService:
    def __init__(self, settings: Settings, registry: JobRegistry | None = None, events: JobEventPublisher | None = None, persistence: Persistence | None = None):
        self.settings = settings
        self.registry = registry or JobRegistry()
        self.events = events or JobEventPublisher()
        self.workspaces = WorkspaceManager(settings.app.workspace)
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="autoclip")
        self.ffmpeg = FfmpegRunner()
        self.ffprobe = FfprobeRunner()
        self.persistence = persistence
        self.pronunciation = PronunciationService()

    def submit(self, uploaded_file, tts_provider: str | None = None, subtitle_mode: str | None = None, script_json: str | None = None, render_engine: str | None = None) -> JobRecord:
        selected_provider = (tts_provider or self.settings.tts.provider or "local").strip().lower()
        # Keep UI/config aliases backwards compatible while exposing one
        # canonical provider name to the rendering pipeline.
        selected_provider = {
            "vachana": "local",
            "vachana-tts": "local",
            "f5": "thonburian",
            "bird/f5-tts-thai": "bird-f5",
        }.get(selected_provider, selected_provider)
        if selected_provider not in {"dummy", "local", "kokoro", "kokoro-thai", "wayu-kokoro-thai", "thonburian", "bird", "bird-f5", "f5-thai", "f5-tts-thai", "khanomtan", "khanom-tan", "khanomtan-tts"}:
            raise AppError("TTS_GENERATION_FAILED", "Selected TTS model is unavailable")
        selected_engine = (render_engine or "ffmpeg_motion").strip().lower()
        if selected_engine not in SUPPORTED_RENDER_ENGINES:
            raise AppError("RENDER_ENGINE_INVALID", "Selected render engine is unavailable")
        job_id = str(uuid.uuid4())
        workspace = self.workspaces.create(job_id)
        input_path = workspace.source / "input.zip"
        max_bytes = self.settings.app.max_upload_mb * 1024 * 1024
        size = 0
        with input_path.open("wb") as output:
            while chunk := uploaded_file.file.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    output.close()
                    raise AppError("UPLOAD_TOO_LARGE", "Upload exceeds the configured size limit")
                output.write(chunk)
        if script_json:
            try:
                from app.domain.models import Script
                script = Script.model_validate(json.loads(script_json))
                replacement = input_path.with_suffix(".patched.zip")
                with zipfile.ZipFile(input_path) as source, zipfile.ZipFile(replacement, "w", zipfile.ZIP_DEFLATED) as target:
                    for item in source.infolist():
                        if item.filename == "script.json":
                            target.writestr(item, json.dumps(script.model_dump(mode="json"), ensure_ascii=False, indent=2))
                        else:
                            target.writestr(item, source.read(item))
                replacement.replace(input_path)
            except Exception as exc:
                logger.exception("script preview patch failed")
                raise AppError("SCRIPT_JSON_INVALID", "ค่าที่แก้ไขใน Scene Preview ไม่ถูกต้อง") from exc
        record = self.registry.set(JobRecord(job_id=job_id, status=JobStatus.RECEIVED, progress=0, current_step="Upload received", tts_provider=selected_provider, subtitle_mode=subtitle_mode, render_engine=selected_engine))
        if self.persistence: self.persistence.upsert_job(record)
        self._investigation_log(job_id, "job_received", render_engine=selected_engine, tts_provider=selected_provider, upload_bytes=size)
        self._log(job_id, "INFO", "Package uploaded")
        self._log(job_id, "INFO", f"Render engine selected: {selected_engine}")
        self._progress(job_id, JobStatus.RECEIVED, 2, "Package uploaded")
        self.executor.submit(self._process, job_id, workspace)
        return record

    def submit_path(self, package_path: Path, tts_provider: str | None = None, subtitle_mode: str | None = None, script_json: str | None = None, render_engine: str | None = None) -> JobRecord:
        """Submit a server-created package through the same render pipeline."""
        if not package_path.is_file():
            raise AppError("PACKAGE_INVALID", "Generated package is unavailable")
        class _File:
            def __init__(self, path: Path): self.file = path.open("rb")
        source = _File(package_path)
        try:
            return self.submit(source, tts_provider, subtitle_mode, script_json, render_engine)
        finally:
            source.file.close()

    def _progress(self, job_id: str, status: JobStatus, progress: int, step: str) -> None:
        self.registry.update(job_id, status, progress, step)
        if self.persistence:
            current = self.registry.get(job_id)
            if current: self.persistence.upsert_job(current)
        self.events.publish(JobEvent(type=JobEventType.PROGRESS, job_id=job_id, payload={"progress": progress, "status": status, "currentStep": step}))

    def _log(self, job_id: str, level: str, message: str) -> None:
        entry = self.registry.add_log(job_id, level, message)
        self.events.publish(JobEvent(type=JobEventType.LOG, job_id=job_id, payload=entry))

    def _investigation_log(self, job_id: str, event: str, **fields: object) -> None:
        """Emit compact, grep-friendly diagnostics without leaking secrets."""
        safe = " ".join(f"{key}={value}" for key, value in fields.items() if value is not None)
        logger.info("event=%s job_id=%s %s", event, job_id, safe)

    def _process(self, job_id: str, workspace: Workspace) -> None:
        started = time.monotonic()
        try:
            job = self.registry.get(job_id)
            render_engine = job.render_engine if job else "ffmpeg_motion"
            self._investigation_log(job_id, "job_started", render_engine=render_engine, workspace=workspace.root)
            self._progress(job_id, JobStatus.VALIDATING, 5, "Validating ZIP package")
            self._log(job_id, "INFO", "Validating ZIP package")
            package = PackageService(self.settings.app.max_extracted_mb * 1024 * 1024)
            script, bgm = package.extract_and_validate(workspace.source / "input.zip", workspace.extracted)
            self._investigation_log(job_id, "package_validated", render_engine=render_engine, project_id=script.project.id, scene_count=len(script.scenes), has_bgm=bool(bgm))
            if bgm is None:
                bgm = ensure_default_bgm(self.settings.app.workspace)
                self._log(job_id, "INFO", "No BGM in package; using system ambient background music")
            video_metadata = {"title": "-", "description": "-"}
            metadata_file = workspace.extracted / "video-metadata.json"
            if metadata_file.is_file():
                try:
                    raw_meta = json.loads(metadata_file.read_text(encoding="utf-8"))
                    if isinstance(raw_meta, dict):
                        video_metadata = {"title": str(raw_meta.get("title") or "-"), "description": str(raw_meta.get("description") or "-")}
                except Exception:
                    self._log(job_id, "WARNING", "video-metadata.json ไม่ถูกต้อง; ใช้ค่าเริ่มต้น (-)")
            self.registry.set_project(job_id, script.project.id)
            if self.persistence:
                self.persistence.ensure_project(script.project.id, script.project.title, len(script.scenes), "RENDERING")
                current = self.registry.get(job_id)
                if current: self.persistence.upsert_job(current)
            self._log(job_id, "INFO", "script.json validated")
            self._log(job_id, "INFO", f"{len(script.scenes)} scenes detected")
            wan_client: ComfyWanClient | None = None
            if render_engine == "wan2.2":
                self._progress(job_id, JobStatus.VALIDATING, 10, "Checking Wan 2.2 connection")
                self._investigation_log(job_id, "wan_connection_check", configured=self.settings.wan.enabled, comfy_url_configured=bool(self.settings.wan.comfy_url))
                wan_client = ComfyWanClient(self.settings)
                wan_client.check_connection()
                if any(scene.wan is None for scene in script.scenes):
                    raise AppError("WAN_SCENE_CONFIG_MISSING", "ทุก scene ต้องมี Wan prompt เมื่อเลือก Wan 2.2")
                self._log(job_id, "SUCCESS", "Connected to ComfyUI Wan 2.2")
            selected_provider = self.registry.get(job_id).tts_provider or self.settings.tts.provider
            provider = create_tts_provider(selected_provider, self.settings)
            count = len(script.scenes)
            durations: list[float] = []
            self._progress(job_id, JobStatus.GENERATING_AUDIO, 15, f"Generating narration 1 of {count}")
            for index, scene in enumerate(script.scenes):
                start_progress = 15 + round(25 * index / count)
                self._progress(job_id, JobStatus.GENERATING_AUDIO, start_progress, f"Generating narration {index + 1} of {count} (in progress)")
                self._log(job_id, "INFO", f"Generating narration {index + 1} of {count} (in progress)")
                self._investigation_log(job_id, "tts_started", render_engine=render_engine, scene_id=scene.id, scene_index=index + 1, scene_count=count, provider=selected_provider)
                output = workspace.generated_audio / f"{scene.id}.wav"
                try:
                    provider.synthesize(self.pronunciation.resolve_scene(scene), script.project.language, script.voice.voice, script.voice.speed, output)
                except AppError:
                    raise
                except Exception as exc:
                    raise AppError("TTS_GENERATION_FAILED", "Narration audio generation failed", {"sceneId": scene.id}) from exc
                durations.append(self.ffprobe.duration(output) + self.settings.video.scene_padding_seconds)
                self._investigation_log(job_id, "tts_completed", render_engine=render_engine, scene_id=scene.id, audio_seconds=round(durations[-1], 3))
                self._log(job_id, "SUCCESS", f"Narration generated {index + 1} of {count}")
                self._progress(job_id, JobStatus.GENERATING_AUDIO, 15 + round(25 * (index + 1) / count), f"Generated narration {index + 1} of {count}")
            subtitle_renderer = SubtitleRenderer()
            scene_renderer = SceneRenderer(self.ffmpeg, self.settings)
            rendered: list[Path] = []
            job_record = self.registry.get(job_id)
            sub_mode = (job_record.subtitle_mode if job_record else None) or "auto"
            transitions = [scene.transition or self.settings.video.transition for scene in script.scenes[:-1]]
            transition_seconds = 0.0
            if count > 1 and self.settings.video.transition_seconds > 0:
                transition_seconds = min(self.settings.video.transition_seconds, min(durations) / 2)
            for index, (scene, duration) in enumerate(zip(script.scenes, durations)):
                render_progress = 40 + round(35 * index / count)
                self._progress(job_id, JobStatus.RENDERING_SCENES, render_progress, f"Rendering scene {index + 1} of {count} (in progress)")
                scene_started = time.monotonic()
                self._investigation_log(job_id, "scene_render_started", render_engine=render_engine, scene_id=scene.id, scene_index=index + 1, motion=scene.motion, transition=scene.transition or self.settings.video.transition, duration_seconds=round(duration, 3))
                self._log(job_id, "INFO", f"Motion: {scene.motion} · Transition: {scene.transition or self.settings.video.transition}")
                if sub_mode == "disable":
                    show_sub = False
                elif sub_mode == "enable":
                    show_sub = True
                else:
                    show_sub = scene.show_subtitle and bool(scene.subtitle)

                if show_sub and (scene.subtitle or scene.narration):
                    entering_transition = transition_seconds if index > 0 and transitions[index - 1] != "none" else 0.0
                    leaving_transition = transition_seconds if index < count - 1 and transitions[index] != "none" else 0.0
                    subtitle_start = entering_transition
                    subtitle_end = duration - leaving_transition
                    if subtitle_end > subtitle_start + 0.05:
                        self._log(job_id, "INFO", f"Adding Thai subtitles to scene {index + 1}")
                        self._investigation_log(job_id, "subtitle_window", scene_id=scene.id, start_seconds=round(subtitle_start, 3), end_seconds=round(subtitle_end, 3), transition_seconds=round(transition_seconds, 3))
                        subtitle = subtitle_renderer.write(scene.subtitle or scene.narration, duration, workspace.subtitles / f"{scene.id}.srt", subtitle_start, subtitle_end)
                    else:
                        self._log(job_id, "WARNING", f"Skipping subtitles for scene {index + 1}; transition leaves no readable subtitle window")
                        subtitle = None
                else:
                    self._log(job_id, "INFO", f"Skipping subtitles for scene {index + 1} ({'disabled by global setting' if sub_mode == 'disable' else 'disabled in scene'})")
                    subtitle = None
                if wan_client:
                    self._progress(job_id, JobStatus.RENDERING_SCENES, render_progress, f"Rendering Wan scene {index + 1} of {count} (in progress)")
                    self._log(job_id, "INFO", f"Submitting scene {index + 1} to Wan 2.2")
                    wan_output = workspace.rendered_scenes / f"{scene.id}.wan.mp4"
                    wan_client.render_scene(job_id, scene, workspace.extracted / scene.image, wan_output)
                    self._log(job_id, "INFO", f"Wan scene {index + 1} received; adding narration and subtitles")
                    rendered.append(scene_renderer.render_wan_video(scene, wan_output, workspace.generated_audio / f"{scene.id}.wav", subtitle, duration, workspace.rendered_scenes / f"{scene.id}.mp4"))
                else:
                    rendered.append(scene_renderer.render(scene, workspace.extracted / scene.image, workspace.generated_audio / f"{scene.id}.wav", subtitle, duration, workspace.rendered_scenes / f"{scene.id}.mp4"))
                self._investigation_log(job_id, "scene_render_completed", render_engine=render_engine, scene_id=scene.id, output=rendered[-1].name, elapsed_ms=round((time.monotonic() - scene_started) * 1000))
                self._log(job_id, "SUCCESS", f"Scene rendered {index + 1} of {count}")
                self._progress(job_id, JobStatus.RENDERING_SCENES, 40 + round(35 * (index + 1) / count), f"Rendered scene {index + 1} of {count}")
            self._progress(job_id, JobStatus.COMPOSING, 80, "Combining scenes")
            self._log(job_id, "INFO", "Combining scenes")
            if bgm:
                self._log(job_id, "INFO", "Mixing background music")
            self._log(job_id, "INFO", "Normalizing audio")
            self._progress(job_id, JobStatus.COMPOSING, 92, "Creating final video")
            self._log(job_id, "INFO", "Creating final video")
            final = VideoComposer(self.ffmpeg, self.settings).compose(rendered, workspace.output, bgm, durations, transitions)
            self._investigation_log(job_id, "compose_completed", render_engine=render_engine, final_path=final.name, elapsed_ms=round((time.monotonic() - started) * 1000))
            probe = self.ffprobe.probe(final)
            video_stream = next(stream for stream in probe["streams"] if stream.get("codec_type") == "video")
            metadata = {
                "projectTitle": script.project.title,
                "durationSeconds": round(float(probe["format"]["duration"]), 3),
                "resolution": f"{video_stream['width']}x{video_stream['height']}",
                "sceneCount": count,
                "fileSizeBytes": final.stat().st_size,
                "createdAt": local_now().isoformat(),
                "videoMetadata": video_metadata,
            }
            self.registry.set_metadata(job_id, metadata)
            if self.persistence:
                current = self.registry.get(job_id)
                if current: self.persistence.upsert_job(current, final, metadata)
                if current and current.project_id: self.persistence.update_project_status(current.project_id, "COMPLETED")
            self._progress(job_id, JobStatus.COMPLETED, 100, "Video is ready")
            self._log(job_id, "SUCCESS", "Video generation completed")
            self.events.publish(JobEvent(type=JobEventType.COMPLETED, job_id=job_id, payload={"progress": 100, "status": JobStatus.COMPLETED, "previewUrl": f"/jobs/{job_id}/preview", "videoUrl": f"/api/jobs/{job_id}/video"}))
            self._investigation_log(job_id, "job_completed", render_engine=render_engine, elapsed_ms=round((time.monotonic() - started) * 1000))
        except AppError as exc:
            current = self.registry.get(job_id)
            progress = current.progress if current else 0
            step = current.current_step if current else "Processing job"
            safe_error = public_error(exc)
            self.registry.update(job_id, JobStatus.FAILED, progress, step, safe_error)
            if self.persistence:
                current = self.registry.get(job_id)
                if current: self.persistence.upsert_job(current)
            self._log(job_id, "ERROR", exc.message)
            self.events.publish(JobEvent(type=JobEventType.FAILED, job_id=job_id, payload={"progress": progress, "status": JobStatus.FAILED, "code": exc.code, "message": exc.message, "currentStep": step}))
            self._investigation_log(job_id, "job_failed", error_code=exc.code, elapsed_ms=round((time.monotonic() - started) * 1000))
            logger.exception("job_id=%s stage=FAILED error_code=%s", job_id, exc.code)
        except Exception:
            error = AppError("INTERNAL_ERROR", "An unexpected processing error occurred")
            current = self.registry.get(job_id)
            progress = current.progress if current else 0
            step = current.current_step if current else "Processing job"
            self.registry.update(job_id, JobStatus.FAILED, progress, step, public_error(error))
            if self.persistence:
                current = self.registry.get(job_id)
                if current: self.persistence.upsert_job(current)
            self._log(job_id, "ERROR", error.message)
            self.events.publish(JobEvent(type=JobEventType.FAILED, job_id=job_id, payload={"progress": progress, "status": JobStatus.FAILED, "code": error.code, "message": error.message, "currentStep": step}))
            self._investigation_log(job_id, "job_failed", error_code="INTERNAL_ERROR", elapsed_ms=round((time.monotonic() - started) * 1000))
            logger.exception("job_id=%s stage=FAILED error_code=INTERNAL_ERROR", job_id)

    def final_video(self, job_id: str) -> Path:
        record = self.registry.get(job_id)
        if record and record.metadata:
            persisted = self.persistence.get_job(job_id) if self.persistence else None
            if persisted and persisted.get("final_path"): return Path(persisted["final_path"])
        persisted = self.persistence.get_job(job_id) if self.persistence else None
        if persisted and persisted.get("final_path"):
            path = Path(persisted["final_path"]).resolve()
            root = self.settings.app.workspace.resolve()
            if root in path.parents and path.is_file(): return path
        return self.settings.app.workspace / job_id / "output" / "final.mp4"

    def restore(self, job_id: str) -> JobRecord | None:
        current = self.registry.get(job_id)
        if current: return current
        if not self.persistence: return None
        row = self.persistence.get_job(job_id)
        if not row: return None
        status = row["status"]
        if status in {JobStatus.RECEIVED, JobStatus.VALIDATING, JobStatus.GENERATING_AUDIO, JobStatus.RENDERING_SCENES, JobStatus.COMPOSING}:
            status = JobStatus.FAILED
            row["error"] = {"code":"JOB_INTERRUPTED","message":"งานหยุดลงเมื่อ server restart กรุณาสั่งสร้างใหม่"}
        record = JobRecord(job_id=job_id,status=status,progress=row["progress"],current_step="Job interrupted" if status==JobStatus.FAILED and row.get("interrupted") else ("Video is ready" if status==JobStatus.COMPLETED else "Job restored"),error=row.get("error"),metadata=row.get("metadata"),project_id=row.get("project_id"),render_engine=row.get("render_engine") or "ffmpeg_motion")
        self.registry.set(record)
        return record
