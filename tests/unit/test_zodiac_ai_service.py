from datetime import date

import pytest

from app.config.settings import Settings
from app.domain.errors import AppError
from app.services.zodiac_ai_service import ZODIAC_IDS, ZodiacAiService


def reading(zodiac_id: str) -> dict:
    return {
        "id": zodiac_id,
        "hook": f"สัปดาห์นี้ราศี{zodiac_id}มีจังหวะสำคัญ",
        "overview": "มีแนวโน้มได้ทบทวนสิ่งสำคัญ",
        "work": "งานอาจมีโอกาสใหม่ ควรตรวจรายละเอียด",
        "finance": "การเงินควรวางแผนและไม่ตัดสินใจเร่งรีบ",
        "love": "ความสัมพันธ์มีแนวโน้มดีขึ้นจากการสื่อสาร",
        "advice": "ใช้ข้อมูลจริงและสติประกอบการตัดสินใจ",
        "closing": "ขอให้เป็นสัปดาห์ที่ดี แล้วกลับมาพบกันใหม่สัปดาห์หน้าครับ",
    }


def test_missing_key_is_clear_and_status_is_safe():
    service = ZodiacAiService(Settings())
    assert service.status()["available"] is False
    assert "api_key" not in service.status()
    with pytest.raises(AppError) as error:
        service.generate(date(2026, 9, 14), date(2026, 9, 20))
    assert error.value.code == "DEEPSEEK_NOT_CONFIGURED"


def test_project_skill_is_present_and_loaded_before_generation():
    service = ZodiacAiService(Settings(deepseek_api_key="test-only"))
    text = service.skill_path.read_text(encoding="utf-8")
    assert service.skill_path.as_posix().endswith("skills/zodiac-weekly/SKILL.md")
    assert "Research before interpretation" in text
    assert "Return valid JSON only" in text


def test_output_parser_ignores_reasoning_text_before_json():
    data = {"output": [
        {"content": [{"type": "reasoning_text", "text": "analysis with {not json}"}]},
        {"content": [{"type": "output_text", "text": '{"zodiacs": []}'}]},
    ]}
    assert ZodiacAiService._output_text(data) == '{"zodiacs": []}'


def test_generated_draft_is_validated_and_dates_are_authoritative(monkeypatch):
    settings = Settings(deepseek_api_key="secret-for-test")
    service = ZodiacAiService(settings)
    response_payload = {"output_text": __import__("json").dumps({"zodiacs": [reading(item) for item in ZODIAC_IDS]}, ensure_ascii=False)}

    class Response:
        status_code = 200
        ok = True
        def json(self):
            return response_payload

    captured = {}
    def fake_post(url, **kwargs):
        captured.update(url=url, **kwargs)
        return Response()

    monkeypatch.setattr("app.services.zodiac_ai_service.requests.post", fake_post)
    result = service.generate(date(2026, 9, 14), date(2026, 9, 20))
    assert result["week"] == {
        "start_date": "2026-09-14",
        "end_date": "2026-09-20",
        "display_th": "14 - 20 ก.ย. 2569",
    }
    assert len(result["zodiacs"]) == 12
    assert captured["json"]["tools"] == [{"type": "web_search"}]
    assert "secret-for-test" not in str(result)
    assert service.last_log is not None
    assert service.last_log["request"]["body"]["model"] == settings.deepseek_model
    assert service.last_log["response"]["status_code"] == 200
    assert service.last_log["request"]["headers"]["Authorization"] == "Bearer [REDACTED]"
    assert "secret-for-test" not in str(service.last_log)


def test_invalid_or_incomplete_model_json_is_rejected(monkeypatch):
    service = ZodiacAiService(Settings(deepseek_api_key="secret-for-test"))

    class Response:
        status_code = 200
        ok = True
        def json(self):
            return {"output_text": '{"zodiacs": []}'}

    monkeypatch.setattr("app.services.zodiac_ai_service.requests.post", lambda *args, **kwargs: Response())
    with pytest.raises(AppError) as error:
        service.generate(date(2026, 9, 14), date(2026, 9, 20))
    assert error.value.code == "ZODIAC_COUNT_INVALID"


def test_model_explicit_error_response_is_surfaced(monkeypatch):
    settings = Settings(deepseek_api_key="secret-for-test")
    service = ZodiacAiService(settings)
    error_payload = {
        "output_text": __import__("json").dumps({
            "error": "research_unavailable",
            "message": "ไม่สามารถจัดทำได้เนื่องจากไม่มีข้อมูล ephemeris",
            "zodiacs": []
        })
    }

    class Response:
        status_code = 200
        ok = True
        def json(self):
            return error_payload

    monkeypatch.setattr("app.services.zodiac_ai_service.requests.post", lambda *args, **kwargs: Response())
    with pytest.raises(AppError) as error:
        service.generate(date(2026, 9, 14), date(2026, 9, 20))
    assert error.value.code == "DEEPSEEK_MODEL_REJECTED"
    assert "ไม่สามารถจัดทำได้เนื่องจากไม่มีข้อมูล ephemeris" in str(error.value.message)


