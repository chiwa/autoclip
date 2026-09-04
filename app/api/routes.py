import asyncio
import base64
import json
import queue
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.domain.enums import JobStatus
from app.domain.errors import AppError, public_error
from app.domain.events import JobEvent, JobEventType
from app.domain.ai_models import AiProject
from app.services.bgm_service import ensure_default_bgm

router = APIRouter(prefix="/api")


class AiMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)


class AiSceneUpdate(BaseModel):
    narration: str | None = None
    subtitle: str | None = None
    show_subtitle: bool | None = None
    image_prompt: str | None = None
    motion: str | None = None
    transition: str | None = None
    estimated_duration: float | None = None

class YouTubeUploadRequest(BaseModel):
    connectionId: str
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=5000)
    tags: list[str] = Field(default_factory=list, max_length=30)
    privacyStatus: str = "private"

class VideoMetadataRequest(BaseModel):
    title: str = Field(default="-", max_length=100)
    description: str = Field(default="-", max_length=10000)


@router.post("/tts")
def create_thai_speech(
    request: Request,
    text: str = Form(...),
    voice: str = Form("thai-male-01"),
    speed: float = Form(1.0),
    provider: str = Form("local"),
) -> FileResponse:
    try:
        path = request.app.state.tts_preview_service.synthesize(text, voice, speed, provider)
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


@router.post("/jobs", status_code=202)
def create_job(
    request: Request,
    file: UploadFile = File(...),
    tts_provider: str | None = Form(None),
    subtitle_mode: str | None = Form(None),
    render_engine: str | None = Form(None),
    output_format: str | None = Form(None),
    script_json: str | None = Form(None),
) -> dict:
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, public_error(AppError("PACKAGE_INVALID", "Exactly one ZIP file is required")))
    try:
        record = request.app.state.job_service.submit(file, tts_provider, subtitle_mode, script_json, render_engine, output_format)
    except AppError as exc:
        raise HTTPException(413 if exc.code == "UPLOAD_TOO_LARGE" else 400, public_error(exc)) from exc
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
    return (record.metadata or {}).get("videoMetadata", {"title": "-", "description": "-"})

@router.put("/jobs/{job_id}/video-metadata")
def save_video_metadata(request: Request, job_id: str, body: VideoMetadataRequest) -> dict:
    record = request.app.state.job_service.restore(job_id)
    if not record: raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "Job was not found")))
    metadata = dict(record.metadata or {}); title=body.title.strip() or "-"; description=body.description if body.description else "-"
    metadata["videoMetadata"]={"title":title,"description":description}
    request.app.state.job_service.set_metadata(job_id, metadata)
    if not request.app.state.persistence.update_job_metadata(job_id, metadata): raise HTTPException(404, public_error(AppError("JOB_NOT_FOUND", "Job was not found")))
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


@router.get("/ai/status")
def ai_status(request: Request) -> dict:
    return {"configured": request.app.state.ai_project_service.configured}


@router.get("/history")
def history(request: Request) -> dict:
    return {"projects": request.app.state.persistence.history()}

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
    try: return request.app.state.youtube_service.upload(body.connectionId,path,body.title,body.description,body.tags,body.privacyStatus)
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


@router.post("/ai/projects/{project_id}/confirm")
def ai_confirm(request: Request, project_id: str) -> dict:
    try:
        return request.app.state.ai_project_service.confirm(project_id).model_dump(mode="json")
    except AppError as exc:
        raise HTTPException(400, public_error(exc)) from exc


def _build_ai_package(request: Request, project_id: str, generate: bool) -> dict:
    try:
        path = request.app.state.ai_project_service.build_package(project_id)
        result = {"projectId": project_id, "packageUrl": f"/api/ai/projects/{project_id}/package", "filename": path.name}
        if generate:
            record = request.app.state.job_service.submit_path(path)
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
