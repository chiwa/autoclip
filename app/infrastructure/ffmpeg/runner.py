from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from app.domain.errors import AppError


class FfmpegRunner:
    def __init__(self, executable: str = "ffmpeg", timeout_seconds: int = 900):
        self.executable = executable
        self.timeout_seconds = timeout_seconds

    @property
    def available(self) -> bool:
        return shutil.which(self.executable) is not None

    def has_filter(self, name: str) -> bool:
        if not hasattr(self, "_filters"):
            try:
                result = subprocess.run([self.executable, "-filters"], capture_output=True, text=True, check=False)
                self._filters = set(line.split()[1] for line in result.stdout.splitlines() if len(line.split()) >= 2)
            except Exception:
                self._filters = set()
        return name in self._filters

    def run(self, args: list[str], error_code: str) -> None:
        try:
            result = subprocess.run(
                [self.executable, "-hide_banner", "-nostdin", "-y", *args],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise AppError(error_code, "Media processing command failed") from exc
        if result.returncode:
            raise AppError(error_code, "Media processing command failed", {"diagnostic": result.stderr[-2000:]})


class FfprobeRunner:
    def __init__(self, executable: str = "ffprobe", timeout_seconds: int = 60):
        self.executable = executable
        self.timeout_seconds = timeout_seconds

    @property
    def available(self) -> bool:
        return shutil.which(self.executable) is not None

    def probe(self, path: Path) -> dict:
        try:
            result = subprocess.run(
                [self.executable, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                capture_output=True, text=True, timeout=self.timeout_seconds, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise AppError("FFPROBE_FAILED", "Could not inspect generated media") from exc
        if result.returncode:
            raise AppError("FFPROBE_FAILED", "Could not inspect generated media")
        return json.loads(result.stdout)

    def duration(self, path: Path) -> float:
        try:
            return float(self.probe(path)["format"]["duration"])
        except (KeyError, TypeError, ValueError) as exc:
            raise AppError("FFPROBE_FAILED", "Media duration is unavailable") from exc

