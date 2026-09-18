import asyncio
import base64
import json
import queue
import shutil
import sqlite3
import uuid
from typing import Any
from datetime import date
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.domain.enums import JobStatus
from app.domain.errors import AppError, public_error
from app.domain.events import JobEvent, JobEventType
from app.domain.ai_models import AiProject
from app.domain.zodiac_models import ZodiacBatchImport, ZodiacMetadataUpdate
from app.services.bgm_service import ensure_default_bgm, get_podcast_bgm_catalog, resolve_podcast_bgm

router = APIRouter(prefix="/api")


def _zodiac_readings(body: ZodiacBatchImport) -> dict[str, dict]:
    return {item.id: item.model_dump() for item in body.zodiacs}


@router.get("/zodiac/master")
def zodiac_master(request: Request) -> dict:
    try:
        return request.app.state.zodiac_service.master()
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.get("/zodiac/example")
def zodiac_example(request: Request) -> dict:
    master = request.app.state.zodiac_service.master()
    return {
        "schema": "autoclip.zodiac-weekly-batch.v1",
        "week": {"start_date": "2026-09-14", "end_date": "2026-09-20"},
        "tts_provider": "google-gemini",
        "voice": {"voice": "Iapetus", "language": "th-TH", "speed": 1.10},
        "visual": {
            "use_template_as_primary_visual": True,
            "generate_new_images": False,
            "date_overlay": {"enabled": True, "text_source": "week.display_th", "preserve_master_image": True},
            "motion": {"enabled": False, "preset": "none"},
        },
        "zodiacs": [],
        "help": "เว้น zodiacs เป็น [] เพื่อให้ระบบสร้างคำทำนายมาตรฐาน หรือใส่ครบ 12 ราศีตามรายการ master",
        "master": master["zodiacs"],
    }


@router.post("/zodiac/batches")
def create_zodiac_batch(request: Request, body: ZodiacBatchImport) -> dict:
    try:
        return request.app.state.zodiac_service.create_batch(
            body.start_date, body.end_date, body.tts_provider, _zodiac_readings(body),
            body.visual.model_dump(), body.voice.model_dump(), body.channel_id,
        )
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc
    except KeyError as exc:
        raise HTTPException(400, public_error(AppError("CHANNEL_NOT_FOUND", "ไม่พบ Channel ที่เลือก"))) from exc


@router.get("/zodiac/batches")
def list_zodiac_batches(request: Request) -> dict:
    return {"batches": request.app.state.zodiac_service.list_batches()}


@router.get("/zodiac/batches/{batch_id}")
def get_zodiac_batch(request: Request, batch_id: str) -> dict:
    try:
        return request.app.state.zodiac_service.get_batch(batch_id)
    except AppError as exc:
        raise HTTPException(404, public_error(exc)) from exc


@router.post("/zodiac/batches/{batch_id}/retry-failed")
def retry_zodiac_batch(request: Request, batch_id: str) -> dict:
    try:
        return request.app.state.zodiac_service.retry_failed(batch_id)
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.post("/zodiac/batches/{batch_id}/{zodiac_id}/regenerate")
def regenerate_zodiac_child(request: Request, batch_id: str, zodiac_id: str) -> dict:
    try:
        return request.app.state.zodiac_service.regenerate_child(batch_id, zodiac_id)
    except AppError as exc:
        raise HTTPException(409, public_error(exc)) from exc


@router.delete("/zodiac/batches/{batch_id}")
def delete_zodiac_batch(request: Request, batch_id: str) -> dict:
    try:
        return request.app.state.zodiac_service.delete_batch(batch_id)
    except AppError as exc:
        raise HTTPException(409, public_error(exc)) from exc


@router.get("/zodiac/batches/{batch_id}/{zodiac_id}/package")
def download_zodiac_package(request: Request, batch_id: str, zodiac_id: str) -> FileResponse:
    path = request.app.state.zodiac_service.package_path(batch_id, zodiac_id)
    return FileResponse(path, media_type="application/zip", filename=path.name)


@router.get("/zodiac/batches/{batch_id}/{zodiac_id}/video")
def download_zodiac_video(request: Request, batch_id: str, zodiac_id: str) -> FileResponse:
    path = request.app.state.zodiac_service.video_path(batch_id, zodiac_id)
    filename = request.app.state.zodiac_service.video_filename(batch_id, zodiac_id)
    return FileResponse(path, media_type="video/mp4", filename=filename)


@router.get("/zodiac/batches/{batch_id}/all-packages")
def download_all_zodiac_packages(request: Request, batch_id: str) -> FileResponse:
    path = request.app.state.zodiac_service.archive(batch_id, "packages")
    return FileResponse(path, media_type="application/zip", filename=path.name)


@router.get("/zodiac/batches/{batch_id}/all-videos")
def download_all_zodiac_videos(request: Request, batch_id: str) -> FileResponse:
    path = request.app.state.zodiac_service.archive(batch_id, "videos")
    return FileResponse(path, media_type="application/zip", filename=path.name)


@router.get("/zodiac/batches/{batch_id}/complete-archive")
def download_complete_zodiac_archive(request: Request, batch_id: str) -> FileResponse:
    path = request.app.state.zodiac_service.complete_archive(batch_id)
    return FileResponse(path, media_type="application/zip", filename=path.name)


@router.patch("/zodiac/batches/{batch_id}/{zodiac_id}/metadata")
def update_zodiac_metadata(request: Request, batch_id: str, zodiac_id: str, body: ZodiacMetadataUpdate) -> dict:
    try:
        return request.app.state.zodiac_service.update_metadata(batch_id, zodiac_id, body.model_dump())
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.post("/zodiac/batches/{batch_id}/regenerate-metadata")
def regenerate_zodiac_metadata(request: Request, batch_id: str) -> dict:
    try:
        return request.app.state.zodiac_service.regenerate_metadata(batch_id)
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.get("/zodiac/batches/{batch_id}/{zodiac_id}/metadata")
def download_zodiac_metadata(request: Request, batch_id: str, zodiac_id: str) -> FileResponse:
    path = request.app.state.zodiac_service.metadata_path(batch_id, zodiac_id)
    return FileResponse(path, media_type="application/json", filename=path.name)


