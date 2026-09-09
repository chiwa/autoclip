from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.domain.errors import AppError
from app.infrastructure.tts.providers import TtsProvider, create_tts_provider


class TtsPreviewService:
    MAX_TEXT_LENGTH = 2_000

    def __init__(self, workspace: Path, provider: TtsProvider, settings=None):
        self.output_dir = workspace / "tts-previews"
        self.provider = provider
        self.settings = settings

    def synthesize(self, text: str, voice: str, speed: float, provider_name: str | None = None, style_prompt: str | None = None, language: str = "th-TH") -> Path:
        normalized = text.strip()
        if not normalized:
            raise AppError("TTS_GENERATION_FAILED", "กรุณาป้อนข้อความภาษาไทย")
        if len(normalized) > self.MAX_TEXT_LENGTH:
            raise AppError(
                "TTS_GENERATION_FAILED",
                f"ข้อความต้องไม่เกิน {self.MAX_TEXT_LENGTH:,} ตัวอักษร",
            )
        if not 0.5 <= speed <= 2.0:
            raise AppError("TTS_GENERATION_FAILED", "ความเร็วเสียงต้องอยู่ระหว่าง 0.5 ถึง 2.0")

        output_path = self.output_dir / f"{uuid4()}.wav"
        provider = self.provider
        if provider_name and provider_name != "local":
            if self.settings is None:
                raise AppError("TTS_GENERATION_FAILED", "ไม่สามารถตั้งค่าเสียงที่เลือกได้")
            provider = create_tts_provider(provider_name, self.settings)
        if style_prompt is not None and hasattr(provider, "style_prompt"):
            provider.style_prompt = style_prompt.strip() or None
        return provider.synthesize(normalized, language, voice, speed, output_path)
