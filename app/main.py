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
from app.services.zodiac_service import ZodiacWeeklyService
from app.services.zodiac_ephemeris_service import ZodiacEphemerisService
from app.services.zodiac_ai_service import ZodiacAiService
from app.services.quick_reel_service import QuickReelService


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
    application.state.zodiac_service = ZodiacWeeklyService(
        settings.app.workspace,
        assets_root=Path(__file__).resolve().parents[1] / "assets",
        job_service=application.state.job_service,
        persistence=application.state.persistence,
    )
    application.state.zodiac_ephemeris_service = ZodiacEphemerisService(settings.app.workspace)
    application.state.zodiac_ai_service = ZodiacAiService(
        settings, ephemeris_service=application.state.zodiac_ephemeris_service
    )
    application.state.quick_reel_service = QuickReelService(
        settings,
        ffmpeg=application.state.ffmpeg,
        ffprobe=application.state.ffprobe,
        job_service=application.state.job_service,
        persistence=application.state.persistence,
        assets_root=Path(__file__).resolve().parents[1] / "assets",
    )
    application.state.ai_project_service = AiProjectService(settings, persistence=application.state.persistence)
    application.state.tts_preview_service = TtsPreviewService(settings.app.workspace, LocalThaiTtsProvider(), settings)
    application.include_router(router)
    static_dir = Path(__file__).parent / "web" / "static"
    application.mount("/static", StaticFiles(directory=static_dir), name="static")
    assets_dir = Path(__file__).resolve().parents[1] / "assets"
    if assets_dir.is_dir():
        application.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @application.api_route("/favicon.ico", methods=["GET", "HEAD"], include_in_schema=False)
    def favicon() -> FileResponse:
        fav_path = assets_dir / "logo" / "auto-clip-logo.png"
        if fav_path.is_file():
            return FileResponse(fav_path, media_type="image/png")
        return FileResponse(static_dir / "index.html")

    @application.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @application.get("/tts", include_in_schema=False)
    def tts_page() -> FileResponse:
        return FileResponse(static_dir / "tts.html", headers={"Cache-Control": "no-store"})

    @application.get("/ai", include_in_schema=False)
    def ai_page() -> FileResponse:
        # The automatic package UI changes independently of media assets;
        # never leave a browser using an old download handler from cache.
        return FileResponse(static_dir / "ai.html", headers={"Cache-Control": "no-store"})

    @application.get("/podcast", include_in_schema=False)
    def podcast_page() -> FileResponse:
        return FileResponse(static_dir / "podcast.html", headers={"Cache-Control": "no-store"})

    @application.get("/quick-reel", include_in_schema=False)
    def quick_reel_page() -> FileResponse:
        return FileResponse(static_dir / "quick-reel.html", headers={"Cache-Control": "no-store"})

    @application.get("/channels", include_in_schema=False)
    def channels_page() -> FileResponse:
        return FileResponse(static_dir / "channels.html", headers={"Cache-Control": "no-store"})

    @application.get("/quick-reel-history", include_in_schema=False)
    def quick_reel_history_page() -> FileResponse:
        return FileResponse(static_dir / "history.html", headers={"Cache-Control": "no-store"})

    @application.get("/antigravity", include_in_schema=False)
    def antigravity_page() -> FileResponse:
        return FileResponse(static_dir / "antigravity.html", headers={"Cache-Control": "no-store"})

    @application.get("/history", include_in_schema=False)
    def history_page() -> FileResponse:
        return FileResponse(static_dir / "history.html")

    @application.get("/reels-history", include_in_schema=False)
    def reels_history_page() -> FileResponse:
        return FileResponse(static_dir / "history.html", headers={"Cache-Control": "no-store"})

    @application.get("/podcast-history", include_in_schema=False)
    def podcast_history_page() -> FileResponse:
        return FileResponse(static_dir / "history.html", headers={"Cache-Control": "no-store"})

    @application.get("/zodiac-weekly", include_in_schema=False)
    def zodiac_weekly_page() -> FileResponse:
        return FileResponse(static_dir / "zodiac-weekly.html", headers={"Cache-Control": "no-store"})

    @application.get("/zodiac-history", include_in_schema=False)
    def zodiac_history_page() -> FileResponse:
        return FileResponse(static_dir / "zodiac-history.html", headers={"Cache-Control": "no-store"})

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