@router.get("/zodiac/batches/{batch_id}/upload-csv")
def download_zodiac_csv(request: Request, batch_id: str) -> FileResponse:
    path = request.app.state.zodiac_service.csv_path(batch_id)
    return FileResponse(path, media_type="text/csv", filename="youtube-upload.csv")


@router.get("/zodiac/batches/{batch_id}/all-metadata")
def download_all_zodiac_metadata(request: Request, batch_id: str) -> FileResponse:
    path = request.app.state.zodiac_service.metadata_archive(batch_id)
    return FileResponse(path, media_type="application/zip", filename=path.name)


class AiMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)


class AiAutomaticRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)
    concept: str = Field(default="", max_length=4000)
    channel_id: str = "undefined"


class AiSceneUpdate(BaseModel):
    narration: str | None = None
    tts_text: str | None = None
    subtitle: str | None = None
    show_subtitle: bool | None = None
    image_prompt: str | None = None
    motion: str | None = None
    transition: str | None = None
    estimated_duration: float | None = None
    wan: dict | None = None

class YouTubeUploadRequest(BaseModel):
    connectionId: str
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=5000)
    tags: list[str] = Field(default_factory=list, max_length=30)
    privacyStatus: str = "private"

class VideoMetadataRequest(BaseModel):
    title: str = Field(default="-", max_length=100)
    description: str = Field(default="-", max_length=10000)
    hashtags: str = Field(default="", max_length=3000)


class HistoryPublishStatusRequest(BaseModel):
    published: bool

class ChannelRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class ProjectChannelRequest(BaseModel):
    channelId: str = Field(min_length=1, max_length=80)


class ZodiacAiDraftRequest(BaseModel):
    start_date: date
    end_date: date


@router.get("/zodiac/ai/status")
def zodiac_ai_status(request: Request) -> dict:
    return request.app.state.zodiac_ai_service.status()


@router.get("/zodiac/ai/log")
def zodiac_ai_log(request: Request) -> dict:
    return {"log": request.app.state.zodiac_ai_service.last_log}


@router.post("/zodiac/ai/draft")
def zodiac_ai_draft(request: Request, body: ZodiacAiDraftRequest) -> dict:
    if body.end_date < body.start_date:
        raise HTTPException(422, {"code": "INVALID_WEEK", "message": "วันสิ้นสุดต้องไม่ก่อนวันเริ่มต้น"})
    try:
        draft = request.app.state.zodiac_ai_service.generate(body.start_date, body.end_date)
        return {
            **draft,
            "draft": draft,
            "log": request.app.state.zodiac_ai_service.last_log,
        }
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.post("/tts")
def create_thai_speech(
    request: Request,
    text: str = Form(...),
    voice: str = Form("thai-male-01"),
    speed: float = Form(1.0),
    provider: str = Form("local"),
    style_prompt: str | None = Form(None),
) -> FileResponse:
    try:
        path = request.app.state.tts_preview_service.synthesize(text, voice, speed, provider, style_prompt)
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc
    except Exception:
        # Keep preview failures as a normal API response; never make the browser
        # see a connection-level "Failed to fetch" for an internal TTS error.
        raise HTTPException(500, public_error(AppError("TTS_GENERATION_FAILED", "สร้างเสียงตัวอย่างไม่สำเร็จ")))
    return FileResponse(path, media_type="audio/wav", filename="autoclip-thai-speech.wav")


@router.get("/bgm-preview")
def preview_background_music(request: Request) -> FileResponse:
    """Play the same system fallback BGM used when a ZIP has no bgm asset."""
    path = ensure_default_bgm(request.app.state.settings.app.workspace)
    return FileResponse(path, media_type="audio/wav", filename="autoclip-default-bgm.wav")


@router.post("/podcast/preview-audio")
def podcast_preview_audio(
    request: Request,
    text: str | None = Form(None),
    voice: str = Form("Iapetus"),
    speed: float = Form(0.90),
    style_prompt: str | None = Form(None),
    language: str = Form("th-TH"),
) -> FileResponse:
    sample_text = (text or "").strip()
    if not sample_text:
        sample_text = (
            "สวัสดีครับ ยินดีต้อนรับสู่ช่วงเวลาแห่งความผ่อนคลาย "
            "ค่ำคืนนี้ขอให้ปล่อยวางความเหนื่อยล้า แล้วเดินทางสู่ความสงบไปด้วยกันครับ"
        )
    else:
        import re
        sentences = [s.strip() for s in re.split(r"[.!?\n]+", sample_text) if s.strip()]
        if len(sentences) >= 2:
            sample_text = " ".join(sentences[:3])
        if len(sample_text) > 300:
            sample_text = sample_text[:300].rsplit(" ", 1)[0] + "..."

    try:
        path = request.app.state.tts_preview_service.synthesize(
            text=sample_text,
            voice=voice,
            speed=speed,
            provider_name="google-gemini",
            style_prompt=request.app.state.settings.podcast.resolve_style_prompt(voice, style_prompt),
            language="en-US" if language.lower().startswith("en") else "th-TH",
        )
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, public_error(AppError("TTS_GENERATION_FAILED", "สร้างเสียงตัวอย่างไม่สำเร็จ"))) from exc
    return FileResponse(path, media_type="audio/wav", filename="podcast-sample.wav")


@router.get("/podcast/bgm-tracks")
def list_podcast_bgm_tracks() -> dict:
    return {"tracks": get_podcast_bgm_catalog()}


