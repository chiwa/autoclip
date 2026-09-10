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
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr("app.services.podcast_audio_service.time.sleep", lambda _: None)
        output_audio, durations, total_duration = service.synthesize_and_stitch(
            "job-retry-1", tmp_path, chunks, FlakyProvider(), "Enceladus", 0.95
        )

    assert attempts == 2
    assert output_audio.is_file()


def test_podcast_audio_retry_waits_at_least_five_seconds(tmp_path):
    settings = Settings()
    settings.podcast.max_retries = 1
    service = PodcastAudioService(FfmpegRunner(), FfprobeRunner(), settings)
    dummy = DummyTtsProvider()
    attempts = 0
    waits = []

    class RateLimitedProvider:
        def synthesize(self, text, lang, voice, speed, output_path):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise AppError("TTS_GENERATION_FAILED", "rate limited", {"retryable": True, "retryAfterSeconds": 2})
            dummy.synthesize(text, lang, voice, speed, output_path)

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr("app.services.podcast_audio_service.time.sleep", waits.append)
        service.synthesize_and_stitch("retry-five", tmp_path, ["retry me"], RateLimitedProvider(), "Enceladus", 1.0)

    assert attempts == 2
    assert waits == [5.0]


def test_podcast_audio_does_not_retry_nonretryable_error(tmp_path):
    settings = Settings()
    service = PodcastAudioService(FfmpegRunner(), FfprobeRunner(), settings)
    attempts = 0

    class BadRequestProvider:
        def synthesize(self, text, lang, voice, speed, output_path):
            nonlocal attempts
            attempts += 1
            raise AppError("TTS_GENERATION_FAILED", "bad request", {"status": 400, "retryable": False})

    with pytest.raises(AppError):
        service.synthesize_and_stitch("no-retry", tmp_path, ["bad"], BadRequestProvider(), "Enceladus", 1.0)
    assert attempts == 1


def test_targeted_retry_reuses_successful_chunks(tmp_path):
    settings = Settings()
    settings.podcast.max_retries = 1
    service = PodcastAudioService(FfmpegRunner(), FfprobeRunner(), settings)
    dummy = DummyTtsProvider()
    first_calls = []

    class PartiallyFailingProvider:
        def synthesize(self, text, lang, voice, speed, output_path):
            first_calls.append(text)
            if text == "failed chunk":
                raise AppError("TTS_GENERATION_FAILED", "temporary", {"retryable": True})
            dummy.synthesize(text, lang, voice, speed, output_path)

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr("app.services.podcast_audio_service.time.sleep", lambda _: None)
        with pytest.raises(AppError) as exc_info:
            service.synthesize_and_stitch(
                "targeted-retry",
                tmp_path,
                ["successful chunk", "failed chunk"],
                PartiallyFailingProvider(),
                "Enceladus",
                1.0,
            )
    assert exc_info.value.details["failedChunkIndexes"] == [1]

    retry_calls = []

    class SuccessfulRetryProvider:
        def synthesize(self, text, lang, voice, speed, output_path):
            retry_calls.append(text)
            dummy.synthesize(text, lang, voice, speed, output_path)

    output, _, _ = service.synthesize_and_stitch(
        "targeted-retry",
        tmp_path,
        ["successful chunk", "failed chunk"],
        SuccessfulRetryProvider(),
        "Enceladus",
        1.0,
    )
    assert output.is_file()
    assert retry_calls == ["failed chunk"]


def _make_tone(ffmpeg, path, duration):
    ffmpeg.run(
        [
            "-y", "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}",
            "-c:a", "pcm_s16le", str(path),
        ],
        "TEST_AUDIO_FAILED",
    )


def test_conform_english_audio_pads_short_track(tmp_path):
    service = PodcastAudioService(FfmpegRunner(), FfprobeRunner(), Settings())
    source = tmp_path / "short.wav"
    output = tmp_path / "short-aligned.wav"
    _make_tone(service.ffmpeg, source, 0.6)

    _, duration = service.conform_to_video_duration(source, output, 1.0)

    assert output.is_file()
    assert abs(duration - 1.0) <= 0.1


