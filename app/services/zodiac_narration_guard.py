from __future__ import annotations

import re
import unicodedata

from app.domain.errors import AppError


class ZodiacNarrationGuard:
    """Guarantee that zodiac TTS receives only the scene's final narration."""

    STYLE_FRAGMENTS = (
        "read aloud",
        "slightly mysterious",
        "reassuring",
        "trusted person",
        "weekly insight",
        "news anchor",
        "advertisement",
        "speed:",
        "language:",
    )

    @staticmethod
    def normalize(text: str) -> str:
        text = unicodedata.normalize("NFKC", text or "")
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def provider_text(cls, scene, pronunciation) -> str:
        final_text = cls.normalize(scene.tts_text or scene.narration)
        if not final_text:
            raise AppError("ZODIAC_NARRATION_EMPTY", "ไม่พบบทพูดสุดท้ายของราศี")
        cls.reject_style_leak(final_text)

        # Pronunciation replacement is the only permitted transformation.
        # No global intro, brand line, outro, or CTA is concatenated here.
        expected = cls.normalize(pronunciation.normalize(final_text))
        provider_text = expected
        if cls.normalize(provider_text) != expected:
            raise AppError("ZODIAC_NARRATION_MISMATCH", "บทที่กำลังส่ง TTS มีข้อความนอกเหนือจากบทสุดท้าย")
        return provider_text

    @classmethod
    def reject_style_leak(cls, final_text: str) -> None:
        normalized = cls.normalize(final_text).casefold()
        leaked = [fragment for fragment in cls.STYLE_FRAGMENTS if fragment in normalized]
        if leaked:
            raise AppError(
                "ZODIAC_TTS_STYLE_LEAK",
                "บทพูดมีข้อความจาก TTS style ปะปน ระบบจึงหยุดก่อนส่งไป Gemini",
                {"fragments": leaked},
            )

    @classmethod
    def verify_provider_text(cls, final_text: str, provider_text: str, pronunciation) -> None:
        cls.reject_style_leak(final_text)
        expected = cls.normalize(pronunciation.normalize(cls.normalize(final_text)))
        if cls.normalize(provider_text) != expected:
            raise AppError(
                "ZODIAC_NARRATION_MISMATCH",
                "ตรวจพบ intro, outro, CTA หรือข้อความอื่นที่ไม่ได้อยู่ในบทสุดท้ายก่อนส่ง TTS",
            )
