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
from app.services.video_service import SceneRenderer, SubtitleRenderer, VideoComposer
from app.services.persistence import Persistence

logger = logging.getLogger("autoclip.jobs")


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

    def submit(self, uploaded_file, tts_provider: str | None = None, subtitle_mode: str | None = None, script_json: str | None = None) -> JobRecord:
        selected_provider = (tts_provider or self.settings.tts.provider or "local").strip().lower()
        # Keep UI/config aliases backwards compatible while exposing one
        # canonical provider name to the rendering pipeline.
        selected_provider = {
            "vachana": "local",
            "vachana-tts": "local",
            "f5": "thonburian",
            "bird/f5-tts-thai": "bird-f5",
        }.get(selected_provider, selected_provider)
        if selected_provider not in {"dummy", "local", "thonburian", "bird", "bird-f5", "f5-thai", "f5-tts-thai", "khanomtan", "khanom-tan", "khanomtan-tts"}:
            raise AppError("TTS_GENERATION_FAILED", "Selected TTS model is unavailable")
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
        record = self.registry.set(JobRecord(job_id=job_id, status=JobStatus.RECEIVED, progress=0, current_step="Upload received", tts_provider=selected_provider, subtitle_mode=subtitle_mode))
        if self.persistence: self.persistence.upsert_job(record)
        self._log(job_id, "INFO", "Package uploaded")
        self._progress(job_id, JobStatus.RECEIVED, 2, "Package uploaded")
        self.executor.submit(self._process, job_id, workspace)
        return record

    def submit_path(self, package_path: Path, tts_provider: str | None = None, subtitle_mode: str | None = None, script_json: str | None = None) -> JobRecord:
        """Submit a server-created package through the same render pipeline."""
        if not package_path.is_file():
            raise AppError("PACKAGE_INVALID", "Generated package is unavailable")
        class _File:
            def __init__(self, path: Path): self.file = path.open("rb")
        source = _File(package_path)
        try:
            return self.submit(source, tts_provider, subtitle_mode, script_json)
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

    def _process(self, job_id: str, workspace: Workspace) -> None:
        started = time.monotonic()
        try:
            self._progress(job_id, JobStatus.VALIDATING, 5, "Validating ZIP package")
            self._log(job_id, "INFO", "Validating ZIP package")
            package = PackageService(self.settings.app.max_extracted_mb * 1024 * 1024)
            script, bgm = package.extract_and_validate(workspace.source / "input.zip", workspace.extracted)
            self.registry.set_project(job_id, script.project.id)
            if self.persistence:
                self.persistence.ensure_project(script.project.id, script.project.title, len(script.scenes), "RENDERING")
                current = self.registry.get(job_id)
                if current: self.persistence.upsert_job(current)
            self._log(job_id, "INFO", "script.json validated")
            self._log(job_id, "INFO", f"{len(script.scenes)} scenes detected")
            selected_provider = self.registry.get(job_id).tts_provider or self.settings.tts.provider
            provider = create_tts_provider(selected_provider, self.settings)
            count = len(script.scenes)
            durations: list[float] = []
            self._progress(job_id, JobStatus.GENERATING_AUDIO, 15, f"Generating narration 1 of {count}")
            for index, scene in enumerate(script.scenes):
                start_progress = 15 + round(25 * index / count)
                self._progress(job_id, JobStatus.GENERATING_AUDIO, start_progress, f"Generating narration {index + 1} of {count} (in progress)")
                self._log(job_id, "INFO", f"Generating narration {index + 1} of {count} (in progress)")
                output = workspace.generated_audio / f"{scene.id}.wav"
                try:
                    provider.synthesize(scene.narration, script.project.language, script.voice.voice, script.voice.speed, output)
                except AppError:
                    raise
                except Exception as exc:
                    raise AppError("TTS_GENERATION_FAILED", "Narration audio generation failed", {"sceneId": scene.id}) from exc
                durations.append(self.ffprobe.duration(output) + self.settings.video.scene_padding_seconds)
                self._log(job_id, "SUCCESS", f"Narration generated {index + 1} of {count}")
                self._progress(job_id, JobStatus.GENERATING_AUDIO, 15 + round(25 * (index + 1) / count), f"Generated narration {index + 1} of {count}")
            subtitle_renderer = SubtitleRenderer()
            scene_renderer = SceneRenderer(self.ffmpeg, self.settings)
            rendered: list[Path] = []
            job_record = self.registry.get(job_id)
            sub_mode = (job_record.subtitle_mode if job_record else None) or "auto"
            for index, (scene, duration) in enumerate(zip(script.scenes, durations)):
                render_progress = 40 + round(35 * index / count)
                self._progress(job_id, JobStatus.RENDERING_SCENES, render_progress, f"Rendering scene {index + 1} of {count} (in progress)")
                self._log(job_id, "INFO", f"Motion: {scene.motion} · Transition: {scene.transition or self.settings.video.transition}")
                if sub_mode == "disable":
                    show_sub = False
                elif sub_mode == "enable":
                    show_sub = True
                else:
                    show_sub = scene.show_subtitle and bool(scene.subtitle)

                if show_sub and (scene.subtitle or scene.narration):
                    self._log(job_id, "INFO", f"Adding Thai subtitles to scene {index + 1}")
                    subtitle = subtitle_renderer.write(scene.subtitle or scene.narration, duration, workspace.subtitles / f"{scene.id}.srt")
                else:
                    self._log(job_id, "INFO", f"Skipping subtitles for scene {index + 1} ({'disabled by global setting' if sub_mode == 'disable' else 'disabled in scene'})")
                    subtitle = None
                rendered.append(scene_renderer.render(scene, workspace.extracted / scene.image, workspace.generated_audio / f"{scene.id}.wav", subtitle, duration, workspace.rendered_scenes / f"{scene.id}.mp4"))
                self._log(job_id, "SUCCESS", f"Scene rendered {index + 1} of {count}")
                self._progress(job_id, JobStatus.RENDERING_SCENES, 40 + round(35 * (index + 1) / count), f"Rendered scene {index + 1} of {count}")
            self._progress(job_id, JobStatus.COMPOSING, 80, "Combining scenes")
            self._log(job_id, "INFO", "Combining scenes")
            if bgm:
                self._log(job_id, "INFO", "Mixing background music")
            self._log(job_id, "INFO", "Normalizing audio")
            self._progress(job_id, JobStatus.COMPOSING, 92, "Creating final video")
            self._log(job_id, "INFO", "Creating final video")
            transitions = [scene.transition or self.settings.video.transition for scene in script.scenes[:-1]]
            final = VideoComposer(self.ffmpeg, self.settings).compose(rendered, workspace.output, bgm, durations, transitions)
            probe = self.ffprobe.probe(final)
            video_stream = next(stream for stream in probe["streams"] if stream.get("codec_type") == "video")
            metadata = {
                "projectTitle": script.project.title,
                "durationSeconds": round(float(probe["format"]["duration"]), 3),
                "resolution": f"{video_stream['width']}x{video_stream['height']}",
                "sceneCount": count,
                "fileSizeBytes": final.stat().st_size,
                "createdAt": local_now().isoformat(),
            }
            self.registry.set_metadata(job_id, metadata)
            if self.persistence:
                current = self.registry.get(job_id)
                if current: self.persistence.upsert_job(current, final, metadata)
                if current and current.project_id: self.persistence.update_project_status(current.project_id, "COMPLETED")
            self._progress(job_id, JobStatus.COMPLETED, 100, "Video is ready")
            self._log(job_id, "SUCCESS", "Video generation completed")
            self.events.publish(JobEvent(type=JobEventType.COMPLETED, job_id=job_id, payload={"progress": 100, "status": JobStatus.COMPLETED, "previewUrl": f"/jobs/{job_id}/preview", "videoUrl": f"/api/jobs/{job_id}/video"}))
            logger.info("job_id=%s stage=COMPLETED elapsed_seconds=%.3f", job_id, time.monotonic() - started)
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
            logger.exception("job_id=%s stage=FAILED error_code=%s elapsed_seconds=%.3f", job_id, exc.code, time.monotonic() - started)
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
        record = JobRecord(job_id=job_id,status=status,progress=row["progress"],current_step="Job interrupted" if status==JobStatus.FAILED and row.get("interrupted") else ("Video is ready" if status==JobStatus.COMPLETED else "Job restored"),error=row.get("error"),metadata=row.get("metadata"),project_id=row.get("project_id"))
        self.registry.set(record)
        return record