def test_conform_english_audio_speeds_up_without_cutting(tmp_path):
    service = PodcastAudioService(FfmpegRunner(), FfprobeRunner(), Settings())
    source = tmp_path / "long.wav"
    output = tmp_path / "long-aligned.wav"
    _make_tone(service.ffmpeg, source, 1.2)

    _, duration = service.conform_to_video_duration(source, output, 1.0)

    assert output.is_file()
    assert abs(duration - 1.0) <= 0.1


def test_conform_english_audio_rejects_excessive_speedup(tmp_path):
    service = PodcastAudioService(FfmpegRunner(), FfprobeRunner(), Settings())
    source = tmp_path / "too-long.wav"
    _make_tone(service.ffmpeg, source, 1.4)

    with pytest.raises(AppError) as exc_info:
        service.conform_to_video_duration(source, tmp_path / "unused.wav", 1.0)

    assert exc_info.value.code == "ENGLISH_AUDIO_TOO_LONG"


def test_create_alternate_track_mixes_bgm_and_matches_video_duration(tmp_path):
    service = PodcastAudioService(FfmpegRunner(), FfprobeRunner(), Settings())
    narration = tmp_path / "narration.wav"
    bgm = tmp_path / "bgm.wav"
    output = tmp_path / "podcast-en.wav"
    _make_tone(service.ffmpeg, narration, 0.65)
    service.ffmpeg.run(
        [
            "-y", "-f", "lavfi", "-i", "sine=frequency=180:duration=0.4",
            "-c:a", "pcm_s16le", str(bgm),
        ],
        "TEST_AUDIO_FAILED",
    )

    _, duration = service.create_alternate_track(
        narration,
        output,
        1.0,
        bgm_path=bgm,
        bgm_volume=0.08,
    )

    assert output.is_file()
    assert abs(duration - 1.0) <= 0.1
    probe = service.ffprobe.probe(output)
    audio_stream = next(stream for stream in probe["streams"] if stream.get("codec_type") == "audio")
    assert audio_stream["codec_name"] == "pcm_s16le"
    assert int(audio_stream["sample_rate"]) == 48000
    assert audio_stream["channels"] == 2
    assert not list(tmp_path.glob(".*.tmp.wav"))


def test_create_alternate_track_without_bgm_keeps_aligned_narration(tmp_path):
    service = PodcastAudioService(FfmpegRunner(), FfprobeRunner(), Settings())
    narration = tmp_path / "narration.wav"
    output = tmp_path / "podcast-en.wav"
    _make_tone(service.ffmpeg, narration, 0.6)

    _, duration = service.create_alternate_track(narration, output, 1.0)

    assert output.is_file()
    assert abs(duration - 1.0) <= 0.1


def test_create_alternate_track_appends_complete_ending_after_duration_matching(tmp_path):
    service = PodcastAudioService(FfmpegRunner(), FfprobeRunner(), Settings())
    narration = tmp_path / "narration.wav"
    ending = tmp_path / "ending.wav"
    output = tmp_path / "podcast-en.wav"
    _make_tone(service.ffmpeg, narration, 0.6)
    _make_tone(service.ffmpeg, ending, 0.45)

    _, duration = service.create_alternate_track(
        narration,
        output,
        1.0,
        ending_song_path=ending,
        ending_song_duration=service.ffprobe.duration(ending),
    )

    assert abs(duration - 1.45) <= 0.12
    assert service.ffprobe.duration(output) > 1.35


def test_create_alternate_track_disabled_keeps_previous_duration(tmp_path):
    service = PodcastAudioService(FfmpegRunner(), FfprobeRunner(), Settings())
    narration = tmp_path / "narration.wav"
    output = tmp_path / "podcast-en.wav"
    _make_tone(service.ffmpeg, narration, 0.6)

    _, duration = service.create_alternate_track(narration, output, 1.0)

    assert abs(duration - 1.0) <= 0.1
