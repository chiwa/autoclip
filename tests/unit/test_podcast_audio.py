from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.config.settings import Settings
from app.domain.errors import AppError
from app.infrastructure.ffmpeg import FfmpegRunner, FfprobeRunner
from app.infrastructure.tts.providers import DummyTtsProvider
from app.services.podcast_audio_service import PodcastAudioService


def test_podcast_audio_synthesis_and_stitching(tmp_path):
    settings = Settings()
    ffmpeg = FfmpegRunner()
    ffprobe = FfprobeRunner()
    service = PodcastAudioService(ffmpeg, ffprobe, settings)
    provider = DummyTtsProvider()

    chunks = [
        "ตอนที่หนึ่ง เรื่องราวความเงียบสงบในอวกาศ",
        "ตอนที่สอง ดวงดาวที่ส่องประกายยามค่ำคืน",
        "ตอนที่สาม หลับตาและพักผ่อน",
    ]

    output_audio, durations, total_duration = service.synthesize_and_stitch(
        job_id="test-job-1",
        workspace_root=tmp_path,
        chunks=chunks,
        provider=provider,
        voice="Enceladus",
        speed=0.95,
    )

    assert output_audio.is_file()
    assert len(durations) == 3
    assert total_duration > 0
    assert abs(sum(durations) - total_duration) < 0.5


def test_podcast_audio_cache_reuse(tmp_path):
    settings = Settings()
    ffmpeg = FfmpegRunner()
    ffprobe = FfprobeRunner()
    service = PodcastAudioService(ffmpeg, ffprobe, settings)

    mock_provider = MagicMock()
    # First pass: synthesize creates valid audio using dummy provider
    dummy = DummyTtsProvider()

    def side_effect(text, lang, voice, speed, output_path):
        dummy.synthesize(text, lang, voice, speed, output_path)

    mock_provider.synthesize.side_effect = side_effect

    chunks = ["ข้อความที่หนึ่ง", "ข้อความที่สอง"]

    # First run
    service.synthesize_and_stitch("job-cache-1", tmp_path, chunks, mock_provider, "Enceladus", 0.95)
    assert mock_provider.synthesize.call_count == 2

    # Second run with same input and workspace
    mock_provider.synthesize.reset_mock()
    service.synthesize_and_stitch("job-cache-1", tmp_path, chunks, mock_provider, "Enceladus", 0.95)
    # Should reuse cached files, 0 new calls
    assert mock_provider.synthesize.call_count == 0


def test_podcast_audio_retry_logic(tmp_path):
    settings = Settings()
    settings.podcast.max_retries = 2
    ffmpeg = FfmpegRunner()
    ffprobe = FfprobeRunner()
    service = PodcastAudioService(ffmpeg, ffprobe, settings)

    dummy = DummyTtsProvider()
    attempts = 0

    class FlakyProvider:
        def synthesize(self, text, lang, voice, speed, output_path):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise RuntimeError("Transient network error")
            dummy.synthesize(text, lang, voice, speed, output_path)

    chunks = ["ข้อความทดสอบ retry"]
    output_audio, durations, total_duration = service.synthesize_and_stitch(
        "job-retry-1", tmp_path, chunks, FlakyProvider(), "Enceladus", 0.95
    )

    assert attempts == 2
    assert output_audio.is_file()