@router.get("/podcast/bgm-preview/{track_id}")
def preview_podcast_bgm(request: Request, track_id: str) -> FileResponse:
    try:
        path = resolve_podcast_bgm(request.app.state.settings.app.workspace, track_id)
        if not path.is_file():
            raise HTTPException(404, public_error(AppError("BGM_NOT_FOUND", "ไม่พบเพลง BGM ที่เลือก")))
        mimes = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".m4a": "audio/mp4",
            ".aac": "audio/aac",
            ".ogg": "audio/ogg",
            ".flac": "audio/flac",
        }
        media_type = mimes.get(path.suffix.lower(), "audio/mpeg")
        return FileResponse(path, media_type=media_type, filename=path.name)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(404, public_error(AppError("BGM_NOT_FOUND", "ไม่พบเพลง BGM ที่เลือก"))) from exc


@router.post("/bgm/upload")
def upload_bgm_track(bgm_file: UploadFile = File(...)) -> dict[str, Any]:
    ext = Path(bgm_file.filename).suffix.lower()
    if ext not in {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}:
        raise HTTPException(400, public_error(AppError("INVALID_AUDIO_FORMAT", "รองรับเฉพาะไฟล์เสียง .mp3, .wav, .m4a, .aac, .ogg, .flac")))
    import re
    import shutil
    from app.services.bgm_service import SOUNDS_DIR
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    raw_stem = Path(bgm_file.filename).stem
    clean_stem = re.sub(r'[^a-zA-Z0-9_\-\u0e00-\u0e7f]', '_', raw_stem).strip('_') or "custom_bgm"
    target = SOUNDS_DIR / f"{clean_stem}{ext}"
    with target.open("wb") as out:
        shutil.copyfileobj(bgm_file.file, out)
    return {
        "id": target.name,
        "name": f"🎵 {target.name}",
        "filename": target.name,
        "url": f"/api/podcast/bgm-preview/{target.name}",
    }


@router.post("/podcast/jobs", status_code=202)
def create_podcast_job(
    request: Request,
    cover_image: UploadFile = File(...),
    title: str = Form("YouTube Podcast"),
    script: str | None = Form(None),
    script_text: str | None = Form(None),
    english_script: str = Form(""),
    voice: str = Form("Enceladus"),
    description: str = Form(""),
    hashtags: str = Form(""),
    speed: float = Form(0.90),
    style_prompt: str | None = Form(None),
    english_style_prompt: str | None = Form(None),
    enable_subtitles: bool = Form(True),
    bgm_file: UploadFile | None = File(None),
    bgm_track: str = Form("mamase-podcast-bg.mp3"),
    bgm_volume: float = Form(0.08),
    focus: str = Form("center"),
    channel_id: str = Form("undefined"),
) -> dict:
    effective_script = (script_text if script_text is not None else script) or ""
    if not effective_script.strip():
        raise HTTPException(400, public_error(AppError("PODCAST_SCRIPT_EMPTY", "กรุณาใส่บทพูดสำหรับ Podcast")))
    try:
        record = request.app.state.job_service.submit_podcast(
            image_file=cover_image,
            title=title,
            script_text=effective_script,
            english_script=english_script,
            voice=voice,
            speed=speed,
            style_prompt=style_prompt,
            english_style_prompt=english_style_prompt,
            enable_subtitles=enable_subtitles,
            description=description,
            hashtags=hashtags,
            bgm_file=bgm_file,
            bgm_track=bgm_track,
            bgm_volume=bgm_volume,
            focus=focus,
            channel_id=channel_id,
        )
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc
    except KeyError as exc:
        raise HTTPException(400, public_error(AppError("CHANNEL_NOT_FOUND", "ไม่พบ Channel ที่เลือก"))) from exc
    return {"jobId": record.job_id, "status": record.status}


@router.post("/quick-reel")
def create_quick_reel(
    request: Request,
    image: UploadFile | None = File(None),
    images: list[UploadFile] | None = File(None),
    script: str | None = Form(None),
    script_text: str | None = Form(None),
    tts_segments: str | None = Form(None),
    voice: str = Form("Iapetus"),
    speed: float = Form(1.10),
    style_prompt: str | None = Form(None),
    motion: str = Form("static"),
    fit: str = Form("contain"),
    hook_enabled: bool = Form(False),
    hook_text: str = Form(""),
    hook_position: str = Form("top"),
    subtitles_enabled: bool = Form(True),
    bgm_enabled: bool = Form(False),
    bgm_track: str = Form("cosmic_drift"),
    bgm_file: UploadFile | None = File(None),
    bgm_volume: float = Form(0.10),
    title: str = Form(""),
    description: str = Form(""),
    hashtags: str = Form(""),
    channel_id: str = Form("undefined"),
) -> dict:
    effective_script = (script_text if script_text is not None else script) or ""
    if not effective_script.strip():
        raise HTTPException(400, public_error(AppError("QUICK_REEL_SCRIPT_EMPTY", "กรุณาใส่บทพูดสำหรับ Quick Reel")))
    try:
        parsed_segments: list[str] | None = None
        if tts_segments:
            try:
                decoded = json.loads(tts_segments)
            except json.JSONDecodeError as exc:
                raise AppError("QUICK_REEL_TTS_SEGMENTS_INVALID", "ข้อมูล tts array ไม่ใช่ JSON ที่ถูกต้อง") from exc
            if not isinstance(decoded, list) or not decoded or not all(isinstance(item, str) and item.strip() for item in decoded):
                raise AppError("QUICK_REEL_TTS_SEGMENTS_INVALID", "tts ต้องเป็น array ของข้อความที่ไม่ว่าง")
            parsed_segments = [item.strip() for item in decoded]
        record = request.app.state.quick_reel_service.submit_quick_reel(
            image_file=image,
            image_files=images,
            script_text=effective_script,
            tts_segments=parsed_segments,
            voice=voice,
            speed=speed,
            style_prompt=style_prompt,
            motion=motion,
            fit=fit,
            hook_enabled=hook_enabled,
            hook_text=hook_text,
            hook_position=hook_position,
            subtitles_enabled=subtitles_enabled,
            bgm_enabled=bgm_enabled,
            bgm_track=bgm_track,
            bgm_file=bgm_file,
            bgm_volume=bgm_volume,
            title=title,
            description=description,
            hashtags=hashtags,
            channel_id=channel_id,
        )
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc
    except KeyError as exc:
        raise HTTPException(400, public_error(AppError("CHANNEL_NOT_FOUND", "ไม่พบ Channel ที่เลือก"))) from exc
    return {"jobId": record.job_id, "status": record.status}


