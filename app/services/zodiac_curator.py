from __future__ import annotations

import difflib
import logging
import re
from datetime import date

from app.domain.errors import AppError
from app.services.zodiac_service import ZODIACS, thai_week_range

logger = logging.getLogger(__name__)

HOOK_SIMILARITY_THRESHOLD: float = 0.80
HOOK_BODY_SIMILARITY_THRESHOLD: float = 0.75
HOOK_MAX_LENGTH: int = 120
HOOK_MIN_LENGTH: int = 28
MAX_SHARED_OPENING_PATTERN: int = 2
CURATOR_VERSION: str = "1.2.1"

CJK_REGEX = re.compile(r"[一-鿿㐀-䶿぀-ヿ가-힯]")

OPENING_BLOCKLIST = (
    "สวัสดี",
    "ยินดีต้อนรับ",
    "วันนี้เราจะ",
    "วันนี้เรามา",
    "ในคลิปนี้",
    "คลิปนี้เราจะ",
    "สำหรับชาว",
    "ชาวราศี",
    "ดวงชาว",
    "มาดูกัน",
)

CURIOSITY_MARKERS = (
    "?", "？", "อย่าเพิ่ง", "ไม่ควร", "ระวัง", "มีจังหวะ", "จังหวะ", "สิ่งสำคัญ", "สำคัญ",
    "โอกาสใหม่", "โอกาส", "ทางออก", "จุดเปลี่ยน", "แต่", "กลับ", "คำตอบ", "ความจริง",
    "เรื่องที่ไม่คาดคิด", "รายละเอียดเล็ก", "ถ้าคุณ", "มากกว่าที่คิด", "กำลังเข้ามา",
    "รอบคอบ", "ทบทวน", "น่าจับตา", "ความชัดเจน", "ชัดเจน", "พลิก", "ท้าทาย", "พลัง",
    "อย่าลังเล", "ตัดสินใจ", "ปลดล็อก",
)

SEMANTIC_CURIOSITY_MARKERS = (
    "คนอื่น", "ก่อนที่คุณจะ", "ก่อนจะรู้ตัว", "รู้ตัว", "มากกว่าที่วางแผน", "วางแผนไว้",
    "ถึงคิว", "ถูกจับตา", "จับตา", "สิ่งที่ซ่อน", "ซ่อนอยู่", "มองข้าม",
    "ความเปลี่ยนแปลง", "เปลี่ยนไป", "เห็นต่าง", "ไม่เหมือนเดิม", "คาดไม่ถึง",
    "บทเรียน", "ความลับ", "สิ่งที่ต้องเลือก", "สองทาง", "สัญญาณ", "ทดสอบ",
    "พิสูจน์", "เปิดเผย", "ไม่ทันตั้งตัว", "จังหวะซ่อน", "พลิกผัน",
    "สับสน", "ลังเล", "ไม่รู้จะ", "เลือกทาง", "หนักกว่าที่คิด", "รับไว้", "แบกรับ",
)

KNOWN_OPENING_STEMS = (
    "มีเรื่องสำคัญ",
    "มีเรื่อง",
    "มีจังหวะ",
    "มีโอกาส",
    "อย่าเพิ่ง",
    "ไม่ควร",
    "ยิ่ง",
    "ระวัง",
    "ความคิด",
    "สัญชาตญาณ",
    "คำพูด",
    "พลัง",
    "ผลงาน",
    "ทุกอย่าง",
    "อย่าลังเล",
    "เสน่ห์",
    "จุดเปลี่ยน",
    "ทางออก",
    "การตัดสินใจ",
    "ความรอบคอบ",
)

FILLERS = (
    "สัปดาห์นี้",
    "ช่วงนี้",
    "ในสัปดาห์นี้",
    "ระยะนี้",
    "สำหรับ",
    "ครับ",
    "ค่ะ",
    "นะครับ",
    "นะคะ",
)

POLITE_HOOK_ENDINGS_REGEX = re.compile(r"(?:ครับผม|นะครับ|นะคะ|ครับ|ค่ะ)[\s.!?…]*$")

ADVICE_OPENING_STEMS = (
    "พักผ่อน", "ดูแลตัวเอง", "ดูแลสุขภาพ", "รักษาสุขภาพ", "รักษาความสงบ",
    "ปล่อยวาง", "หลีกเลี่ยง", "อย่าลืม", "ควรหาเวลา", "หาเวลา", "ทำใจ",
    "ทำสมาธิ", "สวดมนต์", "ทำบุญ", "อดทน", "ระมัดระวังการใช้จ่าย",
    "ให้เวลากับตัวเอง", "ตั้งสติ", "เปิดใจรับฟัง", "ฝึกความอดทน",
)

CONTRAST_CONNECTORS = (
    "แต่ในขณะเดียวกันก็ต้อง",
    "แต่ในขณะเดียวกันก็",
    "แต่ในขณะเดียวกันต้อง",
    "แต่ในขณะเดียวกัน",
    "ในขณะเดียวกันก็",
    "ในขณะเดียวกัน",
    "แต่ถ้า",
    "แต่ต้อง",
    "แต่กลับ",
    "แต่",
    "ทว่า",
)

ASTRO_TERMS_HOOK_REGEX = re.compile(
    r"ดาว[ก-๙]+|เรือน(?:ภพ|ที่|[ก-๙]+)|ทำมุม|จตุโกณ|โยค|เล็ง|ตรีโกณ|กุมลัคน์|ถอยหลัง|ย้ายราศี|องศา"
)

