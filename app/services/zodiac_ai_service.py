from __future__ import annotations

import json
import time
from datetime import date, datetime
from pathlib import Path

import requests

from app.config.settings import Settings
from app.domain.errors import AppError
from app.domain.zodiac_models import ZodiacBatchImport
from app.services.zodiac_curator import ZodiacCurator
from app.services.zodiac_ephemeris_service import ZodiacEphemerisService


ZODIAC_IDS = [
    "capricorn", "aquarius", "pisces", "aries", "taurus", "gemini",
    "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius",
]


class ZodiacAiService:
    """Build an editable weekly draft; never starts TTS or rendering."""

    def __init__(self, settings: Settings, ephemeris_service: ZodiacEphemerisService | None = None):
        self.settings = settings
        self.ephemeris_service = ephemeris_service or ZodiacEphemerisService(Path("workspaces"))
        self.skill_path = Path(__file__).resolve().parents[2] / "skills" / "zodiac-weekly" / "SKILL.md"
        self.last_log: dict | None = None

    @property
    def available(self) -> bool:
        return bool(self.settings.deepseek_api_key)

    def status(self) -> dict:
        return {"available": self.available, "provider": "DeepSeek", "model": self.settings.deepseek_model, "webSearch": True}

    def generate(self, start_date: date, end_date: date) -> dict:
        if not self.available:
            raise AppError("DEEPSEEK_NOT_CONFIGURED", "ยังไม่ได้ตั้งค่า DEEPSEEK_API_KEY ใน .env แล้วรีสตาร์ต AutoClip")
        if not self.skill_path.is_file():
            raise AppError("ZODIAC_SKILL_MISSING", "ไม่พบ skills/zodiac-weekly/SKILL.md จึงหยุดเพื่อไม่ให้สร้างดวงผิดมาตรฐาน")

        # Step 1: Deterministic astronomical research (fail clearly if unavailable)
        research = self.ephemeris_service.get_weekly_research(start_date, end_date)

        endpoint = f"{self.settings.deepseek_base_url}/responses"
        prompt_text = self._prompt(start_date, end_date, research)
        instructions_text = self.skill_path.read_text(encoding="utf-8")
        req_payload = {
            "model": self.settings.deepseek_model,
            "instructions": instructions_text,
            "input": prompt_text,
            "tools": [{"type": "web_search"}],
            "tool_choice": "auto",
            "text": {"format": {"type": "json_object"}},
        }

        start_time = time.time()
        self.last_log = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "ephemeris_verified": research.get("verified", False),
            "ephemeris_summary": research.get("summary_th", ""),
            "request": {
                "url": endpoint,
                "headers": {"Authorization": "Bearer [REDACTED]", "Content-Type": "application/json"},
                "body": {
                    "model": self.settings.deepseek_model,
                    "instructions_summary": f"{len(instructions_text)} characters (from skills/zodiac-weekly/SKILL.md)",
                    "input": prompt_text,
                    "tools": [{"type": "web_search"}],
                    "tool_choice": "auto",
                    "text": {"format": {"type": "json_object"}},
                },
            },
            "response": None,
            "error": None,
            "duration_seconds": 0.0,
        }

        try:
            response = requests.post(
                endpoint,
                headers={"Authorization": f"Bearer {self.settings.deepseek_api_key}", "Content-Type": "application/json"},
                json=req_payload,
                timeout=180,
            )
            self.last_log["duration_seconds"] = round(time.time() - start_time, 2)
            try:
                resp_json = response.json()
                self.last_log["response"] = {"status_code": response.status_code, "body": resp_json}
            except Exception:
                self.last_log["response"] = {"status_code": response.status_code, "body": response.text}
        except requests.RequestException as exc:
            self.last_log["duration_seconds"] = round(time.time() - start_time, 2)
            self.last_log["error"] = f"Request failed: {exc}"
            raise AppError("DEEPSEEK_UNAVAILABLE", f"ติดต่อ DeepSeek ไม่สำเร็จ ({exc}) กรุณาลองใหม่") from exc

        if response.status_code == 401:
            self.last_log["error"] = "HTTP 401: Unauthorized (DEEPSEEK_API_KEY ไม่ถูกต้องหรือหมดอายุ)"
            raise AppError("DEEPSEEK_AUTH_FAILED", "DEEPSEEK_API_KEY ไม่ถูกต้องหรือหมดอายุ")
        if response.status_code == 429:
            self.last_log["error"] = "HTTP 429: Rate Limited (DeepSeek ใช้งานเกินโควต้าชั่วคราว)"
            raise AppError("DEEPSEEK_RATE_LIMITED", "DeepSeek ใช้งานเกินโควต้าชั่วคราว กรุณาลองใหม่")
        if not response.ok:
            self.last_log["error"] = f"HTTP {response.status_code}: Request failed"
            raise AppError("DEEPSEEK_REQUEST_FAILED", f"DeepSeek สร้างร่างไม่สำเร็จ (HTTP {response.status_code})")

        try:
            raw_output = self._output_text(resp_json if isinstance(resp_json, dict) else response.json())
            payload = self._json_object(raw_output)

            # Surface explicit model error response if returned
            if payload.get("error"):
                err_msg = payload.get("message") or str(payload.get("error"))
                self.last_log["error"] = f"DeepSeek rejected: {err_msg}"
                raise AppError("DEEPSEEK_MODEL_REJECTED", f"DeepSeek รายงาน: {err_msg}")

            # Enforce 10 curation and validation rules
            payload = ZodiacCurator.curate_batch(payload, start_date, end_date)

            payload.update({
                "schema": "autoclip.zodiac-weekly-batch.v1",
                "week": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "display_th": payload["week"]["display_th"],
                },
                "tts_provider": "google-gemini",
                "voice": payload.get("voice", {"voice": "Iapetus", "language": "th-TH", "speed": 1.10}),
                "visual": payload.get("visual", {
                    "use_template_as_primary_visual": True,
                    "generate_new_images": False,
                    "date_overlay": {"enabled": True, "text_source": "week.display_th", "preserve_master_image": True},
                    "motion": {"enabled": False, "preset": "none"},
                }),
            })
            return ZodiacBatchImport.model_validate(payload).model_dump(by_alias=True, mode="json")
        except AppError:
            raise
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self.last_log["error"] = f"JSON parse error: {exc}"
            raise AppError("DEEPSEEK_INVALID_JSON", f"DeepSeek ส่งข้อมูลไม่สมบูรณ์: {exc}") from exc

    @staticmethod
    def _output_text(data: dict) -> str:
        if isinstance(data.get("output_text"), str):
            return data["output_text"]
        parts: list[str] = []
        for item in data.get("output", []):
            for content in item.get("content", []) if isinstance(item, dict) else []:
                # Thinking models may return a long `reasoning_text` item before
                # the final JSON. Only parse the actual assistant output.
                if isinstance(content, dict) and content.get("type") == "output_text" and isinstance(content.get("text"), str):
                    parts.append(content["text"])
        if not parts:
            raise ValueError("missing output text")
        return "\n".join(parts)

    @staticmethod
    def _json_object(text: str) -> dict:
        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        start, end = clean.find("{"), clean.rfind("}")
        if start < 0 or end < start:
            raise ValueError("missing JSON object")
        value = json.loads(clean[start:end + 1])
        if not isinstance(value, dict):
            raise ValueError("JSON is not an object")
        return value

    @staticmethod
    def _prompt(start_date: date, end_date: date, research: dict) -> str:
        ids = ", ".join(ZODIAC_IDS)
        summary = research.get("summary_th", "")
        planets_brief = ", ".join(
            f"{v['name_th']} สถิตราศี{v['sign_th']} ({v['degree_in_sign']}°){' [ถอยหลัง]' if v.get('is_retrograde') else ''}"
            for v in research.get("planetary_positions", {}).values()
        )
        aspects_brief = "; ".join(a.get("description_th", "") for a in research.get("major_aspects", [])[:5]) or "ไม่มีมุมสัมพันธ์พิเศษในระยะเอื้อมแคบ"
        phases_brief = ", ".join(f"{p['phase_th']} วันที่ {p['date']}" for p in research.get("moon_phases", [])) or "ไม่มีจุดตัดเฟสหลักในสัปดาห์นี้"

        return f"""นี่คือข้อมูลดาราศาสตร์และตำแหน่งดวงดาวประจำสัปดาห์ {start_date.isoformat()} ถึง {end_date.isoformat()} ที่คำนวณและตรวจสอบยืนยันทางวิทยาศาสตร์เรียบร้อยแล้ว (Verified Ephemeris Source of Truth):

[สรุปปรากฏการณ์ท้องฟ้าสัปดาห์นี้]
{summary}

[ตำแหน่งดาวเคราะห์จริงประจำสัปดาห์ (Tropical Zodiac)]
{planets_brief}

[มุมสัมพันธ์สำคัญ (Major Aspects)]
{aspects_brief}

[เฟสดวงจันทร์]
{phases_brief}

---
กฎเหล็กและคำสั่งการเขียนบทคำทำนาย (Locked Editorial Standards):
1. ข้อมูลตำแหน่งดวงดาวข้างต้นคือความจริงทางดาราศาสตร์ที่ผ่านการยืนยันแล้ว ห้ามแต่งเติมหรือเปลี่ยนแปลงข้อมูลดาวเด็ดขาด
2. หน้าที่ของคุณคือ "การตีความและเขียนบทพยากรณ์" (Interpretation & Scriptwriting) สำหรับคนเหนือดวง ให้ครบทั้ง 12 ราศี โดยอิงจากข้อมูลดวงดาวข้างต้น
3. ห้ามปฏิเสธงานด้วย research_unavailable เพราะระบบได้ส่งข้อมูลวิจัยที่ตรวจสอบแล้วมาให้ในบริบทนี้ครบถ้วนแล้ว
4. ภาษาที่ใช้: ภาษาไทยล้วน ห้ามมีตัวอักษรจีน/ญี่ปุ่น/เกาหลี (CJK) หรือคำต่างชาติปน
5. ความเข้าใจง่าย: บทพูดต้องเข้าใจง่ายสำหรับคนทั่วไปที่ไม่รู้เรื่องโหราศาสตร์เลย ห้ามอัดศัพท์โหรหรือศัพท์เรือนภพ (เช่น ห้ามใช้ "เรือนที่ 10", "เรือนจิตใต้สำนึก", "เรือนกัมมะ", "เรือนคู่สัมพันธ์")
6. อ้างอิงทางโหราศาสตร์ไม่เกิน 1–2 ครั้งต่อราศี: ให้มีชื่อดาวได้ไม่เกิน 1–2 จุดในแต่ละราศี (ควรอยู่ในส่วน overview) ส่วนเรื่องงาน เงิน ความรัก คำแนะนำ ให้แปลงเป็นผลลัพธ์และการกระทำในชีวิตจริง
7. ห้ามขึ้นต้นแต่ละส่วนซ้ำๆ ด้วย "ดาว...": ห้ามขึ้นต้นงาน เงิน ความรัก ด้วย "ดาวอังคาร...", "ดาวศุกร์...", "ดาวพลูโต..." ติดกัน ให้ขึ้นด้วยบริบทชีวิตจริง เช่น "เรื่องงานช่วงนี้...", "ด้านการเงินมีแนวโน้ม...", "ความรักควรระวัง..."
8. กฎ Hook 1–3 วินาทีแรก:
   - Hook ต้องขึ้นต้นด้วยชื่อราศีเป๊ะๆ ตามรูปแบบ: "ราศี{{ชื่อราศีไทย}} ..." (เช่น "ราศีมังกร ...", "ราศีกุมภ์ ...") ห้ามมี "สำหรับชาว...", "ดวงประจำสัปดาห์..."
   - ประโยคแรกต้องสร้างความอยากรู้และหยุดคนดูทันที มีประเด็นน่าจับตาหรือข้อควรระวัง
9. โทนคำทำนาย: อธิบายเป็นแนวโน้มและโอกาส ใช้คำว่า "มีแนวโน้ม", "มีโอกาส", "ช่วงนี้อาจ", "ควรระวัง", "เหมาะกับการ" ห้ามรับประกันผล ห้ามทำนายเรื่องความตาย อุบัติเหตุ หรือโรคร้าย
10. จัดทำบทพยากรณ์ให้ครบทั้ง 12 ราศีพอดีตามลำดับ id ดังนี้: {ids}
11. แต่ละราศีใช้โครงสร้าง 6 ส่วน: hook, overview, work, finance, love, advice, closing
12. คืนค่าเฉพาะ JSON object เท่านั้น (ห้ามมี markdown หรือคำอธิบายนอก JSON):
{{"zodiacs":[{{"id":"capricorn","hook":"...","overview":"...","work":"...","finance":"...","love":"...","advice":"...","closing":"..."}}]}}"""