@router.get("/quick-reel/{job_id}")
def get_quick_reel(request: Request, job_id: str) -> dict:
    try:
        return request.app.state.quick_reel_service.get_job(job_id)
    except AppError as exc:
        raise HTTPException(404 if exc.code == "JOB_NOT_FOUND" else 400, public_error(exc)) from exc


@router.get("/quick-reel/{job_id}/video")
def get_quick_reel_video(request: Request, job_id: str) -> FileResponse:
    try:
        path = request.app.state.quick_reel_service.video_path(job_id)
        return FileResponse(path, media_type="video/mp4", filename=f"quick-reel-{job_id[:8]}.mp4")
    except AppError as exc:
        raise HTTPException(404 if exc.code in {"JOB_NOT_FOUND", "VIDEO_NOT_READY"} else 400, public_error(exc)) from exc


@router.delete("/quick-reel/{job_id}")
def delete_quick_reel(request: Request, job_id: str) -> dict:
    try:
        return request.app.state.quick_reel_service.delete_job(job_id)
    except AppError as exc:
        raise HTTPException(404 if exc.code == "JOB_NOT_FOUND" else 400, public_error(exc)) from exc


@router.post("/quick-reel/{job_id}/remotion")
async def remotion_quick_reel(request: Request, job_id: str) -> dict:
    try:
        body = await request.json()
        motion = str(body.get("motion", "")).strip()
        fit = body.get("fit")
        if fit is not None:
            fit = str(fit).strip()
        if not motion and not fit:
            raise AppError("INVALID_MOTION", "กรุณาระบุ motion หรือ fit ที่ต้องการเปลี่ยน")
        service = request.app.state.quick_reel_service
        return await asyncio.to_thread(service.remotion_quick_reel, job_id, motion, fit=fit)
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, public_error(AppError("REMOTION_FAILED", str(exc)))) from exc



@router.post("/jobs", status_code=202)
def create_job(
    request: Request,
    file: UploadFile = File(...),
    tts_provider: str | None = Form(None),
    subtitle_mode: str | None = Form(None),
    render_engine: str | None = Form(None),
    output_format: str | None = Form(None),
    motion_resolution: str | None = Form(None),
    script_json: str | None = Form(None),
    channel_id: str = Form("undefined"),
) -> dict:
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, public_error(AppError("PACKAGE_INVALID", "Exactly one ZIP file is required")))
    try:
        record = request.app.state.job_service.submit(file, tts_provider, subtitle_mode, script_json, render_engine, output_format, motion_resolution, channel_id)
    except AppError as exc:
        raise HTTPException(413 if exc.code == "UPLOAD_TOO_LARGE" else 400, public_error(exc)) from exc
    except KeyError as exc:
        raise HTTPException(400, public_error(AppError("CHANNEL_NOT_FOUND", "ไม่พบ Channel ที่เลือก"))) from exc
    return {"jobId": record.job_id, "status": record.status}


@router.post("/package-preview")
def package_preview(request: Request, file: UploadFile = File(...)) -> dict:
    """Validate a ZIP and return its script for the pre-render editor."""
    root = request.app.state.settings.app.workspace / "preview-uploads" / str(uuid.uuid4())
    root.mkdir(parents=True, exist_ok=True)
    archive = root / "input.zip"
    try:
        with archive.open("wb") as out:
            size = 0
            while chunk := file.file.read(1024 * 1024):
                size += len(chunk)
                if size > request.app.state.settings.app.max_upload_mb * 1024 * 1024:
                    raise AppError("UPLOAD_TOO_LARGE", "Upload exceeds the configured size limit")
                out.write(chunk)
        from app.services.package_service import PackageService
        extracted = root / "extracted"
        script, _ = PackageService(request.app.state.settings.app.max_extracted_mb * 1024 * 1024).extract_and_validate(archive, extracted)
        previews = {}
        mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
        for scene in script.scenes:
            image = extracted / scene.image
            if image.is_file() and image.stat().st_size <= 4 * 1024 * 1024:
                previews[scene.id] = f"data:{mime.get(image.suffix.lower(), 'application/octet-stream')};base64," + base64.b64encode(image.read_bytes()).decode("ascii")
        return {"script": script.model_dump(mode="json"), "imagePreviews": previews}
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc
    finally:
        shutil.rmtree(root, ignore_errors=True)


@router.get("/jobs/{job_id}")
def get_job(request: Request, job_id: str) -> dict:
    record = request.app.state.job_service.restore(job_id)
    if not record:
        raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "Job was not found")))
    return record.api_dict()


@router.post("/jobs/{job_id}/retry")
def retry_job(request: Request, job_id: str) -> dict:
    try:
        record = request.app.state.job_service.retry(job_id)
    except AppError as exc:
        raise HTTPException(404 if exc.code == "JOB_NOT_FOUND" else 400, public_error(exc)) from exc
    return {"jobId": record.job_id, "status": record.status}


@router.get("/jobs/{job_id}/scenes")
def get_job_scenes(request: Request, job_id: str) -> dict:
    try:
        return request.app.state.job_service.get_scenes(job_id)
    except AppError as exc:
        raise HTTPException(404 if exc.code == "JOB_NOT_FOUND" else 400, public_error(exc)) from exc


@router.get("/jobs/{job_id}/scenes/{scene_id}/image")
def get_job_scene_image(request: Request, job_id: str, scene_id: str) -> FileResponse:
    try:
        path, media_type = request.app.state.job_service.get_scene_asset(job_id, scene_id, "image")
        return FileResponse(path, media_type=media_type, headers={"Cache-Control": "no-cache"})
    except AppError as exc:
        raise HTTPException(404 if exc.code in {"JOB_NOT_FOUND", "ASSET_NOT_FOUND"} else 400, public_error(exc)) from exc


