from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from app.domain.ai_models import AiScene


_OPENING_BLOCKLIST = (
    "สวัสดี",
    "ยินดีต้อนรับ",
    "วันนี้เราจะ",
    "วันนี้เรามา",
    "วันนี้ Mamase",
    "วันนี้มามาเซ่",
    "ในคลิปนี้",
    "คลิปนี้เราจะ",
    "ก่อนอื่น",
    "มาเริ่มกัน",
    "รู้หรือไม่",
)
_CURIOSITY_SIGNALS = (
    "?", "？", "ทำไม", "ได้ยังไง", "รู้ได้ยังไง", "จริงไหม", "จริงหรือ",
    "เกิดอะไร", "จะเกิดอะไร", "หรือว่า", "แต่", "ทั้งที่", "กลับ", "กว่า",
    "ไม่มีอะไร", "แปลก", "เป็นไปได้", "ถ้า", "เท่าไร", "แค่ไหน",
)
_UNSUPPORTED_CERTAINTY = ("ยืนยันแล้ว", "พิสูจน์แล้ว", "แน่นอนว่า", "พบเอเลียนแล้ว")
_UNCERTAINTY_MARKERS = ("อาจ", "เป็นไปได้", "เบาะแส", "ยังไม่", "หรือไม่", "?")
_GENERIC_VISUALS = (
    "generic stars", "generic starfield", "generic galaxy", "slow logo",
    "logo animation", "plain starfield", "อวกาศทั่วไป", "ท้องฟ้าทั่วไป",
)
_CTA_WORDS = (
    "กดไลก์", "กดแชร์", "กดติดตาม", "ฝากติดตาม", "อย่าลืมติดตาม",
    "คอมเมนต์คุยกัน", "อย่าลืมคอมเมนต์", "ขอบคุณที่รับชม",
)


@dataclass(frozen=True)
class HookGateCheck:
    number: int
    name: str
    passed: bool
    message: str


@dataclass(frozen=True)
class HookGateResult:
    passed: bool
    checks: tuple[HookGateCheck, ...]

    @property
    def issues(self) -> list[str]:
        return [check.message for check in self.checks if not check.passed]

    def as_dict(self) -> dict:
        return {"passed": self.passed, "checks": [asdict(check) for check in self.checks], "issues": self.issues}


class MamaseReelHookGate:
    """Fast deterministic preflight for the structural parts of the Reel hook rules.

    This intentionally does not claim to fact-check arbitrary science. It flags
    unsupported certainty and leaves final factual review visible as a required
    editorial responsibility.
    """

    def __init__(self, max_hook_characters: int = 120):
        self.max_hook_characters = max_hook_characters

    def evaluate(self, scenes: list[AiScene]) -> HookGateResult:
        content = [scene for scene in scenes if not scene.id.endswith("brand-outro")]
        if not content:
            failed = HookGateCheck(1, "hook_timing", False, "ยังไม่มีซีนเนื้อหาสำหรับตรวจ Hook")
            return HookGateResult(False, (failed,))

        first = content[0]
        spoken = (first.tts_text or first.narration).strip()
        hook = self._first_idea(spoken)
        lower_spoken = spoken.casefold()
        prompt = first.image_prompt.strip().casefold()
        starts_with_setup = any(lower_spoken.startswith(value.casefold()) for value in _OPENING_BLOCKLIST)
        has_curiosity = any(signal.casefold() in hook.casefold() for signal in _CURIOSITY_SIGNALS)
        misleading = any(claim in spoken for claim in _UNSUPPORTED_CERTAINTY) and not any(
            marker in spoken for marker in _UNCERTAINTY_MARKERS
        )
        visual_is_specific = len(prompt) >= 40 and not any(value in prompt for value in _GENERIC_VISUALS)
        no_filler = not any(
            phrase in scene.narration.casefold()
            for scene in content
            for phrase in ("วันนี้เราจะมาพูดถึง", "ในคลิปนี้เราจะมาเรียนรู้", "ก่อนอื่นเรามาทำความรู้จัก")
        )
        unique_beats = len({self._normalise(scene.narration) for scene in content}) == len(content)
        last = content[-1].narration.strip()
        ending_has_generic_cta = bool(last) and any(word in last for word in _CTA_WORDS)
        tts_matches = self._normalise(first.tts_text or first.narration).startswith(
            self._normalise(first.narration)[:18]
        )

        checks = (
            HookGateCheck(1, "hook_timing", bool(hook) and len(hook) <= self.max_hook_characters,
                          f"Hook ต้องเข้าใจได้ภายใน 1–3 วินาที (ช่วงเปิดปัจจุบันยาว {len(hook)} ตัวอักษร)"),
            HookGateCheck(2, "no_setup", not starts_with_setup,
                          "ตัดคำทักทาย แนะนำช่อง หรือ setup ก่อน Hook ออก"),
            HookGateCheck(3, "general_audience", bool(hook) and len(hook) <= self.max_hook_characters,
                          "ย่อ Hook ให้เป็นคำถามหรือข้อเท็จจริงง่าย ๆ ที่คนทั่วไปเข้าใจทันที"),
            HookGateCheck(4, "curiosity_gap", has_curiosity,
                          "Hook ยังไม่มีคำถาม ความขัดแย้ง ผลลัพธ์คาดไม่ถึง หรือช่องว่างความอยากรู้"),
            HookGateCheck(5, "scientific_accuracy", not misleading,
                          "Hook ใช้ถ้อยคำยืนยันเกินหลักฐาน ให้ระบุความไม่แน่นอนอย่างตรงไปตรงมา"),
            HookGateCheck(6, "visual_reinforcement", visual_is_specific,
                          "Image prompt ซีนแรกต้องสื่อปริศนาของ Hook โดยตรง ไม่ใช่ดาวหรือโลโก้ทั่วไป"),
            HookGateCheck(7, "no_filler", no_filler,
                          "พบบทเกริ่นหรือ filler ที่ไม่พาเรื่องเดินหน้า"),
            HookGateCheck(8, "continuous_payoff", unique_beats and all(len(s.narration.strip()) >= 8 for s in content),
                          "แต่ละซีนต้องมีข้อมูลหรือ payoff ใหม่ ห้ามใช้บทซ้ำหรือซีนที่แทบไม่มีสาระ"),
            HookGateCheck(9, "strong_ending", bool(last) and not ending_has_generic_cta,
                          "ตอนจบต้องไม่ใช้ generic CTA (เช่น กดไลก์, กดติดตาม, คอมเมนต์, ขอบคุณที่รับชม) ให้จบด้วยคำถามชวนคิดเฉพาะเรื่องหรือ Twist ที่จำได้"),
            HookGateCheck(10, "tts_starts_with_hook", tts_matches and not starts_with_setup,
                          "TTS ซีนแรกต้องเริ่มตรงกับ Hook โดยไม่มี branding หรือคำเกริ่นนำ"),
        )
        return HookGateResult(all(check.passed for check in checks), checks)

    @staticmethod
    def _first_idea(text: str) -> str:
        parts = re.split(r"(?<=[?？!！。])|\n|(?<=[.])\s+", text, maxsplit=1)
        return (parts[0] if parts else text).strip()

    @staticmethod
    def _normalise(text: str) -> str:
        return re.sub(r"[^0-9A-Za-zก-๙]+", "", text).casefold()
