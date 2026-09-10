from __future__ import annotations

import os
from pathlib import Path

from app.config.settings import Settings
from app.domain.errors import AppError
from app.infrastructure.ffmpeg import FfprobeRunner


def _resolve_asset(path: Path) -> Path:
    path = path.expanduser()
    return path if path.is_absolute() else Path(__file__).resolve().parents[2] / path


def resolve_podcast_ending_scene(settings: Settings, ffprobe: FfprobeRunner) -> tuple[Path | None, Path | None, float]:
    config = settings.podcast.ending_scene
    if not config.enabled:
        return None, None, 0.0
    image = _resolve_asset(config.image)
    song = _resolve_asset(config.song)
    if not image.is_file() or not os.access(image, os.R_OK):
        raise AppError(
            "PODCAST_ENDING_IMAGE_MISSING",
            f"เปิดใช้ฉากจบ Podcast แต่ไม่พบหรืออ่านภาพไม่ได้: {image}",
        )
    if not song.is_file() or not os.access(song, os.R_OK):
        raise AppError("PODCAST_ENDING_SONG_MISSING", f"เปิดใช้ฉากจบ Podcast แต่ไม่พบหรืออ่านเพลงไม่ได้: {song}")
    try:
        duration = ffprobe.duration(song)
        probe = ffprobe.probe(image)
        if not any(stream.get("codec_type") == "video" for stream in probe.get("streams", [])):
            raise ValueError("ending image has no decodable video stream")
        from PIL import Image
        with Image.open(image) as opened:
            opened.verify()
    except Exception as exc:
        raise AppError("PODCAST_ENDING_SCENE_INVALID", "ภาพหรือเพลงของฉากจบ Podcast ใช้งานไม่ได้") from exc
    if duration <= 0:
        raise AppError("PODCAST_ENDING_SONG_INVALID", "ไฟล์เพลงจบ Podcast ไม่มีความยาวเสียงที่ใช้งานได้")
    return image, song, duration