@router.get("/jobs/{job_id}/scenes/{scene_id}/audio")
def get_job_scene_audio(request: Request, job_id: str, scene_id: str) -> FileResponse:
    try:
        path, media_type = request.app.state.job_service.get_scene_asset(job_id, scene_id, "audio")
        return FileResponse(path, media_type=media_type, headers={"Cache-Control": "no-cache"})
    except AppError as exc:
        raise HTTPException(404 if exc.code in {"JOB_NOT_FOUND", "ASSET_NOT_FOUND"} else 400, public_error(exc)) from exc


@router.post("/jobs/{job_id}/scenes/{scene_id}/edit")
async def edit_job_scene(
    request: Request,
    job_id: str,
    scene_id: str,
    narration: str | None = Form(None),
    subtitle: str | None = Form(None),
    motion: str | None = Form(None),
    image: UploadFile | None = File(None),
) -> dict:
    try:
        content_type = request.headers.get("content-type", "")
        img_bytes = None
        img_filename = None
        if "application/json" in content_type:
            body = await request.json()
            narration = body.get("narration")
            subtitle = body.get("subtitle")
            motion = body.get("motion")
        else:
            if image and image.filename:
                img_bytes = await image.read()
                img_filename = image.filename

        workspace = request.app.state.job_service.workspaces.get(job_id)
        if (workspace.source / "quick-reel-settings.json").is_file():
            service = request.app.state.quick_reel_service
            return await asyncio.to_thread(
                service.edit_quick_reel,
                job_id,
                new_script=narration,
                new_motion=motion,
                image_bytes=img_bytes,
                image_filename=img_filename,
            )

        return request.app.state.job_service.edit_scene(
            job_id,
            scene_id,
            narration=narration,
            subtitle=subtitle,
            motion=motion,
            image_bytes=img_bytes,
            image_filename=img_filename,
        )
    except AppError as exc:
        raise HTTPException(404 if exc.code == "JOB_NOT_FOUND" else 400, public_error(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, public_error(AppError("EDIT_SCENE_FAILED", str(exc)))) from exc


@router.post("/jobs/{job_id}/re-render")
def rerender_job(request: Request, job_id: str) -> dict:
    try:
        record = request.app.state.job_service.re_render(job_id)
        return {"jobId": record.job_id, "status": record.status}
    except AppError as exc:
        raise HTTPException(404 if exc.code == "JOB_NOT_FOUND" else 400, public_error(exc)) from exc


@router.post("/jobs/{job_id}/swap-cover")
async def swap_podcast_cover(
    request: Request,
    job_id: str,
    image: UploadFile = File(...),
) -> dict:
    try:
        img_bytes = await image.read()
        return request.app.state.job_service.swap_podcast_cover(job_id, img_bytes, image.filename or "cover.png")
    except AppError as exc:
        raise HTTPException(404 if exc.code == "JOB_NOT_FOUND" else 400, public_error(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, public_error(AppError("SWAP_COVER_FAILED", str(exc)))) from exc


@router.get("/jobs/{job_id}/events")
def job_events(request: Request, job_id: str) -> StreamingResponse:
    service = request.app.state.job_service
    if not service.restore(job_id):
        raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "Job was not found")))

    async def stream():
        with service.events.subscribe(job_id) as subscriber:
            record = service.registry.get(job_id)
            if not record:
                return
            yield JobEvent(type=JobEventType.PROGRESS, job_id=job_id, payload={"progress": record.progress, "status": record.status, "currentStep": record.current_step}).to_sse()
            for entry in record.logs:
                yield JobEvent(type=JobEventType.LOG, job_id=job_id, payload=entry).to_sse()
            if record.status == JobStatus.COMPLETED:
                yield JobEvent(type=JobEventType.COMPLETED, job_id=job_id, payload={"progress": 100, "status": JobStatus.COMPLETED, "previewUrl": f"/jobs/{job_id}/preview", "videoUrl": f"/api/jobs/{job_id}/video"}).to_sse()
                return
            if record.status == JobStatus.FAILED:
                error = record.error or {"code": "INTERNAL_ERROR", "message": "Job failed"}
                yield JobEvent(type=JobEventType.FAILED, job_id=job_id, payload={"progress": record.progress, "status": JobStatus.FAILED, "code": error["code"], "message": error["message"], "currentStep": record.current_step}).to_sse()
                return
            while not await request.is_disconnected():
                try:
                    event = await asyncio.to_thread(subscriber.get, True, 15)
                except queue.Empty:
                    yield JobEvent(type=JobEventType.HEARTBEAT, job_id=job_id).to_sse()
                    continue
                yield event.to_sse()
                if event.type in {JobEventType.COMPLETED, JobEventType.FAILED}:
                    return

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"})


@router.get("/jobs/{job_id}/video-metadata")
def get_video_metadata(request: Request, job_id: str) -> dict:
    record = request.app.state.job_service.restore(job_id)
    if not record: raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "Job was not found")))
    return (record.metadata or {}).get("videoMetadata", {"title": "-", "description": "-", "hashtags": ""})

@router.put("/jobs/{job_id}/video-metadata")
def save_video_metadata(request: Request, job_id: str, body: VideoMetadataRequest) -> dict:
    record = request.app.state.job_service.restore(job_id)
    if not record: raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "Job was not found")))
    metadata = dict(record.metadata or {})
    title = body.title.strip() or "-"
    description = body.description if body.description else "-"
    hashtags = body.hashtags.strip() if body.hashtags else ""
    metadata["videoMetadata"] = {"title": title, "description": description, "hashtags": hashtags}
    request.app.state.job_service.registry.set_metadata(job_id, metadata)
    if not request.app.state.persistence.update_job_metadata(job_id, metadata): raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "Job was not found")))
    full_desc = description
    if hashtags and hashtags not in description:
        full_desc = f"{description}\n\n{hashtags}" if description != "-" else hashtags
    request.app.state.job_service.update_video_metadata_tags(
        job_id,
        title=title if title != "-" else "",
        description=full_desc if full_desc != "-" else "",
    )
    return metadata["videoMetadata"]

