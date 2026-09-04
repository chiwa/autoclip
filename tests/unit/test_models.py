import pytest
from pydantic import ValidationError

from app.domain.models import Script


def valid_data():
    return {"project": {"id": "lake-natron", "title": "Lake Natron", "language": "th-TH"}, "voice": {"provider": "dummy", "voice": "test", "speed": 1.0}, "scenes": [{"id": "scene-01", "image": "images/scene-01.png", "narration": "คุณเชื่อไหม", "motion": "none"}]}


def test_thai_and_subtitle_default_and_order():
    data = valid_data()
    data["scenes"].append({"id": "scene-02", "image": "images/scene-02.png", "narration": "เรื่องนี้มีอยู่จริง", "subtitle": "", "motion": "slow_zoom_in"})
    script = Script.model_validate(data)
    assert [scene.id for scene in script.scenes] == ["scene-01", "scene-02"]
    assert script.scenes[0].subtitle == "คุณเชื่อไหม"
    assert script.scenes[0].show_subtitle is True
    assert script.scenes[1].subtitle == "เรื่องนี้มีอยู่จริง"
    assert script.scenes[1].show_subtitle is True
    assert script.scenes[0].transition is None


def test_scene_can_disable_subtitles():
    data = valid_data()
    data["scenes"] = [
        {"id": "scene-01", "image": "images/s1.png", "narration": "มีซับ", "motion": "none"},
        {"id": "scene-02", "image": "images/s2.png", "narration": "ไม่มีซับแบบ show_subtitle", "show_subtitle": False, "motion": "none"},
        {"id": "scene-03", "image": "images/s3.png", "narration": "ไม่มีซับแบบ subtitle false", "subtitle": False, "motion": "none"},
        {"id": "scene-04", "image": "images/s4.png", "narration": "ไม่มีซับแบบ subtitle none", "subtitle": "none", "motion": "none"},
    ]
    script = Script.model_validate(data)
    assert script.scenes[0].show_subtitle is True
    assert script.scenes[0].subtitle == "มีซับ"
    assert script.scenes[1].show_subtitle is False
    assert script.scenes[1].subtitle is None
    assert script.scenes[2].show_subtitle is False
    assert script.scenes[2].subtitle is None
    assert script.scenes[3].show_subtitle is False
    assert script.scenes[3].subtitle is None


def test_scene_accepts_supported_transition_and_rejects_unknown():
    data = valid_data()
    data["scenes"][0]["transition"] = "wipe_left"
    assert Script.model_validate(data).scenes[0].transition == "wipe_left"
    data["scenes"][0]["transition"] = "spin"
    with pytest.raises(ValidationError):
        Script.model_validate(data)


def test_scene_accepts_optional_wan_generation_plan():
    data = valid_data()
    data["scenes"][0]["wan"] = {
        "prompt": "Thai anime presenter with subtle natural motion",
        "negative_prompt": "text, watermark, flicker",
        "seed": 42,
        "frames": 81,
        "steps": 25,
        "lip_sync": True,
        "character_id": "mamase-presenter-v1",
    }

    wan = Script.model_validate(data).scenes[0].wan

    assert wan.seed == 42
    assert wan.steps == 25
    assert wan.lip_sync is True
    assert wan.character_id == "mamase-presenter-v1"


def test_wan_generation_plan_rejects_unsafe_character_id():
    data = valid_data()
    data["scenes"][0]["wan"] = {"prompt": "Lake Natron natural motion", "character_id": "../secret"}

    with pytest.raises(ValidationError):
        Script.model_validate(data)


@pytest.mark.parametrize("mutation", [
    lambda d: d["project"].pop("id"),
    lambda d: d.update(scenes=[]),
    lambda d: d["scenes"].append(dict(d["scenes"][0])),
    lambda d: d["scenes"][0].update(image="/etc/passwd"),
    lambda d: d["scenes"][0].update(image="images/../secret.png"),
])
def test_invalid_scripts(mutation):
    data = valid_data()
    mutation(data)
    with pytest.raises(ValidationError):
        Script.model_validate(data)
