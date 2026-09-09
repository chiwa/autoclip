from __future__ import annotations

import json
import math
import zipfile
import logging
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from app.config.settings import Settings
from app.domain.enums import JobStatus
from app.domain.errors import AppError, public_error
from app.domain.events import JobEvent, JobEventPublisher, JobEventType, local_now
from app.domain.models import JobRecord
from app.infrastructure.ffmpeg import FfmpegRunner, FfprobeRunner, build_ffmpeg_metadata_args
from app.infrastructure.filesystem import Workspace, WorkspaceManager
from app.infrastructure.tts import create_tts_provider
from app.services.package_service import PackageService
from app.services.narration_audio_service import NarrationAudioProcessor
from app.services.pronunciation_service import PronunciationService
from app.services.bgm_service import ensure_default_bgm, resolve_podcast_bgm
from app.services.video_service import RenderProfile, SceneRenderer, SubtitleRenderer, VideoComposer
from app.services.persistence import Persistence
from app.services.wan_service import ComfyWanClient, RunpodComfyLogTailer
from app.services.ltx_service import RunpodLtxClient, RunpodLtxLogTailer, ltx_frames_for_duration
from app.services.musetalk_service import RunpodMuseTalkClient, RunpodMuseTalkLogTailer
from app.services.podcast_chunker import PodcastChunker
from app.services.podcast_audio_service import PodcastAudioService
from app.services.podcast_subtitle_service import PodcastSubtitleService
from app.services.podcast_video_renderer import PodcastVideoRenderer

logger = logging.getLogger("autoclip.jobs")
SUPPORTED_RENDER_ENGINES = {"ffmpeg_motion", "wan2.2", "ltx"}
SUPPORTED_OUTPUT_FORMATS = {
    "use_json",
    "vertical", "vertical_1080p", "vertical_2k", "vertical_4k",
    "youtube", "youtube_1080p", "youtube_2k", "youtube_4k",
}
OUTPUT_RESOLUTIONS = {
    "vertical": "1080x1920",
    "vertical_1080p": "1080x1920",
    "vertical_2k": "1440x2560",
    "vertical_4k": "2160x3840",
    "youtube": "1920x1080",
    "youtube_1080p": "1920x1080",
    "youtube_2k": "2560x1440",
    "youtube_4k": "3840x2160",
}
WAN_FPS = 16.0
WAN_FRAME_STEP = 4
WAN_MAX_FRAMES = 161


def wan_frames_for_duration(duration_seconds: float, requested_frames: int | None = None) -> int:
    """Return a Wan-compatible 4k+1 frame count that covers narration.

    A package may request a longer shot, but it must never reduce the length
    needed by narration: doing so forces FFmpeg to loop the Wan output later.
    """
    required = max(1, int(math.ceil((duration_seconds * WAN_FPS - 1) / WAN_FRAME_STEP)))
    requested = max(0, int(requested_frames or 0))
    frames = WAN_FRAME_STEP * max(required, int(math.ceil(max(0, requested - 1) / WAN_FRAME_STEP))) + 1
    return min(frames, WAN_MAX_FRAMES)