@router.get("/jobs/{job_id}/video")
def get_video(request: Request, job_id: str) -> FileResponse:
    record = request.app.state.job_service.restore(job_id)
    if not record:
        raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "Job was not found")))
    if record.status != JobStatus.COMPLETED:
        raise HTTPException(409, public_error(AppError("VIDEO_NOT_READY", "Video is not ready")))
    path = request.app.state.job_service.final_video(job_id)
    if not path.is_file():
        raise HTTPException(500, public_error(AppError("INTERNAL_ERROR", "Completed video is unavailable")))
    filename = f"{record.project_id}.mp4" if record.project_id else "final.mp4"
    return FileResponse(path, media_type="video/mp4", filename=filename)


@router.get("/jobs/{job_id}/thumbnail")
def get_job_thumbnail(request: Request, job_id: str) -> FileResponse:
    path = request.app.state.job_service.thumbnail(job_id)
    if not path or not path.is_file():
        raise HTTPException(404, "Thumbnail not found")
    media_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return FileResponse(path, media_type=media_type, headers={"Cache-Control": "public, max-age=86400"})


@router.get("/jobs/{job_id}/english-audio")
def get_podcast_english_audio(request: Request, job_id: str) -> FileResponse:
    record = request.app.state.job_service.restore(job_id)
    if not record:
        raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "Job was not found")))
    path = request.app.state.job_service.english_audio(job_id)
    if not path.is_file():
        raise HTTPException(409, public_error(AppError("ENGLISH_AUDIO_NOT_READY", "English audio is not ready")))
    filename = f"{record.project_id}-en.wav" if record.project_id else "podcast-en.wav"
    return FileResponse(path, media_type="audio/wav", filename=filename)


@router.post("/jobs/{job_id}/english-audio/retry", status_code=202)
def retry_podcast_english_audio(request: Request, job_id: str) -> dict:
    try:
        record = request.app.state.job_service.retry_podcast_english_audio(job_id)
    except AppError as exc:
        status = 404 if exc.code == "JOB_NOT_FOUND" else 409 if exc.code == "ENGLISH_AUDIO_RETRY_IN_PROGRESS" else 400
        raise HTTPException(status, public_error(exc)) from exc
    return {"jobId": record.job_id, "status": "retrying", "retrying": "englishAudio"}


@router.get("/ai/status")
def ai_status(request: Request) -> dict:
    return {"configured": request.app.state.ai_project_service.configured}


@router.get("/history")
def history(request: Request) -> dict:
    return {"projects": request.app.state.persistence.history()}

@router.get("/channels")
def list_channels(request: Request) -> dict:
    return {"channels": request.app.state.persistence.channels()}

@router.post("/channels", status_code=201)
def create_channel(request: Request, body: ChannelRequest) -> dict:
    try:
        return request.app.state.persistence.create_channel(body.name)
    except (ValueError, sqlite3.IntegrityError) as exc:
        raise HTTPException(409, public_error(AppError("CHANNEL_NAME_INVALID", "ชื่อ Channel ว่างหรือซ้ำกับชื่อเดิม"))) from exc

@router.patch("/channels/{channel_id}")
def rename_channel(request: Request, channel_id: str, body: ChannelRequest) -> dict:
    try:
        return request.app.state.persistence.rename_channel(channel_id, body.name)
    except KeyError as exc:
        raise HTTPException(404, public_error(AppError("CHANNEL_NOT_FOUND", "ไม่พบ Channel"))) from exc
    except (ValueError, sqlite3.IntegrityError) as exc:
        raise HTTPException(409, public_error(AppError("CHANNEL_NAME_INVALID", "ชื่อ Channel ว่าง ซ้ำ หรือแก้ไขไม่ได้"))) from exc

@router.patch("/history/{history_id}/channel")
def set_history_channel(request: Request, history_id: str, body: ProjectChannelRequest) -> dict:
    try:
        return request.app.state.persistence.set_project_channel(history_id, body.channelId)
    except KeyError as exc:
        raise HTTPException(404, public_error(AppError("CHANNEL_OR_PROJECT_NOT_FOUND", "ไม่พบ Channel หรือ Content"))) from exc


@router.patch("/history/{history_id}/published")
def set_history_published(request: Request, history_id: str, body: HistoryPublishStatusRequest) -> dict:
    try:
        return request.app.state.persistence.set_published(history_id, body.published)
    except KeyError as exc:
        raise HTTPException(404, public_error(AppError("PROJECT_NOT_FOUND", "ไม่พบโปรเจกต์"))) from exc


@router.get("/jobs/{job_id}/publication")
def get_job_publication(request: Request, job_id: str) -> dict:
    record = request.app.state.job_service.restore(job_id)
    if not record:
        raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "Job was not found")))
    if not record.project_id:
        raise HTTPException(409, public_error(AppError("PROJECT_NOT_LINKED", "งานนี้ยังไม่ได้เชื่อมกับโปรเจกต์")))
    return {"jobId": job_id, "projectId": record.project_id, "published": request.app.state.persistence.get_published(record.project_id)}

@router.get("/jobs/{job_id}/channel")
def get_job_channel(request: Request, job_id: str) -> dict:
    record = request.app.state.job_service.restore(job_id)
    if not record or not record.project_id:
        raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "ไม่พบงาน")))
    channel = request.app.state.persistence.get_project_channel(record.project_id)
    if not channel:
        raise HTTPException(404, public_error(AppError("PROJECT_NOT_FOUND", "ไม่พบ Content")))
    return {"jobId": job_id, "projectId": record.project_id, **channel}

