from pathlib import Path

import pytest

from app.config.settings import Settings, load_settings
from app.domain.errors import AppError
from app.services.narration_audio_service import NarrationAudioProcessor


class RecordingFfmpeg:
    def __init__(self):
        self.calls: list[tuple[list[str], str]] = []

    def run(self, args: list[str], error_code: str) -> None:
        self.calls.append((args, error_code))
        Path(args[-1]).write_bytes(b"trimmed narration" * 4)


class RecordingFfprobe:
    def __init__(self):
        self.calls: list[Path] = []

    def duration(self, path: Path) -> float:
        self.calls.append(path)
        assert path.read_bytes() == b"trimmed narration" * 4
        return 1.75


def test_filter_trims_only_edges_and_preserves_internal_silence():
    processor = NarrationAudioProcessor(RecordingFfmpeg(), RecordingFfprobe(), Settings())

    audio_filter = processor.silence_trim_filter()

    assert audio_filter.count("silenceremove=") == 2
    assert audio_filter.count("start_periods=1") == 2
    assert audio_filter.count("start_duration=0") == 2
    assert audio_filter.count("window=0.100") == 2
    assert audio_filter.count("areverse") == 2
    assert "stop_periods" not in audio_filter
    assert "stop_duration" not in audio_filter
    assert "stop_threshold" not in audio_filter


def test_filter_uses_configured_retained_edge():
    settings = Settings()
    settings.tts.silence_trim.retained_edge_seconds = 0.08
    processor = NarrationAudioProcessor(RecordingFfmpeg(), RecordingFfprobe(), settings)

    audio_filter = processor.silence_trim_filter()
    assert "adelay=80:all=1" in audio_filter
    assert "apad=pad_dur=0.080" in audio_filter


def test_disabled_trimming_skips_ffmpeg(tmp_path):
    audio = tmp_path / "narration.wav"
    audio.write_bytes(b"original narration")
    ffmpeg = RecordingFfmpeg()

    class OriginalFfprobe:
        def duration(self, path: Path) -> float:
            assert path.read_bytes() == b"original narration"
            return 2.5

    settings = Settings()
    settings.tts.silence_trim.enabled = False
    duration = NarrationAudioProcessor(ffmpeg, OriginalFfprobe(), settings).process(audio)

    assert duration == 2.5
    assert ffmpeg.calls == []


def test_duration_is_measured_after_successful_trim_and_original_is_replaced(tmp_path):
    audio = tmp_path / "narration.wav"
    audio.write_bytes(b"original narration")
    ffmpeg = RecordingFfmpeg()
    ffprobe = RecordingFfprobe()

    settings = Settings()
    settings.tts.silence_trim.enabled = True
    duration = NarrationAudioProcessor(ffmpeg, ffprobe, settings).process(audio)

    assert duration == 1.75
    assert audio.read_bytes() == b"trimmed narration" * 4
    assert ffprobe.calls == [audio]
    assert ffmpeg.calls[0][1] == "TTS_AUDIO_TRIM_FAILED"
    assert not list(tmp_path.glob(".*.silence-trim-*"))


def test_failed_trim_preserves_original_audio(tmp_path):
    audio = tmp_path / "narration.wav"
    original = b"original narration remains intact"
    audio.write_bytes(original)

    class FailingFfmpeg:
        def run(self, args: list[str], error_code: str) -> None:
            Path(args[-1]).write_bytes(b"incomplete temporary output")
            raise AppError(error_code, "simulated failure")

    settings = Settings()
    settings.tts.silence_trim.enabled = True
    with pytest.raises(AppError, match="simulated failure"):
        NarrationAudioProcessor(FailingFfmpeg(), RecordingFfprobe(), settings).process(audio)

    assert audio.read_bytes() == original
    assert not list(tmp_path.glob(".*.silence-trim-*"))


def test_silence_trim_settings_read_from_dotenv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "AUTOCLIP_TTS_SILENCE_TRIM_ENABLED=false\n"
        "AUTOCLIP_TTS_SILENCE_THRESHOLD_DB=-42\n"
        "AUTOCLIP_TTS_MINIMUM_SILENCE_SECONDS=0.15\n"
        "AUTOCLIP_TTS_RETAINED_EDGE_SECONDS=0.08\n",
        encoding="utf-8",
    )

    settings = load_settings(tmp_path / "config.yaml")

    assert settings.tts.silence_trim.enabled is False
    assert settings.tts.silence_trim.threshold_db == -42
    assert settings.tts.silence_trim.minimum_silence_seconds == pytest.approx(0.15)
    assert settings.tts.silence_trim.retained_edge_seconds == pytest.approx(0.08)
