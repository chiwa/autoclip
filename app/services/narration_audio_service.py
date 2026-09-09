from __future__ import annotations

import uuid
from pathlib import Path

from app.config.settings import Settings
from app.domain.errors import AppError
from app.infrastructure.ffmpeg import FfmpegRunner, FfprobeRunner


class NarrationAudioProcessor:
    """Normalize narration timing after any TTS provider has written audio."""

    def __init__(self, ffmpeg: FfmpegRunner, ffprobe: FfprobeRunner, settings: Settings):
        self.ffmpeg = ffmpeg
        self.ffprobe = ffprobe
        self.settings = settings

    def silence_trim_filter(self) -> str:
        trim = self.settings.tts.silence_trim
        edge = f"{trim.retained_edge_seconds:.3f}"
        edge_ms = round(trim.retained_edge_seconds * 1000)
        minimum = f"{trim.minimum_silence_seconds:.3f}"
        threshold = f"{trim.threshold_db:g}dB"
        leading = (
            "silenceremove="
            "start_periods=1:start_duration=0:"
            f"start_threshold={threshold}:window={minimum}"
        )
        # Only start_periods is used. Reversing the samples lets the same
        # leading-edge operation trim the original tail without ever enabling
        # stop_periods, which could remove pauses inside the narration.
        return (
            f"{leading},areverse,{leading},areverse,"
            f"adelay={edge_ms}:all=1,apad=pad_dur={edge},asetpts=N/SR/TB"
        )

    def process(self, audio_path: Path) -> float:
        """Trim enabled edge silence atomically, then measure final duration."""
        if not self.settings.tts.silence_trim.enabled:
            return self.ffprobe.duration(audio_path)

        temporary = audio_path.with_name(
            f".{audio_path.stem}.silence-trim-{uuid.uuid4().hex}{audio_path.suffix}"
        )
        try:
            self.ffmpeg.run(
                [
                    "-i",
                    str(audio_path),
                    "-af",
                    self.silence_trim_filter(),
                    "-c:a",
                    "pcm_s16le",
                    str(temporary),
                ],
                "TTS_AUDIO_TRIM_FAILED",
            )
            if not temporary.is_file() or temporary.stat().st_size <= 44:
                raise AppError(
                    "TTS_AUDIO_TRIM_FAILED",
                    "Trimmed narration audio is empty",
                )
            temporary.replace(audio_path)
        finally:
            temporary.unlink(missing_ok=True)
        return self.ffprobe.duration(audio_path)
