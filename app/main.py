from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import load_settings
from app.api.routes import router
from app.infrastructure.ffmpeg import FfmpegRunner, FfprobeRunner
from app.infrastructure.tts.providers import LocalThaiTtsProvider
from app.services.job_service import JobService
from app.services.tts_preview_service import TtsPreviewService
from app.services.ai_service import AiProjectService
from app.services.persistence import Persistence
from app.services.cleanup_service import CleanupService
from app.services.youtube_service import YouTubeService


def create_app() -> FastAPI:
    settings = load_settings()
    application = FastAPI(title="AutoClip")
    application.state.settings = settings
    application.state.ffmpeg = FfmpegRunner()
    application.state.ffprobe = FfprobeRunner()
    settings.app.workspace.mkdir(parents=True, exist_ok=True)
    application.state.persistence = Persistence(settings.app.workspace)
    application.state.youtube_service = YouTubeService(settings, application.state.persistence)
    application.state.persistence.mark_interrupted_jobs()
    application.state.cleanup_service = CleanupService(settings.app.workspace, application.state.persistence)
    application.state.job_service = JobService(settings, persistence=application.state.persistence)
    application.state.ai_project_service = AiProjectService(settings, persistence=application.state.persistence)
    application.state.tts_preview_service = TtsPreviewService(settings.app.workspace, LocalThaiTtsProvider(), settings)
    application.include_router(router)
    static_dir = Path(__file__).parent / "web" / "static"
    application.mount("/static", StaticFiles(directory=static_dir), name="static")

    @application.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @application.get("/tts", include_in_schema=False)
    def tts_page() -> FileResponse:
        return FileResponse(static_dir / "tts.html", headers={"Cache-Control": "no-store"})

    @application.get("/ai", include_in_schema=False)
    def ai_page() -> FileResponse:
        return FileResponse(static_dir / "ai.html")

    @application.get("/history", include_in_schema=False)
    def history_page() -> FileResponse:
        return FileResponse(static_dir / "history.html")

    @application.get("/jobs/{job_id}", include_in_schema=False)
    def progress_page(job_id: str) -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @application.get("/jobs/{job_id}/preview", include_in_schema=False)
    def preview_page(job_id: str) -> FileResponse:
        return FileResponse(static_dir / "preview.html")

    @application.get("/health")
    def health() -> dict[str, object]:
        ffmpeg = application.state.ffmpeg.available
        ffprobe = application.state.ffprobe.available
        return {"status": "UP" if ffmpeg and ffprobe else "DOWN", "ffmpeg": ffmpeg, "ffprobe": ffprobe}

    return application


app = create_app()