def scene_render_engine(selected_engine: str, scene) -> str:
    """Resolve the actual renderer without adding a new ZIP field.

    FFmpeg mode is an explicit all-scenes override. LTX/Wan mode is hybrid: the
    optional ``ltx`` or ``wan`` object opts that scene into AI motion, while scenes
    without it keep their existing FFmpeg motion plan.
    """
    has_ai_motion = getattr(scene, "ltx", None) is not None or getattr(scene, "wan", None) is not None
    if selected_engine in {"wan2.2", "ltx"} and has_ai_motion:
        return selected_engine
    return "ffmpeg_motion"


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
        self.narration_audio = NarrationAudioProcessor(self.ffmpeg, self.ffprobe, settings)
        self.persistence = persistence
        self.pronunciation = PronunciationService()

    def submit(self, uploaded_file, tts_provider: str | None = None, subtitle_mode: str | None = None, script_json: str | None = None, render_engine: str | None = None, output_format: str | None = None, motion_resolution: str | None = None) -> JobRecord:
        selected_provider = (tts_provider or self.settings.tts.provider or "google-gemini").strip().lower()
        # Keep UI/config aliases backwards compatible while exposing one
        # canonical provider name to the rendering pipeline.
        selected_provider = {
            "vachana": "local",
            "vachana-tts": "local",
            "f5": "thonburian",
            "bird/f5-tts-thai": "bird-f5",
            "google": "google-gemini",
            "gemini": "google-gemini",
        }.get(selected_provider, selected_provider)
        if selected_provider not in {"dummy", "local", "google-gemini", "runpod-f5", "runpod-f5-thai", "kokoro", "kokoro-thai", "wayu-kokoro-thai", "thonburian", "bird", "bird-f5", "f5-thai", "f5-tts-thai", "khanomtan", "khanom-tan", "khanomtan-tts"}:
            raise AppError("TTS_GENERATION_FAILED", "Selected TTS model is unavailable")
        selected_engine = (render_engine or "ffmpeg_motion").strip().lower()
        if selected_engine not in SUPPORTED_RENDER_ENGINES:
            raise AppError("RENDER_ENGINE_INVALID", "Selected render engine is unavailable")
        selected_output_format = (output_format or "use_json").strip().lower()
        if selected_output_format not in SUPPORTED_OUTPUT_FORMATS:
            raise AppError("OUTPUT_FORMAT_INVALID", "Selected output format is unavailable")
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
        if script_json or selected_output_format != "use_json" or motion_resolution:
            try:
                from app.domain.models import Script
                with zipfile.ZipFile(input_path) as source:
                    raw_script = json.loads(script_json) if script_json else json.loads(source.read("script.json"))
                    script = Script.model_validate(raw_script)
                    if resolution := OUTPUT_RESOLUTIONS.get(selected_output_format):
                        script = script.model_copy(update={"project": script.project.model_copy(update={"resolution": resolution})})
                    if selected_engine == "ffmpeg_motion" and motion_resolution:
                        tier = motion_resolution.strip().lower()
                        if tier in {"2k", "4k"}:
                            orig_w, orig_h = (int(p) for p in script.project.resolution.split("x", 1))
                            if orig_w > orig_h:
                                target_res = "2560x1440" if tier == "2k" else "3840x2160"
                            else:
                                target_res = "1440x2560" if tier == "2k" else "2160x3840"
                            script = script.model_copy(update={"project": script.project.model_copy(update={"resolution": target_res})})
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
        record = self.registry.set(JobRecord(job_id=job_id, status=JobStatus.RECEIVED, progress=0, current_step="Upload received", tts_provider=selected_provider, subtitle_mode=subtitle_mode, render_engine=selected_engine, output_format=selected_output_format))
        if self.persistence: self.persistence.upsert_job(record)
        self._investigation_log(job_id, "job_received", render_engine=selected_engine, output_format=selected_output_format, tts_provider=selected_provider, upload_bytes=size)
        self._log(job_id, "INFO", "Package uploaded")
        self._log(job_id, "INFO", f"Render engine selected: {selected_engine}")
        if selected_engine == "ffmpeg_motion" and motion_resolution and motion_resolution.strip().lower() in {"2k", "4k"}:
            self._log(job_id, "INFO", f"Resolution: {motion_resolution.strip().upper()} ({script.project.resolution})")
        self._log(job_id, "INFO", f"Output format selected: {selected_output_format}")
        self._progress(job_id, JobStatus.RECEIVED, 2, "Package uploaded")
        self.executor.submit(self._process, job_id, workspace)
        return record

    def submit_path(self, package_path: Path, tts_provider: str | None = None, subtitle_mode: str | None = None, script_json: str | None = None, render_engine: str | None = None, output_format: str | None = None, motion_resolution: str | None = None) -> JobRecord:
        """Submit a server-created package through the same render pipeline."""
        if not package_path.is_file():
            raise AppError("PACKAGE_INVALID", "Generated package is unavailable")
        class _File:
            def __init__(self, path: Path): self.file = path.open("rb")
        source = _File(package_path)
        try:
            return self.submit(source, tts_provider, subtitle_mode, script_json, render_engine, output_format)
        finally:
            source.file.close()

    def submit_podcast(
        self,
        image_file: Any,
        title: str,
        script_text: str,
        english_script: str = "",
        voice: str | None = None,
        speed: float | None = None,
        style_prompt: str | None = None,
        english_style_prompt: str | None = None,
        enable_subtitles: bool = True,
        description: str | None = None,
        hashtags: str | None = None,
        bgm_file: Any | None = None,
        bgm_track: str = "space.mp3",
        bgm_volume: float | None = None,
        focus: str = "center",
    ) -> JobRecord:
        if not script_text or not script_text.strip():
            raise AppError("PODCAST_SCRIPT_EMPTY", "กรุณาใส่บทพูดสำหรับ Podcast")

        cleaned_title = title.strip() or "YouTube Podcast"
        job_id = str(uuid.uuid4())
        workspace = self.workspaces.create(job_id)

        import shutil
        # Save cover image
        if isinstance(image_file, Path):
            cover_ext = image_file.suffix.lower()
            cover_dest = workspace.source / f"cover{cover_ext}"
            shutil.copy(image_file, cover_dest)
        elif hasattr(image_file, "file") and getattr(image_file, "filename", None):
            cover_ext = Path(image_file.filename).suffix.lower()
            cover_dest = workspace.source / f"cover{cover_ext}"
            with cover_dest.open("wb") as out:
                shutil.copyfileobj(image_file.file, out)
        else:
            raise AppError("PODCAST_IMAGE_INVALID", "ไฟล์ภาพปกไม่ถูกต้อง")

        if cover_dest.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise AppError("PODCAST_IMAGE_INVALID", "ไฟล์ภาพปกต้องเป็น PNG, JPG, JPEG หรือ WebP")

        # Save script text for durability and retries
        (workspace.source / "script.txt").write_text(script_text, encoding="utf-8")
        cleaned_english_script = (english_script or "").strip()
        if cleaned_english_script:
            (workspace.source / "script-en.txt").write_text(cleaned_english_script, encoding="utf-8")

        # Save BGM file if provided
        saved_bgm: Path | None = None
        if bgm_file:
            if isinstance(bgm_file, Path):
                if bgm_file.is_file():
                    saved_bgm = workspace.source / f"bgm{bgm_file.suffix.lower()}"
                    shutil.copy(bgm_file, saved_bgm)
            elif hasattr(bgm_file, "file") and getattr(bgm_file, "filename", None):
                bgm_ext = Path(bgm_file.filename).suffix.lower()
                if bgm_ext in {".mp3", ".wav", ".m4a", ".aac", ".ogg"}:
                    saved_bgm = workspace.source / f"bgm{bgm_ext}"
                    with saved_bgm.open("wb") as out:
                        shutil.copyfileobj(bgm_file.file, out)

        selected_voice = voice or self.settings.podcast.default_voice
        selected_speed = float(speed if speed is not None else self.settings.podcast.default_speed)
        selected_style = self.settings.podcast.resolve_style_prompt(selected_voice, style_prompt)
        selected_english_style = (
            english_style_prompt.strip()
            if english_style_prompt and english_style_prompt.strip()
            else self.settings.podcast.default_english_style_prompt
        )
        selected_bgm_vol = float(bgm_volume if bgm_volume is not None else self.settings.podcast.default_bgm_volume)
        selected_focus = focus if focus in {"center", "top", "bottom", "left", "right"} else "center"
        (workspace.source / "podcast-settings.json").write_text(
            json.dumps(
                {
                    "voice": selected_voice,
                    "speed": selected_speed,
                    "thaiStylePrompt": selected_style,
                    "englishStylePrompt": selected_english_style,
                    "bgmTrack": bgm_track,
                    "bgmVolume": selected_bgm_vol,
                    "customBgmFile": saved_bgm.name if saved_bgm else None,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        project_id = f"podcast-{uuid.uuid4().hex[:8]}"
        record = self.registry.set(
            JobRecord(
                job_id=job_id,
                project_id=project_id,
                status=JobStatus.RECEIVED,
                progress=0,
                current_step="เตรียมบท Podcast",
                tts_provider="google-gemini",
                subtitle_mode="enable" if enable_subtitles else "disable",
                render_engine="ffmpeg_motion",
                output_format="youtube",
            )
        )
        if self.persistence:
            self.persistence.ensure_project(project_id, cleaned_title, 1, "RENDERING")
            self.persistence.upsert_job(record)

        self._investigation_log(job_id, "podcast_job_received", title=cleaned_title, voice=selected_voice, speed=selected_speed)
        self._log(job_id, "INFO", f"Podcast '{cleaned_title}' uploaded")
        self._progress(job_id, JobStatus.RECEIVED, 2, "เตรียมบท Podcast")

        self.executor.submit(
            self._process_podcast,
            job_id,
            project_id,
            cleaned_title,
            script_text,
            cleaned_english_script,
            cover_dest,
            workspace,
            selected_voice,
            selected_speed,
            selected_style,
            selected_english_style,
            enable_subtitles,
            description,
            hashtags,
            saved_bgm,
            bgm_track,
            selected_bgm_vol,
            selected_focus,
        )
        return record

    def _progress(self, job_id: str, status: JobStatus, progress: int, step: str) -> None:
        self.registry.update(job_id, status, progress, step)
        if self.persistence:
            current = self.registry.get(job_id)
            if current: self.persistence.upsert_job(current)
        self.events.publish(JobEvent(type=JobEventType.PROGRESS, job_id=job_id, payload={"progress": progress, "status": status, "currentStep": step}))

    def set_metadata(self, job_id: str, metadata: dict) -> None:
        self.registry.set_metadata(job_id, metadata)

    def _log(self, job_id: str, level: str, message: str, technical: bool = False) -> None:
        entry = self.registry.add_log(job_id, level, message)
        if technical:
            entry["technical"] = True
        self.events.publish(JobEvent(type=JobEventType.LOG, job_id=job_id, payload=entry))

    def _investigation_log(self, job_id: str, event: str, **fields: object) -> None:
        """Emit compact, grep-friendly diagnostics without leaking secrets."""
        safe = " ".join(f"{key}={value}" for key, value in fields.items() if value is not None)
        logger.info("event=%s job_id=%s %s", event, job_id, safe)

    def _technical_log(self, job_id: str, message: str) -> None:
        """Send remote diagnostics to the collapsed technical-log UI only."""
        self._log(job_id, "TECHNICAL", message, technical=True)

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
            render_profile = RenderProfile.from_project(self.settings, script.project.resolution, script.project.fps)
            self._investigation_log(job_id, "render_profile_resolved", width=render_profile.width, height=render_profile.height, fps=render_profile.fps)
            self._log(job_id, "INFO", f"Output resolution: {render_profile.width}x{render_profile.height}")
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
            ltx_client: RunpodLtxClient | None = None
            wan_client: ComfyWanClient | None = None
            ai_scene_count = sum(scene_render_engine(render_engine, scene) in {"wan2.2", "ltx"} for scene in script.scenes)
            ffmpeg_scene_count = len(script.scenes) - ai_scene_count
            self._investigation_log(
                job_id,
                "render_plan_resolved",
                selected_engine=render_engine,
                ai_scenes=ai_scene_count,
                ffmpeg_scenes=ffmpeg_scene_count,
            )
            use_ltx = render_engine == "ltx" or (render_engine == "wan2.2" and (getattr(self.settings.ltx, "enabled", True) or bool(getattr(self.settings.ltx, "ssh_host", ""))))
            if render_engine in {"wan2.2", "ltx"} and ai_scene_count:
                if use_ltx:
                    self._progress(job_id, JobStatus.VALIDATING, 10, "Checking LTX Video connection")
                    self._investigation_log(job_id, "ltx_connection_check", configured=self.settings.ltx.enabled, host_configured=bool(self.settings.ltx.runpod_host))
                    ltx_client = RunpodLtxClient(self.settings)
                    ltx_client.check_connection()
                    self._log(job_id, "SUCCESS", f"Hybrid plan: {ai_scene_count} LTX scenes · {ffmpeg_scene_count} FFmpeg scenes")
                else:
                    self._progress(job_id, JobStatus.VALIDATING, 10, "Checking Wan 2.2 connection")
                    self._investigation_log(job_id, "wan_connection_check", configured=self.settings.wan.enabled, comfy_url_configured=bool(self.settings.wan.comfy_url))
                    wan_client = ComfyWanClient(self.settings)
                    wan_client.check_connection()
                    self._log(job_id, "SUCCESS", f"Hybrid plan: {ai_scene_count} Wan scenes · {ffmpeg_scene_count} FFmpeg scenes")
            elif render_engine in {"wan2.2", "ltx"}:
                self._log(job_id, "INFO", "No AI-enabled scenes in ZIP; rendering every scene with FFmpeg Motion")
            else:
                self._log(job_id, "INFO", f"FFmpeg Motion override: rendering all {len(script.scenes)} scenes with FFmpeg")

            musetalk_client: RunpodMuseTalkClient | None = None
            lip_sync_scene_count = sum(bool(getattr(scene, "lip_sync", False) or (scene.ltx and scene.ltx.lip_sync) or (scene.wan and scene.wan.lip_sync)) for scene in script.scenes)
            if lip_sync_scene_count and getattr(self.settings.musetalk, "enabled", True):
                self._progress(job_id, JobStatus.VALIDATING, 12, "Checking MuseTalk Lip-sync connection")
                try:
                    musetalk_client = RunpodMuseTalkClient(self.settings)
                    musetalk_client.check_connection()
                    self._log(job_id, "SUCCESS", f"Lip-sync enabled for {lip_sync_scene_count} scenes (MuseTalk on RunPod)")
                except Exception as exc:
                    self._log(job_id, "WARNING", f"MuseTalk Lip-sync unavailable ({exc}); continuing without lip-sync")
                    musetalk_client = None

            selected_provider = self.registry.get(job_id).tts_provider or self.settings.tts.provider
            provider = create_tts_provider(selected_provider, self.settings)
            if getattr(script.voice, "style_prompt", None) and hasattr(provider, "style_prompt"):
                provider.style_prompt = script.voice.style_prompt
            count = len(script.scenes)
            parallelism = min(count, self.settings.tts.google_parallelism) if selected_provider == "google-gemini" else 1
            self._progress(job_id, JobStatus.GENERATING_AUDIO, 15, f"Generating narration 0 of {count}")
            trim = self.settings.tts.silence_trim
            self._investigation_log(
                job_id,
                "tts_silence_trim_config",
                enabled=trim.enabled,
                threshold_db=trim.threshold_db,
                minimum_silence_seconds=trim.minimum_silence_seconds,
                retained_edge_seconds=trim.retained_edge_seconds,
            )
            if parallelism > 1:
                self._log(job_id, "INFO", f"Generating Google Gemini narration in parallel ({parallelism} workers)")
                self._investigation_log(job_id, "tts_parallelism", provider=selected_provider, workers=parallelism, scene_count=count)

            def synthesize_scene(index: int, scene) -> tuple[int, float]:
                output = workspace.generated_audio / f"{scene.id}.wav"
                try:
                    if output.is_file() and output.stat().st_size > 1000:
                        self._log(job_id, "INFO", f"Reusing existing narration for scene {index + 1}")
                        audio_duration = self.narration_audio.process(output)
                        return index, audio_duration
                    provider.synthesize(self.pronunciation.resolve_scene(scene), script.project.language, script.voice.voice, script.voice.speed, output)
                    audio_duration = self.narration_audio.process(output)
                    return index, audio_duration
                except AppError:
                    raise
                except Exception as exc:
                    raise AppError("TTS_GENERATION_FAILED", "Narration audio generation failed", {"sceneId": scene.id}) from exc

            raw_audio_durations_by_index: dict[int, float] = {}
            with ThreadPoolExecutor(max_workers=parallelism, thread_name_prefix="autoclip-tts") as audio_executor:
                futures = {}
                for index, scene in enumerate(script.scenes):
                    self._log(job_id, "INFO", f"Generating narration {index + 1} of {count} (queued)")
                    self._investigation_log(job_id, "tts_started", render_engine=render_engine, scene_id=scene.id, scene_index=index + 1, scene_count=count, provider=selected_provider)
                    futures[audio_executor.submit(synthesize_scene, index, scene)] = (index, scene)
                for completed, future in enumerate(as_completed(futures), start=1):
                    index, scene = futures[future]
                    _, raw_audio_duration = future.result()
                    raw_audio_durations_by_index[index] = raw_audio_duration
                    self._investigation_log(job_id, "tts_completed", render_engine=render_engine, scene_id=scene.id, audio_seconds=round(raw_audio_duration, 3))
                    self._log(job_id, "SUCCESS", f"Narration generated {index + 1} of {count}")
                    self._progress(job_id, JobStatus.GENERATING_AUDIO, 15 + round(25 * completed / count), f"Generated narration {completed} of {count}")
            raw_audio_durations = [raw_audio_durations_by_index[index] for index in range(count)]
            subtitle_renderer = SubtitleRenderer()
            scene_renderer = SceneRenderer(self.ffmpeg, self.settings, render_profile)
            rendered: list[Path] = []
            job_record = self.registry.get(job_id)
            sub_mode = (job_record.subtitle_mode if job_record else None) or "auto"
            transitions = [scene.transition or self.settings.video.transition for scene in script.scenes[:-1]]
            transition_seconds = 0.0
            if count > 1 and self.settings.video.transition_seconds > 0:
                transition_seconds = min(self.settings.video.transition_seconds, min(raw_audio_durations) / 2)
            durations = [
                raw_audio_durations[index] + self.settings.video.scene_padding_seconds + (
                    transition_seconds if index < count - 1 and transitions[index] != "none" else 0.0
                )
                for index in range(count)
            ]
            if render_engine == "ffmpeg_motion" or ai_scene_count == 0:
                rendered = self._render_ffmpeg_scenes(job_id, script, durations, raw_audio_durations, workspace, render_profile, sub_mode, transitions, transition_seconds)
            for index, (scene, duration) in enumerate(zip(script.scenes, durations) if ai_scene_count else ()):
                actual_engine = scene_render_engine(render_engine, scene)
                render_progress = 40 + round(35 * index / count)
                self._progress(job_id, JobStatus.RENDERING_SCENES, render_progress, f"Rendering scene {index + 1} of {count} (in progress)")
                scene_started = time.monotonic()
                self._investigation_log(job_id, "scene_render_started", render_engine=actual_engine, selected_engine=render_engine, scene_id=scene.id, scene_index=index + 1, motion=scene.motion, transition=scene.transition or self.settings.video.transition, duration_seconds=round(duration, 3))
                self._log(job_id, "INFO", f"Scene renderer: {actual_engine} · Motion: {scene.motion} · Transition: {scene.transition or self.settings.video.transition}")

                final_scene_output = workspace.rendered_scenes / f"{scene.id}.mp4"
                if final_scene_output.is_file() and final_scene_output.stat().st_size > 1000:
                    self._log(job_id, "INFO", f"Reusing already rendered video for scene {index + 1}")
                    rendered.append(final_scene_output)
                    self._investigation_log(job_id, "scene_render_reused", scene_id=scene.id, output=final_scene_output.name)
                    self._progress(job_id, JobStatus.RENDERING_SCENES, 40 + round(35 * (index + 1) / count), f"Rendered scene {index + 1} of {count}")
                    continue

                if sub_mode == "disable":
                    show_sub = False
                elif sub_mode == "enable":
                    show_sub = True
                else:
                    show_sub = scene.show_subtitle and bool(scene.subtitle)

                if show_sub and (scene.subtitle or scene.narration):
                    leaving_transition = transition_seconds if index < count - 1 and transitions[index] != "none" else 0.0
                    subtitle_start = 0.0
                    subtitle_end = min(duration - leaving_transition, raw_audio_durations[index] + 0.15)
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
                is_lip_sync = bool(getattr(scene, "lip_sync", False) or (scene.ltx and scene.ltx.lip_sync) or (scene.wan and scene.wan.lip_sync))
                if actual_engine in {"wan2.2", "ltx"} and ltx_client is not None:
                    ai_opts = scene.ltx or scene.wan
                    assert ai_opts is not None
                    ltx_output = workspace.rendered_scenes / f"{scene.id}.ltx.mp4"
                    if not (ltx_output.is_file() and ltx_output.stat().st_size > 1000):
                        self._progress(job_id, JobStatus.RENDERING_SCENES, render_progress, f"Rendering LTX scene {index + 1} of {count} (in progress)")
                        self._log(job_id, "INFO", f"Submitting scene {index + 1} to LTX Video")
                        is_landscape = render_profile.width > render_profile.height
                        ltx_width = self.settings.ltx.height if is_landscape else self.settings.ltx.width
                        ltx_height = self.settings.ltx.width if is_landscape else self.settings.ltx.height
                        dynamic_frames = ltx_frames_for_duration(duration, ai_opts.frames, fps=self.settings.ltx.fps)
                        poc_root = str(getattr(self.settings.ltx, "poc_root", "/workspace/ltx-video-poc"))
                        tailer = RunpodLtxLogTailer(
                            self.settings,
                            lambda message: self._technical_log(job_id, f"RunPod | {message}"),
                            log_file=f"{poc_root}/logs/autoclip-{job_id[:8]}-{scene.id}-inference.log",
                        )
                        tailer.start()
                        try:
                            ltx_client.render_scene(job_id, scene, workspace.extracted / scene.image, ltx_output, width=ltx_width, height=ltx_height, frames=dynamic_frames)
                        finally:
                            tailer.stop()
                        self._log(job_id, "INFO", f"LTX scene {index + 1} received")
                    else:
                        self._log(job_id, "INFO", f"Reusing existing raw LTX video for scene {index + 1}")

                    raw_scene_video = ltx_output
                    if is_lip_sync and musetalk_client is not None:
                        lipsync_output = workspace.rendered_scenes / f"{scene.id}.lipsync.mp4"
                        if not (lipsync_output.is_file() and lipsync_output.stat().st_size > 1000):
                            self._log(job_id, "INFO", f"Submitting scene {index + 1} to MuseTalk for Lip-sync")
                            # Scale LTX raw video to final resolution before MuseTalk so lip-sync
                            # runs at full output quality instead of the small LTX native resolution
                            # (e.g. 448x768 → 1080x1920). Without this, the face region gets
                            # upscaled 2.4x after MuseTalk and looks blurry.
                            ltx_scaled = workspace.rendered_scenes / f"{scene.id}.ltx_scaled.mp4"
                            if not (ltx_scaled.is_file() and ltx_scaled.stat().st_size > 1000):
                                self._log(job_id, "INFO", f"Upscaling LTX scene {index + 1} to {render_profile.width}x{render_profile.height} for MuseTalk")
                                vf_scale = (
                                    f"scale={render_profile.width}:{render_profile.height}:"
                                    f"force_original_aspect_ratio=increase:flags=lanczos,"
                                    f"crop={render_profile.width}:{render_profile.height},setsar=1,"
                                    f"format=yuv420p"
                                )
                                self.ffmpeg.run(
                                    ["-i", str(ltx_output),
                                     "-vf", vf_scale,
                                     "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                                     "-pix_fmt", "yuv420p", str(ltx_scaled)],
                                    "LTX_PRESCALE_FAILED",
                                )
                            musetalk_root = str(getattr(self.settings.musetalk, "musetalk_root", "/workspace/musetalk"))
                            tailer = RunpodMuseTalkLogTailer(
                                self.settings,
                                lambda message: self._technical_log(job_id, f"MuseTalk | {message}"),
                                log_file=f"{musetalk_root}/logs/autoclip-{job_id[:8]}-{scene.id}-inference.log",
                            )
                            tailer.start()
                            try:
                                musetalk_client.sync_lips(
                                    job_id,
                                    scene,
                                    input_media=ltx_scaled,
                                    audio=workspace.generated_audio / f"{scene.id}.wav",
                                    output=lipsync_output,
                                    bbox_shift=getattr(self.settings.musetalk, "bbox_shift", 0),
                                )
                            finally:
                                tailer.stop()
                            self._log(job_id, "SUCCESS", f"MuseTalk lip-sync received for scene {index + 1}")
                        else:
                            self._log(job_id, "INFO", f"Reusing existing lip-synced video for scene {index + 1}")
                        raw_scene_video = lipsync_output

                    rendered.append(scene_renderer.render_wan_video(scene, raw_scene_video, workspace.generated_audio / f"{scene.id}.wav", subtitle, duration, final_scene_output))
                elif actual_engine == "wan2.2" and wan_client is not None:
                    assert scene.wan is not None
                    wan_output = workspace.rendered_scenes / f"{scene.id}.wan.mp4"
                    if not (wan_output.is_file() and wan_output.stat().st_size > 1000):
                        self._progress(job_id, JobStatus.RENDERING_SCENES, render_progress, f"Rendering Wan scene {index + 1} of {count} (in progress)")
                        self._log(job_id, "INFO", f"Submitting scene {index + 1} to Wan 2.2")
                        is_landscape = render_profile.width > render_profile.height
                        wan_width = self.settings.wan.height if is_landscape else self.settings.wan.width
                        wan_height = self.settings.wan.width if is_landscape else self.settings.wan.height
                        dynamic_frames = wan_frames_for_duration(duration, scene.wan.frames)
                        self._technical_log(job_id, "RunPod ComfyUI log stream started")
                        tailer = RunpodComfyLogTailer(self.settings, lambda message: self._technical_log(job_id, f"RunPod | {message}"))
                        tailer.start()
                        try:
                            wan_client.render_scene(job_id, scene, workspace.extracted / scene.image, wan_output, width=wan_width, height=wan_height, frames=dynamic_frames)
                        finally:
                            tailer.stop()
                        self._log(job_id, "INFO", f"Wan scene {index + 1} received; adding narration and subtitles")
                    else:
                        self._log(job_id, "INFO", f"Reusing existing raw Wan video for scene {index + 1}")
                    rendered.append(scene_renderer.render_wan_video(scene, wan_output, workspace.generated_audio / f"{scene.id}.wav", subtitle, duration, final_scene_output))
                elif is_lip_sync and musetalk_client is not None:
                    lipsync_output = workspace.rendered_scenes / f"{scene.id}.lipsync.mp4"
                    if not (lipsync_output.is_file() and lipsync_output.stat().st_size > 1000):
                        self._progress(job_id, JobStatus.RENDERING_SCENES, render_progress, f"Rendering MuseTalk Lip-sync scene {index + 1} of {count} (in progress)")
                        self._log(job_id, "INFO", f"Submitting portrait scene {index + 1} to MuseTalk for Lip-sync")
                        musetalk_root = str(getattr(self.settings.musetalk, "musetalk_root", "/workspace/musetalk"))
                        tailer = RunpodMuseTalkLogTailer(
                            self.settings,
                            lambda message: self._technical_log(job_id, f"MuseTalk | {message}"),
                            log_file=f"{musetalk_root}/logs/autoclip-{job_id[:8]}-{scene.id}-inference.log",
                        )
                        tailer.start()
                        try:
                            musetalk_client.sync_lips(
                                job_id,
                                scene,
                                input_media=workspace.extracted / scene.image,
                                audio=workspace.generated_audio / f"{scene.id}.wav",
                                output=lipsync_output,
                                bbox_shift=getattr(self.settings.musetalk, "bbox_shift", 0),
                            )
                        finally:
                            tailer.stop()
                        self._log(job_id, "SUCCESS", f"MuseTalk lip-sync received for scene {index + 1}")
                    else:
                        self._log(job_id, "INFO", f"Reusing existing lip-synced video for scene {index + 1}")
                    rendered.append(scene_renderer.render_wan_video(scene, lipsync_output, workspace.generated_audio / f"{scene.id}.wav", subtitle, duration, final_scene_output))
                else:
                    self._progress(job_id, JobStatus.RENDERING_SCENES, render_progress, f"Rendering FFmpeg scene {index + 1} of {count} (in progress)")
                    self._log(job_id, "INFO", f"Scene {index + 1} has no AI motion plan; using FFmpeg Motion")
                    rendered.append(scene_renderer.render(scene, workspace.extracted / scene.image, workspace.generated_audio / f"{scene.id}.wav", subtitle, duration, final_scene_output))
                self._investigation_log(job_id, "scene_render_completed", render_engine=actual_engine, selected_engine=render_engine, scene_id=scene.id, output=rendered[-1].name, elapsed_ms=round((time.monotonic() - scene_started) * 1000))
                self._log(job_id, "SUCCESS", f"Scene rendered {index + 1} of {count}")
                self._progress(job_id, JobStatus.RENDERING_SCENES, 40 + round(35 * (index + 1) / count), f"Rendered scene {index + 1} of {count}")
            self._progress(job_id, JobStatus.COMPOSING, 80, "Combining scenes")
            self._log(job_id, "INFO", "Combining scenes")
            if bgm:
                self._log(job_id, "INFO", "Mixing background music")
            self._log(job_id, "INFO", "Normalizing audio")
            self._progress(job_id, JobStatus.COMPOSING, 92, "Creating final video")
            self._log(job_id, "INFO", "Creating final video")
            final = VideoComposer(self.ffmpeg, self.settings, render_profile).compose(
                rendered,
                workspace.output,
                bgm,
                durations,
                transitions,
                title=video_metadata.get("title") if video_metadata.get("title") != "-" else script.project.title,
                description=video_metadata.get("description") if video_metadata.get("description") != "-" else "",
            )
            self._investigation_log(job_id, "compose_completed", render_engine=render_engine, final_path=final.name, elapsed_ms=round((time.monotonic() - started) * 1000))
            probe = self.ffprobe.probe(final)
            video_stream = next(stream for stream in probe["streams"] if stream.get("codec_type") == "video")
            metadata = {
                "projectTitle": script.project.title,
                "durationSeconds": round(float(probe["format"]["duration"]), 3),
                "resolution": f"{video_stream['width']}x{video_stream['height']}",
                "outputFormat": job.output_format if job else "use_json",
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

    def _process_podcast(
        self,
        job_id: str,
        project_id: str,
        title: str,
        script_text: str,
        english_script: str,
        cover_path: Path,
        workspace: Workspace,
        voice: str,
        speed: float,
        style_prompt: str,
        english_style_prompt: str,
        enable_subtitles: bool,
        description: str = "",
        hashtags: str = "",
        bgm_path: Path | None = None,
        bgm_track: str = "cosmic_drift",
        bgm_volume: float = 0.08,
        focus: str = "center",
    ) -> None:
        started = time.monotonic()
        english_executor: ThreadPoolExecutor | None = None
        try:
            self._investigation_log(job_id, "podcast_job_started", title=title, voice=voice, speed=speed)
            self._progress(job_id, JobStatus.VALIDATING, 5, "เตรียมบท Podcast")
            self._log(job_id, "INFO", "เตรียมบท Podcast")

            # 1. Chunking
            chunks = PodcastChunker.chunk(script_text, max_bytes=self.settings.podcast.chunk_max_bytes)
            if not chunks:
                raise AppError("PODCAST_SCRIPT_EMPTY", "บทพูดพอดแคสต์ว่างเปล่า")

            chunk_count = len(chunks)
            self._investigation_log(job_id, "podcast_chunked", total_chunks=chunk_count)
            self._log(job_id, "INFO", f"แบ่งบทเป็น {chunk_count} ส่วน")

            # 2. Audio Synthesis
            self._progress(job_id, JobStatus.GENERATING_AUDIO, 15, f"กำลังสร้างเสียง 0 จาก {chunk_count}")
            provider = create_tts_provider("google-gemini", self.settings)
            audio_service = PodcastAudioService(self.ffmpeg, self.ffprobe, self.settings)

            english_future = None
            if english_script:
                english_chunks = PodcastChunker.chunk(
                    english_script,
                    max_bytes=self.settings.podcast.chunk_max_bytes,
                )
                self._log(job_id, "INFO", f"เตรียม English audio {len(english_chunks)} ส่วน")

                def synthesize_english_audio():
                    english_provider = create_tts_provider("google-gemini", self.settings)
                    english_service = PodcastAudioService(self.ffmpeg, self.ffprobe, self.settings)

                    def english_log(level: str, message: str, technical: bool = False) -> None:
                        prefix = "English audio: "
                        if technical:
                            self._technical_log(job_id, prefix + message)
                        else:
                            self._log(job_id, level, prefix + message)

                    return english_service.synthesize_and_stitch(
                        job_id=f"{job_id}-en",
                        workspace_root=workspace.root,
                        chunks=english_chunks,
                        provider=english_provider,
                        voice=voice,
                        speed=speed,
                        style_prompt=english_style_prompt,
                        language="en-US",
                        namespace="podcast_chunks_en",
                        output_name="english_narration_raw.wav",
                        log_callback=english_log,
                    )

                english_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="podcast-en")
                english_future = english_executor.submit(synthesize_english_audio)

            def audio_progress(completed: int, total: int, step_desc: str) -> None:
                pct = 15 + round(50 * completed / max(1, total))
                self._progress(job_id, JobStatus.GENERATING_AUDIO, pct, step_desc)

            def audio_log(lvl: str, msg: str, tech: bool = False) -> None:
                if tech:
                    self._technical_log(job_id, msg)
                else:
                    self._log(job_id, lvl, msg)

            stitched_audio, chunk_durations, total_dur = audio_service.synthesize_and_stitch(
                job_id=job_id,
                workspace_root=workspace.root,
                chunks=chunks,
                provider=provider,
                voice=voice,
                speed=speed,
                style_prompt=style_prompt,
                language="th-TH",
                progress_callback=audio_progress,
                log_callback=audio_log,
            )
            self._progress(job_id, JobStatus.GENERATING_AUDIO, 65, "สร้างเสียงครบแล้ว")
            self._log(job_id, "SUCCESS", "สร้างเสียงครบแล้ว")

            # 3. Subtitles
            srt_path: Path | None = None
            if enable_subtitles:
                self._progress(job_id, JobStatus.RENDERING_SCENES, 70, "กำลังสร้าง Subtitle")
                self._log(job_id, "INFO", "กำลังสร้าง Subtitle")
                srt_path = workspace.subtitles / "subtitles.srt"
                PodcastSubtitleService().generate_srt(chunks, chunk_durations, srt_path)

            # 4. Video Rendering
            self._progress(job_id, JobStatus.RENDERING_SCENES, 75, "กำลังสร้าง Visual Podcast")
            self._log(job_id, "INFO", "กำลังสร้าง Visual Podcast (1920x1080 30 FPS)")

            resolved_bgm = bgm_path
            if resolved_bgm is None:
                resolved_bgm = resolve_podcast_bgm(self.settings.app.workspace, bgm_track)

            renderer = PodcastVideoRenderer(self.ffmpeg, self.ffprobe, self.settings)
            final_output = workspace.output / "final.mp4"

            raw_desc = (description or "").strip()
            raw_hashtags = (hashtags or "").strip()

            if raw_desc:
                desc_text = raw_desc
            else:
                desc_text = (
                    f"{title}\n\n"
                    "เรื่องเล่าวิทยาศาสตร์และจักรวาลฟังสบายยามค่ำคืน เจาะลึกความลับของเอกภพผ่านมุมมองฟิสิกส์และดาราศาสตร์\n\n"
                    "ค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ"
                )

            if raw_hashtags and raw_hashtags not in desc_text:
                full_description = f"{desc_text}\n\n{raw_hashtags}"
            else:
                full_description = desc_text

            renderer.render(
                job_id=job_id,
                workspace_root=workspace.root,
                cover_image=cover_path,
                narration_audio=stitched_audio,
                total_duration=total_dur,
                output_path=final_output,
                subtitle_path=srt_path,
                bgm_path=resolved_bgm,
                bgm_volume=bgm_volume,
                focus=focus,
                log_callback=audio_log,
                title=title,
                description=full_description,
            )

            # 5. Composing & Completion
            self._progress(job_id, JobStatus.COMPOSING, 95, "กำลังรวมเสียงและเพลง")
            probe = self.ffprobe.probe(final_output)
            video_stream = next(s for s in probe["streams"] if s.get("codec_type") == "video")

            video_duration = float(probe["format"]["duration"])
            english_audio_metadata: dict[str, Any] = {
                "requested": bool(english_script),
                "status": "not_requested",
                "available": False,
            }
            if english_future is not None:
                try:
                    raw_english_audio, _, raw_english_duration = english_future.result()
                    english_audio_path = workspace.output / "podcast-en.wav"
                    _, english_duration = audio_service.create_alternate_track(
                        raw_english_audio,
                        english_audio_path,
                        video_duration,
                        bgm_path=resolved_bgm,
                        bgm_volume=bgm_volume,
                    )
                    english_audio_metadata = {
                        "requested": True,
                        "status": "ready",
                        "available": True,
                        "url": f"/api/jobs/{job_id}/english-audio",
                        "durationSeconds": round(english_duration, 3),
                        "sourceDurationSeconds": round(raw_english_duration, 3),
                        "fileSizeBytes": english_audio_path.stat().st_size,
                        "bgmIncluded": bool(resolved_bgm and resolved_bgm.is_file()),
                        "bgmTrack": bgm_track,
                        "bgmVolume": bgm_volume,
                    }
                    self._log(job_id, "SUCCESS", "English WAV พร้อมดาวน์โหลดแล้ว")
                except AppError as exc:
                    english_audio_metadata = {
                        "requested": True,
                        "status": "failed",
                        "available": False,
                        "error": public_error(exc),
                        "retryUrl": f"/api/jobs/{job_id}/english-audio/retry",
                    }
                    if "chunkIndex" in exc.details:
                        english_audio_metadata["failedChunkIndexes"] = [
                            int(value) for value in exc.details.get("failedChunkIndexes", [exc.details["chunkIndex"]])
                        ]
                    self._log(job_id, "WARNING", f"English WAV ไม่สำเร็จ: {exc.message}")
                except Exception:
                    english_audio_metadata = {
                        "requested": True,
                        "status": "failed",
                        "available": False,
                        "error": {"code": "ENGLISH_AUDIO_FAILED", "message": "สร้าง English WAV ไม่สำเร็จ"},
                        "retryUrl": f"/api/jobs/{job_id}/english-audio/retry",
                    }
                    self._log(job_id, "WARNING", "สร้าง English WAV ไม่สำเร็จ แต่วิดีโอภาษาไทยยังพร้อมใช้งาน")
                    logger.exception("job_id=%s english_audio_failed", job_id)
            metadata = {
                "projectTitle": title,
                "durationSeconds": round(video_duration, 3),
                "resolution": f"{video_stream['width']}x{video_stream['height']}",
                "outputFormat": "youtube",
                "sceneCount": chunk_count,
                "fileSizeBytes": final_output.stat().st_size,
                "createdAt": local_now().isoformat(),
                "videoMetadata": {
                    "title": title,
                    "description": full_description,
                    "hashtags": raw_hashtags,
                },
                "englishAudio": english_audio_metadata,
            }
            self.registry.set_metadata(job_id, metadata)
            if self.persistence:
                current = self.registry.get(job_id)
                if current:
                    self.persistence.upsert_job(current, final_output, metadata)
                self.persistence.update_project_status(project_id, "COMPLETED")

            self._progress(job_id, JobStatus.COMPLETED, 100, "วิดีโอพร้อมแล้ว")
            self._log(job_id, "SUCCESS", "วิดีโอพร้อมแล้ว")
            self.events.publish(
                JobEvent(
                    type=JobEventType.COMPLETED,
                    job_id=job_id,
                    payload={
                        "progress": 100,
                        "status": JobStatus.COMPLETED,
                        "previewUrl": f"/jobs/{job_id}/preview",
                        "videoUrl": f"/api/jobs/{job_id}/video",
                    },
                )
            )
            self._investigation_log(job_id, "podcast_job_completed", elapsed_ms=round((time.monotonic() - started) * 1000))
        except AppError as exc:
            current = self.registry.get(job_id)
            progress = current.progress if current else 0
            step = current.current_step if current else "Processing podcast"
            safe_error = public_error(exc)
            self.registry.update(job_id, JobStatus.FAILED, progress, step, safe_error)
            if self.persistence:
                current = self.registry.get(job_id)
                if current:
                    self.persistence.upsert_job(current)
            self._log(job_id, "ERROR", exc.message)
            self.events.publish(JobEvent(type=JobEventType.FAILED, job_id=job_id, payload={"progress": progress, "status": JobStatus.FAILED, "code": exc.code, "message": exc.message, "currentStep": step}))
            self._investigation_log(job_id, "podcast_job_failed", error_code=exc.code, elapsed_ms=round((time.monotonic() - started) * 1000))
            logger.exception("job_id=%s stage=FAILED error_code=%s", job_id, exc.code)
        except Exception:
            error = AppError("INTERNAL_ERROR", "เกิดข้อผิดพลาดในการประมวลผล Podcast")
            current = self.registry.get(job_id)
            progress = current.progress if current else 0
            step = current.current_step if current else "Processing podcast"
            self.registry.update(job_id, JobStatus.FAILED, progress, step, public_error(error))
            if self.persistence:
                current = self.registry.get(job_id)
                if current:
                    self.persistence.upsert_job(current)
            self._log(job_id, "ERROR", error.message)
            self.events.publish(JobEvent(type=JobEventType.FAILED, job_id=job_id, payload={"progress": progress, "status": JobStatus.FAILED, "code": error.code, "message": error.message, "currentStep": step}))
            self._investigation_log(job_id, "podcast_job_failed", error_code="INTERNAL_ERROR", elapsed_ms=round((time.monotonic() - started) * 1000))
            logger.exception("job_id=%s stage=FAILED error_code=INTERNAL_ERROR", job_id)
        finally:
            if english_executor is not None:
                english_executor.shutdown(wait=False, cancel_futures=True)

    def _render_ffmpeg_scenes(self, job_id: str, script, durations: list[float], raw_audio_durations: list[float] | None, workspace: Workspace, render_profile: RenderProfile, sub_mode: str, transitions: list[str], transition_seconds: float) -> list[Path]:
        """Render independent FFmpeg scenes with bounded parallelism.

        The final compose remains ordered and single-threaded.  Each worker owns
        its SRT and MP4 paths, so no scene writes the same file as another.
        """
        count = len(script.scenes)
        workers = min(count, self.settings.video.ffmpeg_scene_parallelism)
        self._log(job_id, "INFO", f"Rendering FFmpeg scenes in parallel ({workers} workers)")
        self._investigation_log(job_id, "ffmpeg_scene_parallelism", workers=workers, scene_count=count)

        def render_one(index: int) -> tuple[int, Path, int]:
            scene = script.scenes[index]
            duration = durations[index]
            started = time.monotonic()
            final_scene_output = workspace.rendered_scenes / f"{scene.id}.mp4"
            if final_scene_output.is_file() and final_scene_output.stat().st_size > 1000:
                self._log(job_id, "INFO", f"Reusing already rendered video for scene {index + 1}")
                self._investigation_log(job_id, "scene_render_reused", scene_id=scene.id, output=final_scene_output.name)
                return index, final_scene_output, 0
            self._investigation_log(job_id, "scene_render_started", render_engine="ffmpeg_motion", scene_id=scene.id, scene_index=index + 1, motion=scene.motion, transition=scene.transition or self.settings.video.transition, duration_seconds=round(duration, 3))
            try:
                if sub_mode == "disable":
                    show_sub = False
                elif sub_mode == "enable":
                    show_sub = True
                else:
                    show_sub = scene.show_subtitle and bool(scene.subtitle)
                subtitle = None
                if show_sub and (scene.subtitle or scene.narration):
                    leaving = transition_seconds if index < count - 1 and transitions[index] != "none" else 0.0
                    subtitle_start = 0.0
                    raw_audio_duration = raw_audio_durations[index] if raw_audio_durations and index < len(raw_audio_durations) else duration - leaving
                    subtitle_end = min(duration - leaving, raw_audio_duration + 0.15)
                    if subtitle_end > subtitle_start + 0.05:
                        subtitle = SubtitleRenderer().write(scene.subtitle or scene.narration, duration, workspace.subtitles / f"{scene.id}.srt", subtitle_start, subtitle_end)
                        self._investigation_log(job_id, "subtitle_window", scene_id=scene.id, start_seconds=round(subtitle_start, 3), end_seconds=round(subtitle_end, 3), transition_seconds=round(transition_seconds, 3))
                output = SceneRenderer(self.ffmpeg, self.settings, render_profile).render(scene, workspace.extracted / scene.image, workspace.generated_audio / f"{scene.id}.wav", subtitle, duration, final_scene_output)
                return index, output, round((time.monotonic() - started) * 1000)
            except AppError as exc:
                details = {**exc.details, "sceneId": scene.id}
                raise AppError(exc.code, exc.message, details) from exc
            except Exception as exc:
                raise AppError("SCENE_RENDER_FAILED", "Scene rendering failed", {"sceneId": scene.id}) from exc

        completed_paths: dict[int, Path] = {}
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="autoclip-ffmpeg") as executor:
            futures = {}
            for index, scene in enumerate(script.scenes):
                self._log(job_id, "INFO", f"Rendering scene {index + 1} of {count} (queued)")
                futures[executor.submit(render_one, index)] = (index, scene)
            for completed, future in enumerate(as_completed(futures), start=1):
                index, scene = futures[future]
                try:
                    _, output, elapsed_ms = future.result()
                except Exception:
                    for pending in futures:
                        pending.cancel()
                    raise
                completed_paths[index] = output
                self._investigation_log(job_id, "scene_render_completed", render_engine="ffmpeg_motion", scene_id=scene.id, scene_index=index + 1, output=output.name, elapsed_ms=elapsed_ms)
                self._log(job_id, "SUCCESS", f"Scene rendered {index + 1} of {count}")
                self._progress(job_id, JobStatus.RENDERING_SCENES, 40 + round(35 * completed / count), f"Rendered scene {completed} of {count}")
        return [completed_paths[index] for index in range(count)]

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

    def english_audio(self, job_id: str) -> Path:
        return self.settings.app.workspace / job_id / "output" / "podcast-en.wav"

    def retry_podcast_english_audio(self, job_id: str) -> JobRecord:
        record = self.restore(job_id)
        if not record:
            raise AppError("JOB_NOT_FOUND", "Job was not found")
        if record.status != JobStatus.COMPLETED:
            raise AppError("JOB_NOT_READY", "รอให้วิดีโอภาษาไทยเสร็จก่อนลองสร้างเสียงอังกฤษใหม่")
        workspace = self.settings.app.workspace / job_id
        if not (workspace / "source/script-en.txt").is_file():
            raise AppError("ENGLISH_SCRIPT_NOT_FOUND", "ไม่พบบทภาษาอังกฤษของงานนี้")
        if not self.final_video(job_id).is_file():
            raise AppError("VIDEO_NOT_READY", "Video is not ready")
        metadata = dict(record.metadata or {})
        english = dict(metadata.get("englishAudio") or {})
        if english.get("status") == "retrying":
            raise AppError("ENGLISH_AUDIO_RETRY_IN_PROGRESS", "กำลังลองสร้างเสียงอังกฤษใหม่อยู่แล้ว")
        english.update({"requested": True, "status": "retrying", "available": False})
        metadata["englishAudio"] = english
        self.registry.set_metadata(job_id, metadata)
        if self.persistence:
            self.persistence.update_job_metadata(job_id, metadata)
        self._log(job_id, "INFO", "กำลัง Retry เฉพาะ English audio ที่ยังไม่สำเร็จ")
        self.executor.submit(self._retry_podcast_english_audio, job_id)
        return self.registry.get(job_id) or record

    def _retry_podcast_english_audio(self, job_id: str) -> None:
        workspace_root = self.settings.app.workspace / job_id
        try:
            config_path = workspace_root / "source/podcast-settings.json"
            config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.is_file() else {}
            voice = str(config.get("voice") or self.settings.podcast.default_voice)
            speed = float(config.get("speed") or self.settings.podcast.default_speed)
            style = str(config.get("englishStylePrompt") or self.settings.podcast.default_english_style_prompt)
            bgm_track = str(config.get("bgmTrack") or "space.mp3")
            bgm_volume = float(config.get("bgmVolume", self.settings.podcast.default_bgm_volume))
            script_text = (workspace_root / "source/script-en.txt").read_text(encoding="utf-8")
            chunks = PodcastChunker.chunk(script_text, max_bytes=self.settings.podcast.chunk_max_bytes)
            provider = create_tts_provider("google-gemini", self.settings)
            service = PodcastAudioService(self.ffmpeg, self.ffprobe, self.settings)

            def retry_log(level: str, message: str, technical: bool = False) -> None:
                prefix = "English retry: "
                if technical:
                    self._technical_log(job_id, prefix + message)
                else:
                    self._log(job_id, level, prefix + message)

            raw_audio, _, raw_duration = service.synthesize_and_stitch(
                job_id=f"{job_id}-en-retry",
                workspace_root=workspace_root,
                chunks=chunks,
                provider=provider,
                voice=voice,
                speed=speed,
                style_prompt=style,
                language="en-US",
                namespace="podcast_chunks_en",
                output_name="english_narration_raw.wav",
                log_callback=retry_log,
            )
            target_duration = self.ffprobe.duration(self.final_video(job_id))
            custom_bgm_name = config.get("customBgmFile")
            custom_bgm = workspace_root / "source" / str(custom_bgm_name) if custom_bgm_name else None
            bgm_path = custom_bgm if custom_bgm and custom_bgm.is_file() else resolve_podcast_bgm(
                self.settings.app.workspace,
                bgm_track,
            )
            output, final_duration = service.create_alternate_track(
                raw_audio,
                self.english_audio(job_id),
                target_duration,
                bgm_path=bgm_path,
                bgm_volume=bgm_volume,
            )
            record = self.restore(job_id)
            metadata = dict((record.metadata if record else None) or {})
            metadata["englishAudio"] = {
                "requested": True,
                "status": "ready",
                "available": True,
                "url": f"/api/jobs/{job_id}/english-audio",
                "durationSeconds": round(final_duration, 3),
                "sourceDurationSeconds": round(raw_duration, 3),
                "fileSizeBytes": output.stat().st_size,
                "bgmIncluded": bool(bgm_path and bgm_path.is_file()),
                "bgmTrack": bgm_track,
                "bgmVolume": bgm_volume,
            }
            self.registry.set_metadata(job_id, metadata)
            if self.persistence:
                self.persistence.update_job_metadata(job_id, metadata)
            self._log(job_id, "SUCCESS", "Retry English audio สำเร็จ พร้อมฟังและดาวน์โหลดแล้ว")
        except Exception as exc:
            error = exc if isinstance(exc, AppError) else AppError("ENGLISH_AUDIO_FAILED", "สร้าง English WAV ไม่สำเร็จ")
            record = self.restore(job_id)
            metadata = dict((record.metadata if record else None) or {})
            failed = {
                "requested": True,
                "status": "failed",
                "available": False,
                "error": public_error(error),
                "retryUrl": f"/api/jobs/{job_id}/english-audio/retry",
            }
            if "chunkIndex" in error.details:
                failed["failedChunkIndexes"] = [
                    int(value) for value in error.details.get("failedChunkIndexes", [error.details["chunkIndex"]])
                ]
            metadata["englishAudio"] = failed
            self.registry.set_metadata(job_id, metadata)
            if self.persistence:
                self.persistence.update_job_metadata(job_id, metadata)
            self._log(job_id, "ERROR", f"Retry English audio ไม่สำเร็จ: {error.message}")
            logger.exception("job_id=%s english_audio_retry_failed", job_id)

    def update_video_metadata_tags(self, job_id: str, title: str, description: str, artist: str = "Mamase") -> bool:
        try:
            video_path = self.final_video(job_id)
            if not video_path.is_file():
                return False
            meta_args = build_ffmpeg_metadata_args(title=title, description=description, artist=artist)
            if not meta_args:
                return False
            temp_path = video_path.with_name(f"{video_path.stem}_meta_tmp{video_path.suffix}")
            self.ffmpeg.run(
                ["-y", "-i", str(video_path), "-c", "copy", "-movflags", "+faststart", *meta_args, str(temp_path)],
                "METADATA_REMUX_FAILED",
            )
            if temp_path.is_file() and temp_path.stat().st_size > 0:
                temp_path.replace(video_path)
                return True
        except Exception:
            logger.exception("Failed to update video metadata tags for job_id=%s", job_id)
        return False

    def restore(self, job_id: str) -> JobRecord | None:
        current = self.registry.get(job_id)
        if current and not self.persistence:
            return current
        row = self.persistence.get_job(job_id) if self.persistence else None
        if current and not row:
            return current
        if not row:
            return None
        # A completed repair may be written to SQLite after a renderer has
        # already recorded this job as failed in the in-memory registry.  The
        # finished file and durable COMPLETED state are authoritative here;
        # otherwise the download endpoint remains stuck at VIDEO_NOT_READY
        # until a server restart.  Never replace an active in-memory job.
        if current and current.status != JobStatus.COMPLETED:
            repaired_path = Path(row["final_path"]).resolve() if row.get("final_path") else None
            workspace_root = self.settings.app.workspace.resolve()
            if row["status"] == JobStatus.COMPLETED and repaired_path and workspace_root in repaired_path.parents and repaired_path.is_file():
                current = None
            else:
                return current
        if current:
            return current
        status = row["status"]
        if status in {JobStatus.RECEIVED, JobStatus.VALIDATING, JobStatus.GENERATING_AUDIO, JobStatus.RENDERING_SCENES, JobStatus.COMPOSING}:
            status = JobStatus.FAILED
            row["error"] = {"code":"JOB_INTERRUPTED","message":"งานหยุดลงเมื่อ server restart กรุณาสั่งสร้างใหม่"}
        record = JobRecord(job_id=job_id,status=status,progress=row["progress"],current_step="Job interrupted" if status==JobStatus.FAILED and row.get("interrupted") else ("Video is ready" if status==JobStatus.COMPLETED else "Job restored"),error=row.get("error"),metadata=row.get("metadata"),project_id=row.get("project_id"),render_engine=row.get("render_engine") or "ffmpeg_motion",output_format=row.get("output_format") or "use_json")
        self.registry.set(record)
        return record

    def retry(self, job_id: str) -> JobRecord:
        record = self.restore(job_id)
        if not record:
            raise AppError("JOB_NOT_FOUND", "ไม่พบงานที่ต้องการลองใหม่")
        if record.status not in {JobStatus.FAILED, JobStatus.RECEIVED}:
            raise AppError("JOB_NOT_RETRYABLE", "สามารถลองใหม่ได้เฉพาะงานที่สถานะล้มเหลวเท่านั้น")

        workspace = self.workspaces.get(job_id)
        if not (workspace.source / "input.zip").is_file():
            raise AppError("PACKAGE_NOT_FOUND", "ไม่พบไฟล์ต้นฉบับสำหรับลองใหม่ กรุณาอัปโหลดใหม่")

        self.registry.update(
            job_id,
            JobStatus.RECEIVED,
            5,
            "กำลังเริ่มประมวลผลใหม่อีกครั้ง...",
            error=None,
        )
        record = self.registry.get(job_id)
        if self.persistence and record:
            self.persistence.upsert_job(record)

        self._investigation_log(job_id, "job_retry_started", render_engine=record.render_engine if record else "")
        self._log(job_id, "INFO", "กำลังเริ่มประมวลผลใหม่อีกครั้ง (Retrying job)...")
        self._progress(job_id, JobStatus.RECEIVED, 5, "กำลังเริ่มประมวลผลใหม่อีกครั้ง...")
        self.executor.submit(self._process, job_id, workspace)
        return record