STRONG_HOOK_TEMPLATES: dict[str, str] = {
    "capricorn": "ราศีมังกร สัปดาห์นี้มีเรื่องสำคัญที่อย่าเพิ่งรีบตัดสินใจ เพราะคำตอบที่ดีที่สุดอาจมาช้ากว่าที่คิด",
    "aquarius": "ราศีกุมภ์ สัปดาห์นี้ความคิดแปลกใหม่อาจสร้างโอกาสใหญ่ แต่ต้องเลือกคนที่ไว้ใจได้ร่วมทาง",
    "pisces": "ราศีมีน สัปดาห์นี้สัญชาตญาณคุณแม่นยำมาก แต่เรื่องเงินและข้อตกลงต้องดูหลักฐานจริงเป็นหลัก",
    "aries": "ราศีเมษ สัปดาห์นี้ยิ่งใจร้อนยิ่งสะดุด ชะลอจังหวะลงนิดเดียวจะเห็นทางออกที่ง่ายกว่าเดิม",
    "taurus": "ราศีพฤษภ สัปดาห์นี้มีโอกาสทางการเงินเข้ามา แต่ต้องระวังอย่าให้ความเกรงใจทำให้เสียเปรียบ",
    "gemini": "ราศีเมถุน สัปดาห์นี้คำพูดของคุณมีพลังสูงมาก เลือกสื่อสารให้ถูกจังหวะแล้วทุกอย่างจะราบรื่น",
    "cancer": "ราศีกรกฎ สัปดาห์นี้มีพลังผลักดันเรื่องงานเต็มที่ แต่สิ่งสำคัญคืออย่าแบกปัญหาของคนอื่นไว้คนเดียว",
    "leo": "ราศีสิงห์ สัปดาห์นี้ผลงานเด่นชัดเป็นที่ยอมรับ แต่ต้องรักษาความสัมพันธ์กับคนรอบข้างให้เหนียวแน่น",
    "virgo": "ราศีกันย์ สัปดาห์นี้ทุกอย่างอยู่ในสายตาคุณ รายละเอียดเล็กๆ ที่คุณเห็นจะพาไปสู่ความสำเร็จ",
    "libra": "ราศีตุลย์ สัปดาห์นี้อย่าลังเลนานเกินไป การตัดสินใจที่ชัดเจนจะปลดล็อกเรื่องที่ค้างคามานาน",
    "scorpio": "ราศีพิจิก สัปดาห์นี้เสน่ห์และความเฉียบคมของคุณกลับมา ใช้ขับเคลื่อนเป้าหมายแล้วจะเห็นผลลัพธ์ชัดเจน",
    "sagittarius": "ราศีธนู สัปดาห์นี้โอกาสใหม่กำลังเปิดออก แต่ต้องวางแผนการเงินและภาระให้รัดกุมก่อนก้าวไปข้างหน้า",
}