@router.patch("/jobs/{job_id}/channel")
def set_job_channel(request: Request, job_id: str, body: ProjectChannelRequest) -> dict:
    record = request.app.state.job_service.restore(job_id)
    if not record or not record.project_id:
        raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "ไม่พบงาน")))
    try:
        return {"jobId": job_id, **request.app.state.persistence.set_project_channel(record.project_id, body.channelId)}
    except KeyError as exc:
        raise HTTPException(404, public_error(AppError("CHANNEL_NOT_FOUND", "ไม่พบ Channel"))) from exc


@router.patch("/jobs/{job_id}/publication")
def set_job_publication(request: Request, job_id: str, body: HistoryPublishStatusRequest) -> dict:
    record = request.app.state.job_service.restore(job_id)
    if not record:
        raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "Job was not found")))
    if not record.project_id:
        raise HTTPException(409, public_error(AppError("PROJECT_NOT_LINKED", "งานนี้ยังไม่ได้เชื่อมกับโปรเจกต์")))
    try:
        result = request.app.state.persistence.set_published(record.project_id, body.published)
    except KeyError as exc:
        raise HTTPException(404, public_error(AppError("PROJECT_NOT_FOUND", "ไม่พบโปรเจกต์"))) from exc
    return {"jobId": job_id, **result}

@router.get("/youtube/connections")
def youtube_connections(request: Request) -> dict:
    return {"configured": request.app.state.youtube_service.configured(), "connections": request.app.state.persistence.youtube_connections()}

@router.get("/youtube/connect")
def youtube_connect(request: Request):
    from fastapi.responses import RedirectResponse
    try: return RedirectResponse(request.app.state.youtube_service.auth_url())
    except AppError as exc: raise HTTPException(400, public_error(exc))

@router.get("/youtube/callback")
def youtube_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    from fastapi.responses import RedirectResponse
    if error: return RedirectResponse("/history?youtube=denied")
    try:
        request.app.state.youtube_service.callback(code or "", state or ""); return RedirectResponse("/history?youtube=connected")
    except AppError as exc: return RedirectResponse("/history?youtube=error")

@router.delete("/youtube/connections/{connection_id}")
def youtube_delete(request: Request, connection_id: str) -> dict:
    if not request.app.state.persistence.delete_youtube_connection(connection_id): raise HTTPException(404, detail="YouTube connection not found")
    return {"status":"DELETED"}

@router.post("/history/{history_id}/youtube/upload")
def youtube_upload(request: Request, history_id: str, body: YouTubeUploadRequest) -> dict:
    item=next((p for p in request.app.state.persistence.history() if p["id"]==history_id),None)
    if not item or not item.get("latestJob") or not item["latestJob"].get("videoAvailable"): raise HTTPException(400, public_error(AppError("VIDEO_NOT_READY", "ยังไม่มีวิดีโอที่สร้างเสร็จ")))
    job=request.app.state.persistence.get_job(item["latestJob"]["id"]); path=Path(job["final_path"])
    try:
        result = request.app.state.youtube_service.upload(body.connectionId,path,body.title,body.description,body.tags,body.privacyStatus)
        request.app.state.persistence.set_published(history_id, True)
        return result
    except AppError as exc: raise HTTPException(400, public_error(exc))


@router.get("/storage")
def storage(request: Request) -> dict:
    return request.app.state.cleanup_service.storage()


@router.post("/storage/cleanup")
def cleanup(request: Request) -> dict:
    return request.app.state.cleanup_service.clean()


@router.get("/trash")
def trash(request: Request) -> dict:
    return {"projects": request.app.state.persistence.list_trashed()}


@router.delete("/ai/projects/{project_id}")
def trash_project(request: Request, project_id: str) -> dict:
    from app.domain.events import local_now
    try:
        if not request.app.state.persistence.project_exists(project_id):
            raise AppError("PROJECT_NOT_FOUND", "ไม่พบโปรเจกต์")
        request.app.state.persistence.mark_trash(project_id, local_now().isoformat())
        return {"status": "TRASHED", "projectId": project_id}
    except AppError as exc:
        raise HTTPException(404, public_error(exc)) from exc


@router.post("/ai/projects/{project_id}/duplicate")
def duplicate_project(request: Request, project_id: str) -> dict:
    try:
        return request.app.state.ai_project_service.duplicate(project_id).model_dump(mode="json")
    except AppError as exc:
        raise HTTPException(404, public_error(exc)) from exc


@router.post("/ai/projects/{project_id}/keep")
def keep_project(request: Request, project_id: str, keep: bool = True) -> dict:
    try:
        request.app.state.ai_project_service.get(project_id)
        with request.app.state.persistence._connect() as db:
            db.execute("UPDATE projects SET keep_flag=? WHERE id=?", (1 if keep else 0, project_id))
        return {"projectId": project_id, "keep": keep}
    except AppError as exc:
        raise HTTPException(404, public_error(exc)) from exc


@router.post("/trash/{project_id}/restore")
def restore_project(request: Request, project_id: str) -> dict:
    try:
        rows = request.app.state.persistence.list_trashed()
        if not any(r["id"] == project_id for r in rows):
            raise AppError("PROJECT_NOT_FOUND", "ไม่พบโปรเจกต์ในถังขยะ")
        request.app.state.persistence.mark_trash(project_id, None)
        return {"status": "RESTORED", "projectId": project_id}
    except Exception as exc:
        raise HTTPException(404, public_error(AppError("PROJECT_NOT_FOUND", "ไม่พบโปรเจกต์"))) from exc


