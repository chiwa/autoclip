from app.domain.models import Script
from app.services.reel_quality_validator import ReelQualityValidator


def make_script(scene_count: int, *, motion: str = "cinematic_push_in", resolution: str = "1080x1920") -> Script:
    return Script.model_validate({
        "project": {"id": "retention-test", "title": "Retention", "language": "th-TH", "resolution": resolution},
        "voice": {"provider": "dummy", "voice": "test", "speed": 1.0},
        "scenes": [
            {"id": f"scene-{index + 1:02d}", "image": f"images/{index + 1:02d}.png", "narration": "ทดสอบ", "motion": motion}
            for index in range(scene_count)
        ],
    })


def warning_codes(result) -> set[str]:
    return {warning.code for warning in result.warnings}


def test_50_second_nine_scene_reel_has_healthy_refresh_rate():
    result = ReelQualityValidator().evaluate(make_script(9), [50 / 9] * 9)
    assert "REEL_DURATION_LONG" not in warning_codes(result)
    assert "LOW_VISUAL_REFRESH_RATE" not in warning_codes(result)


def test_64_second_reel_warns_about_duration():
    result = ReelQualityValidator().evaluate(make_script(9), [64 / 9] * 9)
    assert "REEL_DURATION_LONG" in warning_codes(result)


def test_50_second_four_scene_reel_warns_about_refresh_rate():
    result = ReelQualityValidator().evaluate(make_script(4), [12.5] * 4)
    assert "LOW_VISUAL_REFRESH_RATE" in warning_codes(result)


def test_nine_second_static_scene_warns_without_blocking():
    result = ReelQualityValidator().evaluate(make_script(2, motion="none"), [9.0, 4.0])
    assert "SCENE_VISUAL_TOO_LONG" in warning_codes(result)
    assert "HOOK_SCENE_TOO_LONG" in warning_codes(result)


def test_landscape_project_is_not_treated_as_a_reel():
    result = ReelQualityValidator().evaluate(make_script(2, motion="none", resolution="1920x1080"), [30.0, 34.0])
    assert result.warnings == []


def test_old_script_json_remains_valid_without_optional_fields():
    script = make_script(1)
    scene = script.scenes[0]
    assert scene.role is None
    assert scene.keywords == []
    assert scene.sfx is None


def test_optional_reel_fields_are_accepted():
    payload = make_script(1).model_dump(mode="json")
    payload["scenes"][0].update({"role": "hook", "keywords": ["กฎฟิสิกส์", "Multiverse"], "sfx": "reveal"})
    scene = Script.model_validate(payload).scenes[0]
    assert scene.role == "hook"
    assert scene.keywords == ["กฎฟิสิกส์", "Multiverse"]
    assert scene.sfx == "reveal"