class ZodiacCurator:
    """Validates, curates, and normalizes DeepSeek zodiac readings to locked publication standards."""

    HOOK_SIMILARITY_THRESHOLD: float = HOOK_SIMILARITY_THRESHOLD
    HOOK_BODY_SIMILARITY_THRESHOLD: float = HOOK_BODY_SIMILARITY_THRESHOLD
    HOOK_MAX_LENGTH: int = HOOK_MAX_LENGTH
    HOOK_MIN_LENGTH: int = HOOK_MIN_LENGTH
    MAX_SHARED_OPENING_PATTERN: int = MAX_SHARED_OPENING_PATTERN
    CURATOR_VERSION: str = CURATOR_VERSION
    STRONG_HOOK_TEMPLATES = STRONG_HOOK_TEMPLATES

    ZODIAC_BY_ID = {z.id: z for z in ZODIACS}
    ORDERED_IDS = [z.id for z in ZODIACS]

    @classmethod
    def strip_hook_polite_ending(cls, hook: str) -> tuple[str, bool]:
        trimmed = POLITE_HOOK_ENDINGS_REGEX.sub("", hook.strip()).strip()
        changed = trimmed != hook.strip()
        return trimmed, changed

    @classmethod
    def is_merely_advice_hook(cls, hook: str, name_th: str = "") -> bool:
        """Detects whether a hook is merely passive advice without curiosity or tension."""
        s = hook.strip()
        prefix_pattern = rf"^ราศี(?:{re.escape(name_th)}|[ก-๙]+)?\s*(?:สัปดาห์นี้|ช่วงนี้)?\s*"
        s = re.sub(prefix_pattern, "", s).strip()

        has_contrast = any(w in s for w in ("แต่", "ทว่า", "ไม่ใช่", "มากกว่าที่", "หนักกว่าที่", "แทนที่จะ", "ความจริง"))
        if has_contrast:
            return False

        for stem in ADVICE_OPENING_STEMS:
            if s.startswith(stem) or f"ควร{stem}" in s or f"และ{stem}" in s:
                return True

        if s.startswith("ควร") or s.startswith("แนะนำให้") or s.startswith("เน้น"):
            return True

        return False

    @classmethod
    def normalize_hook(cls, hook: str, name_th: str = "") -> str:
        s = hook.strip()
        for bad in OPENING_BLOCKLIST:
            if s.startswith(bad):
                s = s[len(bad):].strip()
        s = re.sub(rf"^(?:สำหรับ|ชาว|ดวง)?\s*ราศี(?:{re.escape(name_th)}|[ก-๙]+)?\s*", "", s).strip()
        if name_th:
            s = s.replace(name_th, "")
        s = re.sub(r'[\?!.,;:\s\-_"\'()（）！？…]+', "", s)
        for filler in FILLERS:
            s = s.replace(filler, "")
        return s

    @classmethod
    def calculate_similarity(cls, norm_a: str, norm_b: str) -> float:
        if not norm_a or not norm_b:
            return 0.0
        if norm_a == norm_b:
            return 1.0
        return difflib.SequenceMatcher(None, norm_a, norm_b).ratio()

    @classmethod
    def extract_opening_pattern(cls, hook: str, name_th: str = "") -> str:
        s = hook.strip()
        for bad in OPENING_BLOCKLIST:
            if s.startswith(bad):
                s = s[len(bad):].strip()
        s = re.sub(rf"^(?:สำหรับ|ชาว|ดวง)?\s*ราศี(?:{re.escape(name_th)}|[ก-๙]+)?\s*", "", s).strip()
        s = re.sub(r"^(?:สัปดาห์นี้|ช่วงนี้|ระยะนี้)\s*", "", s).strip()
        for stem in KNOWN_OPENING_STEMS:
            if s.startswith(stem):
                return stem
        clean_stem = re.sub(r"\s+", "", s)
        return clean_stem[:10] if clean_stem else "other"

    TIME_PREFIXES_REGEX = re.compile(
        r"(?:สัปดาห์นี้|ช่วงนี้|ระยะนี้|ในสัปดาห์นี้)(?:\s*(?:สัปดาห์นี้|ช่วงนี้|ระยะนี้|ในสัปดาห์นี้))+"
    )

    @classmethod
    def normalize_hook_time_prefixes(cls, text: str) -> str:
        """Eliminates duplicated time phrases like 'สัปดาห์นี้ช่วงนี้', 'สัปดาห์นี้สัปดาห์นี้', etc."""
        def _repl(m: re.Match) -> str:
            val = m.group(0)
            for preferred in ("สัปดาห์นี้", "ช่วงนี้", "ระยะนี้", "ในสัปดาห์นี้"):
                if val.startswith(preferred):
                    return preferred
            return "สัปดาห์นี้"

        return cls.TIME_PREFIXES_REGEX.sub(_repl, text)

    @classmethod
    def clean_hook_prefix(cls, hook: str, name_th: str) -> str:
        clean = hook.strip()
        for bad in OPENING_BLOCKLIST:
            if clean.startswith(bad):
                clean = clean[len(bad):].strip()
        pattern = rf"^(?:สำหรับชาว|ชาวราศี|ชาว|ดวงชาว|ดวง|สำหรับ)?\s*(?:ราศี)?\s*{re.escape(name_th)}\s*"
        clean = re.sub(pattern, "", clean).strip()
        prefix = f"ราศี{name_th}"
        res = f"{prefix} {clean}" if clean else prefix
        return cls.normalize_hook_time_prefixes(res)

    @classmethod
    def is_weak_hook(cls, clean_hook: str, prefix: str, name_th: str = "") -> tuple[bool, str]:
        if len(clean_hook) < cls.HOOK_MIN_LENGTH:
            return True, "too_short"
        if clean_hook.rstrip(".,;… ") == prefix:
            return True, "only_prefix"
        if name_th and cls.is_merely_advice_hook(clean_hook, name_th):
            return True, "advice_only"
        return False, ""

    @classmethod
    def check_body_similarity(cls, hook: str, name_th: str, reading: dict) -> tuple[bool, str, float]:
        norm_hook = cls.normalize_hook(hook, name_th)
        if not norm_hook:
            return False, "", 0.0
        sections = ("overview", "work", "finance", "love", "advice")
        for sec in sections:
            val = (reading.get(sec) or "").strip()
            if not val:
                continue
            norm_sec = cls.normalize_hook(val, name_th)
            if not norm_sec:
                continue
            sim = cls.calculate_similarity(norm_hook, norm_sec)
            if sim >= cls.HOOK_BODY_SIMILARITY_THRESHOLD or (len(norm_hook) >= 20 and norm_hook in norm_sec) or (len(norm_sec) >= 20 and norm_sec in norm_hook):
                effective_sim = max(sim, 0.85 if (norm_hook in norm_sec or norm_sec in norm_hook) else sim)
                return True, sec, round(effective_sim, 3)
        return False, "", 0.0

    @classmethod
    def extract_original_hook_clauses(cls, original_hook: str, name_th: str) -> list[str]:
        """Extracts sub-clauses from an overlong original hook to preserve its central meaning and tension."""
        if not original_hook or not original_hook.strip():
            return []
        clean = cls.clean_hook_prefix(original_hook, name_th)
        clean, _ = cls.strip_hook_polite_ending(clean)
        core = re.sub(rf"^ราศี{re.escape(name_th)}\s*(?:สัปดาห์นี้)?\s*", "", clean).strip()
        if not core:
            return []

        conn_regex = "(" + "|".join(re.escape(c) for c in CONTRAST_CONNECTORS) + ")"
        m = re.search(rf"\s*{conn_regex}\s*", core)
        raw_clauses: list[str] = []

        if m:
            first = core[:m.start()].strip()
            conn = m.group(1).strip()
            second = core[m.end():].strip()
            if first:
                raw_clauses.append(first)
            if second:
                if conn.startswith("แต่ถ้า"):
                    raw_clauses.append(f"ถ้า{second}")
                elif conn.startswith("แต่ต้อง"):
                    raw_clauses.append(f"ต้อง{second}")
                elif conn.startswith("แต่ในขณะเดียวกันก็ต้อง") or conn.startswith("แต่ในขณะเดียวกันต้อง"):
                    raw_clauses.append(f"ต้อง{second}")
                    raw_clauses.append(second)
                elif conn.startswith("แต่ในขณะเดียวกันก็") or conn.startswith("ในขณะเดียวกันก็"):
                    raw_clauses.append(second)
                else:
                    raw_clauses.append(second)
        else:
            split_pat = r"(?<=[^\s])(?:\s*[,;!?…]\s*|\s+(?:เพราะ|เพื่อไม่ให้|ก่อนที่)\s*)"
            parts = [p.strip() for p in re.split(split_pat, core) if p.strip()]
            raw_clauses.extend(parts)

        candidates: list[str] = []
        for cl in raw_clauses:
            clean_cl = re.sub(r"^[,\-;:…\s]+|[,\-;:…\s]+$", "", cl).strip()
            if len(clean_cl) < 15:
                continue
            cand = f"ราศี{name_th} สัปดาห์นี้{clean_cl}"
            cand, _ = cls.strip_hook_polite_ending(cand)
            cand = cls.normalize_hook_time_prefixes(cand)
            if len(cand) <= cls.HOOK_MAX_LENGTH and cand not in candidates:
                candidates.append(cand)
        return candidates

    @classmethod
    def derive_hook_from_content(
        cls,
        sign_id: str,
        name_th: str,
        reading: dict,
        accepted_hooks: list[dict],
        pattern_counts: dict[str, int],
        exclude_section: str | None = None,
        original_hook: str = "",
    ) -> str | None:
        """Derives a concise, strong, curious hook following strict source priority:
        1. original hook meaning (sub-clauses)
        2. overview central tension
        3. work / finance / love strongest tension
        4. advice only as LAST resort (rejecting hooks that are merely advice)
        """
        all_sections = ["overview", "work", "finance", "love", "advice"]
        candidates: list[tuple[str, str]] = []

        # Source 1: original hook clauses
        raw_hook_source = original_hook or str(reading.get("hook") or "")
        if raw_hook_source:
            for orig_cand in cls.extract_original_hook_clauses(raw_hook_source, name_th):
                candidates.append((orig_cand, "original_hook"))

        # Source 2: overview central tension
        if exclude_section != "overview":
            overview_val = (reading.get("overview") or "").strip()
            if overview_val and len(overview_val) >= 15:
                for sent in [s.strip() for s in re.split(r"[.!?\n]+", overview_val) if s.strip()]:
                    clean_sent = re.sub(r"^(?:ภาพรวมสัปดาห์นี้)\s*", "", sent).strip()
                    if len(clean_sent) < 15:
                        continue
                    if len(clean_sent) > 85:
                        sub_parts = re.split(r"\s*(?:แต่|เพราะ|และ|โดย|ก่อนที่)\s*", clean_sent)
                        if sub_parts and len(sub_parts[0]) >= 20:
                            clean_sent = sub_parts[0].strip()
                    cand = f"ราศี{name_th} สัปดาห์นี้{clean_sent}"
                    cand, _ = cls.strip_hook_polite_ending(cand)
                    cand = cls.normalize_hook_time_prefixes(cand)
                    if len(cand) <= cls.HOOK_MAX_LENGTH:
                        candidates.append((cand, "overview"))

        # Source 3: work / finance / love strongest tension
        tension_sections = [s for s in ("work", "finance", "love") if s != exclude_section]
        for sec in tension_sections:
            val = (reading.get(sec) or "").strip()
            if not val or len(val) < 15:
                continue
            for sent in [s.strip() for s in re.split(r"[.!?\n]+", val) if s.strip()]:
                clean_sent = re.sub(r"^(?:ด้านการงาน|ด้านการเงิน|ด้านความรัก)\s*", "", sent).strip()
                if len(clean_sent) < 15:
                    continue
                if len(clean_sent) > 85:
                    sub_parts = re.split(r"\s*(?:แต่|เพราะ|และ|โดย|ก่อนที่)\s*", clean_sent)
                    if sub_parts and len(sub_parts[0]) >= 20:
                        clean_sent = sub_parts[0].strip()
                cand = f"ราศี{name_th} สัปดาห์นี้{clean_sent}"
                cand, _ = cls.strip_hook_polite_ending(cand)
                cand = cls.normalize_hook_time_prefixes(cand)
                if len(cand) <= cls.HOOK_MAX_LENGTH:
                    candidates.append((cand, sec))

        # Source 4: advice only as LAST resort
        if exclude_section != "advice":
            advice_val = (reading.get("advice") or "").strip()
            if advice_val and len(advice_val) >= 15:
                for sent in [s.strip() for s in re.split(r"[.!?\n]+", advice_val) if s.strip()]:
                    clean_sent = re.sub(r"^(?:คำแนะนำคือ)\s*", "", sent).strip()
                    if len(clean_sent) < 15:
                        continue
                    if len(clean_sent) > 85:
                        sub_parts = re.split(r"\s*(?:แต่|เพราะ|และ|โดย|ก่อนที่)\s*", clean_sent)
                        if sub_parts and len(sub_parts[0]) >= 20:
                            clean_sent = sub_parts[0].strip()
                    cand = f"ราศี{name_th} สัปดาห์นี้{clean_sent}"
                    cand, _ = cls.strip_hook_polite_ending(cand)
                    cand = cls.normalize_hook_time_prefixes(cand)
                    if len(cand) <= cls.HOOK_MAX_LENGTH:
                        candidates.append((cand, "advice"))

        for cand, src_sec in candidates:
            cand = cls.normalize_hook_time_prefixes(cand)
            if len(cand) < cls.HOOK_MIN_LENGTH or len(cand) > cls.HOOK_MAX_LENGTH:
                continue
            # Life-first rule: Reject candidates dominated by technical astrology terms
            if ASTRO_TERMS_HOOK_REGEX.search(cand):
                continue
            is_weak, _ = cls.is_weak_hook(cand, f"ราศี{name_th}", name_th)
            if is_weak:
                continue
            if cls.is_merely_advice_hook(cand, name_th):
                continue

            # When checking body similarity for a derived candidate, check other sections
            other_sections = {s: reading.get(s) for s in all_sections if s != src_sec}
            is_body_dup, _, _ = cls.check_body_similarity(cand, name_th, other_sections)
            if is_body_dup:
                continue

            norm = cls.normalize_hook(cand, name_th)
            pattern = cls.extract_opening_pattern(cand, name_th)

            if pattern_counts.get(pattern, 0) >= cls.MAX_SHARED_OPENING_PATTERN:
                continue

            collision = False
            for prev in accepted_hooks:
                sim = cls.calculate_similarity(norm, prev["norm"])
                if sim >= cls.HOOK_SIMILARITY_THRESHOLD:
                    collision = True
                    break
            if not collision:
                return cand

        return None

    @classmethod
    def get_fallback_hook(
        cls,
        sign_id: str,
        name_th: str,
        accepted_hooks: list[dict],
        pattern_counts: dict[str, int],
    ) -> str:
        base_template = STRONG_HOOK_TEMPLATES.get(
            sign_id,
            f"ราศี{name_th} สัปดาห์นี้มีเรื่องสำคัญที่อย่าเพิ่งรีบตัดสินใจ"
        )
        base_template, _ = cls.strip_hook_polite_ending(base_template)
        norm = cls.normalize_hook(base_template, name_th)
        pattern = cls.extract_opening_pattern(base_template, name_th)

        collision = any(cls.calculate_similarity(norm, prev["norm"]) >= cls.HOOK_SIMILARITY_THRESHOLD for prev in accepted_hooks)
        pattern_exceeded = pattern_counts.get(pattern, 0) >= cls.MAX_SHARED_OPENING_PATTERN

        if not collision and not pattern_exceeded:
            return base_template

        prefix = f"ราศี{name_th}"
        core = re.sub(rf"^{re.escape(prefix)}\s*(?:สัปดาห์นี้)?\s*", "", base_template).strip()
        variations = (
            f"{prefix} จังหวะสำคัญในสัปดาห์นี้คือ {core}",
            f"{prefix} สิ่งที่น่าจับตาในสัปดาห์นี้คือ {core}",
            f"{prefix} เรื่องเด่นประจำสัปดาห์นี้คือ {core}",
            f"{prefix} สัปดาห์นี้จุดที่ควรใส่ใจคือ {core}",
        )
        for var in variations:
            var, _ = cls.strip_hook_polite_ending(var)
            v_norm = cls.normalize_hook(var, name_th)
            v_pat = cls.extract_opening_pattern(var, name_th)
            if not any(cls.calculate_similarity(v_norm, p["norm"]) >= cls.HOOK_SIMILARITY_THRESHOLD for p in accepted_hooks) and pattern_counts.get(v_pat, 0) < cls.MAX_SHARED_OPENING_PATTERN:
                return var

        return base_template

    @classmethod
    def clean_duplicated_section_prefixes(cls, reading: dict) -> int:
        """Cleans up duplicated semantic section prefixes like 'ด้านความรัก ความรัก...' -> 'ด้านความรัก...'"""
        prefix_cleanup_rules = (
            ("love", re.compile(r"^(ด้านความรัก)\s*(?:ความรัก|เรื่องความรัก)\s*"), r"\1 "),
            ("finance", re.compile(r"^(ด้านการเงิน)\s*(?:การเงิน|เรื่องการเงิน)\s*"), r"\1 "),
            ("work", re.compile(r"^(ด้านการงาน)\s*(?:งาน|การงาน|เรื่องงาน)\s*"), r"\1 "),
        )
        cleaned_count = 0
        for sec, pattern, repl in prefix_cleanup_rules:
            text = reading.get(sec, "").strip()
            if not text:
                continue
            new_text, n = pattern.subn(repl, text)
            if n > 0:
                reading[sec] = new_text
                cleaned_count += n
        return cleaned_count

    DETERMINISTIC_SAFETY_RULES = (
        (re.compile(r"(?:ระวัง)?จะเกิดอุบัติเหตุ(?:ร้ายแรง)?"), "ควรระมัดระวังความปลอดภัยในการเดินทาง"),
        (re.compile(r"(?:ระวัง)?จะ(?:เป็น|ติด)โรคร้าย(?:แรง)?"), "ควรดูแลสุขภาพและสังเกตร่างกาย"),
        (re.compile(r"(?:ระวัง)?จะป่วยหนัก"), "ควรใส่ใจดูแลสุขภาพเป็นพิเศษ"),
        (re.compile(r"จะ(?:ถึงแก่ชีวิต|เสียชีวิต|ตาย)"), "ควรใช้ชีวิตด้วยความรอบคอบและไม่ประมาท"),
        (re.compile(r"จะ(?:ตั้งครรภ์|ท้อง)(?:แน่นอน)?"), "มีเกณฑ์เรื่องดี ๆ ในครอบครัว"),
        (re.compile(r"รักษาหายขาดแน่นอน"), "มีแนวโน้มฟื้นตัวดีขึ้น"),
        (re.compile(r"จะหายไปแน่นอน"), "มีแนวโน้มคลี่คลาย"),
        (re.compile(r"จะหายแน่นอน"), "มีแนวโน้มดีขึ้น"),
        (re.compile(r"จะหายไป"), "อาจค่อย ๆ คลี่คลาย"),
        (re.compile(r"จะได้เงินแน่นอน"), "มีโอกาสได้เงิน"),
        (re.compile(r"จะได้งานแน่นอน"), "มีโอกาสได้งาน"),
        (re.compile(r"จะรวยแน่นอน"), "มีโอกาสทางการเงินที่ดีขึ้น"),
        (re.compile(r"จะพบเนื้อคู่แน่นอน"), "มีโอกาสพบคนที่ถูกใจ"),
        (re.compile(r"จะเจอเนื้อคู่แน่นอน"), "มีโอกาสพบคนที่ถูกใจ"),
        (re.compile(r"จะสำเร็จแน่นอน"), "มีโอกาสสำเร็จสูง"),
        (re.compile(r"จะชนะแน่นอน"), "มีโอกาสชนะ"),
        (re.compile(r"จะหมดหนี้แน่นอน"), "มีแนวโน้มจัดการภาระหนี้ได้ดีขึ้น"),
        (re.compile(r"จะสมหวังแน่นอน"), "มีโอกาสสมหวัง"),
        (re.compile(r"จะต้องเกิดขึ้นแน่นอน"), "มีแนวโน้มเกิดขึ้น"),
        (re.compile(r"เกิดขึ้นแน่นอน"), "มีแนวโน้มเกิดขึ้น"),
        (re.compile(r"แน่นอน 100%|แน่นอนร้อยเปอร์เซ็นต์"), "มีแนวโน้มสูง"),
    )

    @classmethod
    def soften_deterministic_claims(cls, reading: dict) -> int:
        """Softens rigid fortune-teller guarantees and enforces health/safety wording rules."""
        sections = ("hook", "overview", "work", "finance", "love", "advice", "closing")
        modified_count = 0
        for sec in sections:
            text = reading.get(sec)
            if not isinstance(text, str) or not text.strip():
                continue
            orig = text
            for pattern, repl in cls.DETERMINISTIC_SAFETY_RULES:
                new_text, n = pattern.subn(repl, text)
                if n > 0:
                    text = new_text
                    modified_count += n
            if text != orig:
                reading[sec] = text
        return modified_count

    @classmethod
    def curate_batch(cls, payload: dict, start_date: date, end_date: date) -> dict:
        raw_text = str(payload)
        if CJK_REGEX.search(raw_text):
            raise AppError("ZODIAC_INVALID_CHARACTERS", "พบตัวอักษรภาษาที่ไม่ถูกต้อง (CJK) ในบทคำทำนาย")

        display_th = thai_week_range(start_date, end_date)
        week_data = payload.setdefault("week", {})
        week_data["start_date"] = start_date.isoformat()
        week_data["end_date"] = end_date.isoformat()
        week_data["display_th"] = display_th

        raw_readings = payload.get("zodiacs")
        if not isinstance(raw_readings, list) or len(raw_readings) != 12:
            count = len(raw_readings) if isinstance(raw_readings, list) else 0
            raise AppError("ZODIAC_COUNT_INVALID", f"ต้องมีข้อมูลครบทั้ง 12 ราศีพอดี (พบ {count}/12)")

        readings_map: dict[str, dict] = {}
        for item in raw_readings:
            if not isinstance(item, dict) or "id" not in item:
                raise AppError("ZODIAC_STRUCTURE_INVALID", "โครงสร้างข้อมูลราศีไม่ถูกต้อง")
            zid = str(item["id"]).strip().lower()
            if zid not in cls.ZODIAC_BY_ID:
                raise AppError("ZODIAC_UNKNOWN_ID", f"พบรหัสราศีที่ไม่รู้จัก: {zid}")
            readings_map[zid] = item

        if len(readings_map) != 12:
            raise AppError("ZODIAC_MISSING_SIGNS", "ข้อมูลราศีมีรหัสซ้ำหรือมีไม่ครบ 12 ราศี")

        curated_readings = []
        accepted_hooks: list[dict] = []
        pattern_counts: dict[str, int] = {}
        rewritten_hooks: list[dict] = []
        similar_hooks_detected: list[dict] = []
        warnings: list[str] = []
        total_technical_terms_removed = 0
        total_repeated_prefixes_fixed = 0
        total_overlong_rewritten = 0
        total_body_dups_rewritten = 0
        total_polite_removed = 0
        total_duplicated_prefixes_cleaned = 0
        total_semantic_preserved = 0
        total_softened_claims = 0

        for zid in cls.ORDERED_IDS:
            definition = cls.ZODIAC_BY_ID[zid]
            reading = dict(readings_map[zid])
            reading["id"] = zid
            reading["zodiac_th"] = definition.name_th

            t_count = cls.decant_technical_astrology(reading)
            total_technical_terms_removed += t_count

            p_count = cls.fix_repetitive_star_openings(reading)
            total_repeated_prefixes_fixed += p_count

            prefix_clean_count = cls.clean_duplicated_section_prefixes(reading)
            total_duplicated_prefixes_cleaned += prefix_clean_count

            softened_count = cls.soften_deterministic_claims(reading)
            total_softened_claims += softened_count

            raw_hook = str(reading.get("hook") or "").strip()
            clean_hook = cls.clean_hook_prefix(raw_hook, definition.name_th)

            clean_hook, had_polite = cls.strip_hook_polite_ending(clean_hook)
            if had_polite:
                total_polite_removed += 1

            prefix = f"ราศี{definition.name_th}"
            is_weak, weak_reason = cls.is_weak_hook(clean_hook, prefix, definition.name_th)

            needs_rewrite = False
            rewrite_reason = ""
            score: float | None = None
            body_sim_section = ""

            if len(clean_hook) > cls.HOOK_MAX_LENGTH:
                needs_rewrite = True
                rewrite_reason = f"overlong_hook ({len(clean_hook)} chars > {cls.HOOK_MAX_LENGTH})"
                total_overlong_rewritten += 1
            else:
                is_body_dup, body_sec, body_score = cls.check_body_similarity(clean_hook, definition.name_th, reading)
                if is_body_dup:
                    needs_rewrite = True
                    rewrite_reason = f"duplicate_body_section_{body_sec} ({body_score:.2f})"
                    score = body_score
                    body_sim_section = body_sec
                    total_body_dups_rewritten += 1
                elif is_weak:
                    needs_rewrite = True
                    rewrite_reason = f"weak_hook ({weak_reason})"
                else:
                    norm_hook = cls.normalize_hook(clean_hook, definition.name_th)
                    hook_pattern = cls.extract_opening_pattern(clean_hook, definition.name_th)

                    highest_sim = 0.0
                    most_similar_sign = ""
                    for prev in accepted_hooks:
                        sim = cls.calculate_similarity(norm_hook, prev["norm"])
                        if sim > highest_sim:
                            highest_sim = sim
                            most_similar_sign = prev["id"]

                    if highest_sim >= 0.999:
                        needs_rewrite = True
                        rewrite_reason = f"exact_duplicate_with_{most_similar_sign}"
                        score = 1.0
                        similar_hooks_detected.append({
                            "id": zid,
                            "compared_with": most_similar_sign,
                            "similarity_score": 1.0,
                            "type": "exact_duplicate",
                        })
                    elif highest_sim >= cls.HOOK_SIMILARITY_THRESHOLD:
                        needs_rewrite = True
                        rewrite_reason = f"high_similarity_with_{most_similar_sign} ({highest_sim:.2f})"
                        score = highest_sim
                        similar_hooks_detected.append({
                            "id": zid,
                            "compared_with": most_similar_sign,
                            "similarity_score": round(highest_sim, 3),
                            "type": "high_similarity",
                        })
                    elif pattern_counts.get(hook_pattern, 0) >= cls.MAX_SHARED_OPENING_PATTERN:
                        needs_rewrite = True
                        rewrite_reason = f"shared_opening_pattern_exceeded ({hook_pattern})"
                        score = highest_sim
                        warnings.append(f"Sign {zid} exceeded shared opening pattern limit for '{hook_pattern}'")

            if needs_rewrite:
                derived = cls.derive_hook_from_content(
                    zid, definition.name_th, reading, accepted_hooks, pattern_counts,
                    exclude_section=body_sim_section or None,
                    original_hook=raw_hook,
                )
                if derived:
                    final_hook = derived
                else:
                    final_hook = cls.get_fallback_hook(zid, definition.name_th, accepted_hooks, pattern_counts)

                final_hook, _ = cls.strip_hook_polite_ending(final_hook)

                rewritten_hooks.append({
                    "id": zid,
                    "original": raw_hook,
                    "final": final_hook,
                    "reason": rewrite_reason,
                    "similarity_score": round(score, 3) if score is not None else None,
                    "original_length": len(raw_hook),
                    "final_length": len(final_hook),
                })
                logger.info(
                    "Zodiac hook curated | zodiac_id=%s reason=%s similarity_score=%s orig_len=%d final_len=%d original=%r final=%r",
                    zid, rewrite_reason, score, len(raw_hook), len(final_hook), raw_hook, final_hook,
                )
            elif clean_hook != raw_hook:
                final_hook = clean_hook
                rewritten_hooks.append({
                    "id": zid,
                    "original": raw_hook,
                    "final": final_hook,
                    "reason": "normalized_prefix_or_polite_trimmed",
                    "similarity_score": None,
                    "original_length": len(raw_hook),
                    "final_length": len(final_hook),
                })
                total_semantic_preserved += 1
                logger.info(
                    "Zodiac hook normalized | zodiac_id=%s orig_len=%d final_len=%d original=%r final=%r",
                    zid, len(raw_hook), len(final_hook), raw_hook, final_hook,
                )
            else:
                final_hook = clean_hook
                total_semantic_preserved += 1

            final_norm = cls.normalize_hook(final_hook, definition.name_th)
            final_pattern = cls.extract_opening_pattern(final_hook, definition.name_th)
            accepted_hooks.append({
                "id": zid,
                "hook": final_hook,
                "norm": final_norm,
                "pattern": final_pattern,
            })
            pattern_counts[final_pattern] = pattern_counts.get(final_pattern, 0) + 1

            reading["hook"] = final_hook
            curated_readings.append(reading)

        curator_report = {
            "status": "passed" if len(rewritten_hooks) == 0 else "curated",
            "version": cls.CURATOR_VERSION,
            "rewritten_hooks_count": len(rewritten_hooks),
            "rewritten_hooks": rewritten_hooks,
            "technical_terms_removed": total_technical_terms_removed,
            "repeated_prefixes_fixed": total_repeated_prefixes_fixed,
            "similar_hooks_detected": similar_hooks_detected,
            "warnings": warnings,
            "overlong_hooks_rewritten": total_overlong_rewritten,
            "hook_body_duplicates_rewritten": total_body_dups_rewritten,
            "polite_hook_endings_removed": total_polite_removed,
            "duplicated_section_prefixes_removed": total_duplicated_prefixes_cleaned,
            "semantic_hooks_preserved": total_semantic_preserved,
            "deterministic_claims_softened": total_softened_claims,
        }

        payload["zodiacs"] = curated_readings
        payload["curator"] = curator_report
        return payload

    @classmethod
    def curate_hook(
        cls,
        sign_id: str,
        name_th: str,
        hook: str,
        overview: str = "",
        reading: dict | None = None,
    ) -> str:
        """Backward-compatible single hook curator."""
        clean = cls.clean_hook_prefix(hook, name_th)
        clean, _ = cls.strip_hook_polite_ending(clean)
        hook_container = {"hook": clean}
        cls.soften_deterministic_claims(hook_container)
        clean = hook_container["hook"]
        prefix = f"ราศี{name_th}"

        is_weak, _ = cls.is_weak_hook(clean, prefix, name_th)
        source_reading = dict(reading or {})
        if overview and "overview" not in source_reading:
            source_reading["overview"] = overview

        is_dup, _, _ = cls.check_body_similarity(clean, name_th, source_reading)

        if not is_weak and len(clean) <= cls.HOOK_MAX_LENGTH and not is_dup:
            return clean

        derived = cls.derive_hook_from_content(sign_id, name_th, source_reading, [], {}, original_hook=hook)
        if derived:
            derived, _ = cls.strip_hook_polite_ending(derived)
            return derived

        fallback = cls.get_fallback_hook(sign_id, name_th, [], {})
        fallback, _ = cls.strip_hook_polite_ending(fallback)
        return fallback

    @classmethod
    def decant_technical_astrology(cls, reading: dict) -> int:
        """Limits explicit astrology references to <= 2 and converts the rest into practical consequences."""
        sections = ["overview", "work", "finance", "love", "advice"]

        replacements = (
            (re.compile(r"ดาว[ก-๙]+ในเรือน(อาชีพ|การงาน)\S*"), "จังหวะงานช่วงนี้"),
            (re.compile(r"ดาว[ก-๙]+ในเรือน(เงิน|รายได้|การเงิน)\S*"), "ด้านการเงินช่วงนี้"),
            (re.compile(r"ดาว[ก-๙]+ในเรือน(คู่สัมพันธ์|ความรัก)\S*"), "เรื่องความสัมพันธ์"),
            (re.compile(r"ดาว[ก-๙]+ในเรือน(เครือข่าย|เพื่อนฝูง)\S*"), "การพบปะผู้คน"),
            (re.compile(r"ดาว[ก-๙]+ในเรือน(บ้าน|ครอบครัว)\S*"), "บรรยากาศในครอบครัว"),
            (re.compile(r"ดาว[ก-๙]+ในเรือน(จิตใต้สำนึก|เบื้องหลัง)\S*"), "เรื่องที่อยู่เบื้องหลัง"),
            (re.compile(r"ดาว[ก-๙]+ในเรือน(กิจวัตร|สุขภาพ)\S*"), "การจัดการเวลาและสุขภาพ"),
            (re.compile(r"ดาว[ก-๙]+ในเรือนความสุข\S*"), "การใช้เวลาพักผ่อน"),
            (re.compile(r"ดาว[ก-๙]+และดาว[ก-๙]+ถอยหลัง\S*"), "จังหวะที่ควรทบทวนให้รอบคอบ"),
            (re.compile(r"ดาว[ก-๙]+ถอยหลังในเรือน\S*"), "เรื่องที่อาจต้องใช้ความอดทน"),
            (re.compile(r"ทำมุม(โยค|เล็ง|ตรีโกณ|จตุโกณ)กับดาว[ก-๙]+"), "ส่งผลให้"),
            (re.compile(r"เรือนภพที่\s*\d+"), "จังหวะชีวิต"),
            (re.compile(r"ในเรือนที่\s*\d+"), "ในช่วงนี้"),
        )

        tech_count = 0
        replaced_count = 0
        for sec in sections:
            text = reading.get(sec, "")
            if not text:
                continue

            if sec in ("work", "finance", "love", "advice"):
                for pattern, repl in replacements:
                    text, n = pattern.subn(repl, text)
                    replaced_count += n

            stars = len(re.findall(r"ดาว[ก-๙]+", text))
            if tech_count + stars > 2 and sec in ("finance", "love", "advice"):
                for pattern, repl in replacements:
                    text, n = pattern.subn(repl, text)
                    replaced_count += n
                text, n = re.subn(r"ดาว[ก-๙]+ใน\S+", "ช่วงนี้", text)
                replaced_count += n
            tech_count += stars
            reading[sec] = text.strip()

        return replaced_count

    @classmethod
    def fix_repetitive_star_openings(cls, reading: dict) -> int:
        """Ensures sections do not repeatedly begin with 'ดาว...'."""
        section_prefixes = {
            "work": ("ด้านการงาน ", re.compile(r"^(?:ดาว[ก-๙]+|ดวงอาทิตย์)\S*\s*")),
            "finance": ("ด้านการเงิน ", re.compile(r"^(?:ดาว[ก-๙]+|ดวงอาทิตย์)\S*\s*")),
            "love": ("ด้านความรัก ", re.compile(r"^(?:ดาว[ก-๙]+|ดวงอาทิตย์)\S*\s*")),
            "advice": ("คำแนะนำคือ ", re.compile(r"^(?:ดาว[ก-๙]+|ดวงอาทิตย์)\S*\s*")),
        }

        fixed_count = 0
        for sec, (pref, pattern) in section_prefixes.items():
            text = reading.get(sec, "").strip()
            if not text:
                continue

            if text.startswith("ดาว") or text.startswith("ดวงอาทิตย์"):
                text = pattern.sub("", text).strip()
                if not text.startswith(pref.strip()):
                    text = f"{pref}{text}"
                fixed_count += 1
            elif not text.startswith(pref.strip()) and sec in ("work", "finance", "love"):
                text = f"{pref}{text}"
                fixed_count += 1

            reading[sec] = text

        return fixed_count