@router.delete("/trash/{project_id}/permanent")
def delete_project_permanently(request: Request, project_id: str) -> dict:
    persistence = request.app.state.persistence
    if not any(r["id"] == project_id for r in persistence.list_trashed()):
        raise HTTPException(404, public_error(AppError("PROJECT_NOT_FOUND", "ไม่พบโปรเจกต์ในถังขยะ")))
    root = request.app.state.settings.app.workspace.resolve()
    import shutil
    candidates = [persistence_path for persistence_path in [root / "ai-projects" / project_id] if persistence_path.exists()]
    candidates += [Path(p) for p in persistence.project_job_paths(project_id)]
    for target in candidates:
        resolved = target.resolve()
        if root not in resolved.parents and resolved != root:
            raise HTTPException(400, public_error(AppError("ZIP_SECURITY_VIOLATION", "ไม่สามารถลบ path นอก workspace")))
        if target.is_symlink():
            raise HTTPException(400, public_error(AppError("ZIP_SECURITY_VIOLATION", "ไม่สามารถลบ symlink")))
        if target.is_dir(): shutil.rmtree(target)
        elif target.exists(): target.unlink()
    persistence.delete_project(project_id)
    return {"status": "DELETED", "projectId": project_id}


@router.post("/ai/projects")
def create_ai_project(request: Request, topic: str = "") -> dict:
    try:
        return request.app.state.ai_project_service.create(topic).model_dump(mode="json")
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.post("/ai/projects/automatic")
def create_automatic_ai_project(request: Request, body: AiAutomaticRequest) -> dict:
    """Start the no-chat topic-to-ZIP workflow and return immediately.

    The browser polls the project resource for the live, persisted progress log.
    """
    try:
        return request.app.state.ai_project_service.create_automatic(body.topic, body.concept, body.channel_id).model_dump(mode="json")
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc
    except KeyError as exc:
        raise HTTPException(400, public_error(AppError("CHANNEL_NOT_FOUND", "ไม่พบ Channel ที่เลือก"))) from exc


@router.get("/ai/projects")
def list_ai_projects(request: Request) -> dict:
    return {"projects": request.app.state.persistence.list_projects()}


@router.get("/ai/projects/{project_id}")
def get_ai_project(request: Request, project_id: str) -> dict:
    try:
        return request.app.state.ai_project_service.get(project_id).model_dump(mode="json")
    except AppError as exc:
        raise HTTPException(404 if exc.code == "AI_PROJECT_NOT_FOUND" else 400, public_error(exc)) from exc


@router.post("/ai/projects/{project_id}/messages")
def ai_message(request: Request, project_id: str, body: AiMessageRequest) -> dict:
    try:
        return request.app.state.ai_project_service.message(project_id, body.content).model_dump(mode="json")
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.post("/ai/projects/{project_id}/preview")
def ai_preview(request: Request, project_id: str) -> dict:
    try:
        return request.app.state.ai_project_service.create_preview(project_id).model_dump(mode="json")
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.patch("/ai/projects/{project_id}/scenes/{scene_id}")
def ai_update_scene(request: Request, project_id: str, scene_id: str, body: AiSceneUpdate) -> dict:
    try:
        return request.app.state.ai_project_service.update_scene(project_id, scene_id, body.model_dump(exclude_none=True)).model_dump(mode="json")
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.post("/ai/projects/{project_id}/scenes/{scene_id}/regenerate-image")
def ai_regenerate_image(request: Request, project_id: str, scene_id: str) -> dict:
    try:
        return request.app.state.ai_project_service.regenerate_image(project_id, scene_id).model_dump(mode="json")
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.post("/ai/projects/{project_id}/generate-images")
def ai_generate_images(request: Request, project_id: str) -> dict:
    try:
        return request.app.state.ai_project_service.start_image_generation(project_id).model_dump(mode="json")
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.post("/ai/projects/{project_id}/confirm")
def ai_confirm(request: Request, project_id: str) -> dict:
    try:
        return request.app.state.ai_project_service.confirm(project_id).model_dump(mode="json")
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.post("/ai/projects/{project_id}/approve-and-package")
def ai_approve_and_package(request: Request, project_id: str) -> dict:
    try:
        path = request.app.state.ai_project_service.approve_and_build_package(project_id)
        return {"projectId": project_id, "packageUrl": f"/api/ai/projects/{project_id}/package", "filename": path.name}
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


def _build_ai_package(request: Request, project_id: str, generate: bool) -> dict:
    try:
        path = request.app.state.ai_project_service.build_package(project_id)
        result = {"projectId": project_id, "packageUrl": f"/api/ai/projects/{project_id}/package", "filename": path.name}
        if generate:
            project = request.app.state.ai_project_service.get(project_id)
            record = request.app.state.job_service.submit_path(path, channel_id=project.channel_id)
            result.update({"jobId": record.job_id, "status": record.status})
        return result
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


@router.post("/ai/projects/{project_id}/package")
def ai_package(request: Request, project_id: str) -> dict:
    return _build_ai_package(request, project_id, False)


@router.post("/ai/projects/{project_id}/package-and-generate")
def ai_package_generate(request: Request, project_id: str) -> dict:
    return _build_ai_package(request, project_id, True)


@router.get("/ai/projects/{project_id}/package")
def ai_download_package(request: Request, project_id: str) -> FileResponse:
    try:
        project = request.app.state.ai_project_service.get(project_id)
        if not project.package_versions:
            raise AppError("PACKAGE_NOT_READY", "ยังไม่มี ZIP ที่สร้างเสร็จ")
        path = request.app.state.ai_project_service.root / project_id / project.package_versions[-1]
        return FileResponse(path, media_type="application/zip", filename=path.name)
    except AppError as exc:
        raise HTTPException(404 if exc.code == "AI_PROJECT_NOT_FOUND" else 409, public_error(exc)) from exc


@router.get("/ai/projects/{project_id}/assets/{asset_path:path}")
def ai_asset(request: Request, project_id: str, asset_path: str) -> FileResponse:
    try:
        project = request.app.state.ai_project_service.get(project_id)
        root = (request.app.state.ai_project_service.root / project_id).resolve()
        path = (root / asset_path).resolve()
        if root not in path.parents or not path.is_file():
            raise AppError("ASSET_NOT_FOUND", "ไม่พบภาพตัวอย่าง")
        return FileResponse(path)
    except AppError as exc:
        raise HTTPException(404, public_error(exc)) from exc
