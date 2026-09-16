from pathlib import Path

import pytest

from app.config.settings import ReelOutroSettings
from app.domain.errors import AppError
from app.domain.models import Script
from app.services.reel_outro import migrate_legacy_outro_scene, resolve_reel_outro


def make_script(*, outro=None, legacy=False):
    scenes = [
        {"id": "scene-01", "image": "images/01.png", "narration": "เรื่องหลัก", "motion": "none"},
        {"id": "scene-02", "image": "images/02.png", "narration": "คำถามสุดท้าย", "motion": "slow_zoom_out"},
    ]
    if legacy:
        scenes.append({"id": "scene-03-brand-outro", "image": "images/mamase-outro.png", "narration": "แล้วคุณคิดว่าอย่างไร", "motion": "none", "role": "outro"})
    data = {"project": {"id": "reel", "title": "Reel", "language": "th-TH"}, "scenes": scenes}
    if outro is not None:
        data["outro"] = outro
    return Script.model_validate(data)


def test_legacy_outro_narration_moves_to_final_content_scene():
    migrated, image = migrate_legacy_outro_scene(make_script(legacy=True))
    assert len(migrated.scenes) == 2
    assert migrated.scenes[-1].image == "images/02.png"
    assert migrated.scenes[-1].narration == "คำถามสุดท้าย แล้วคุณคิดว่าอย่างไร"
    assert migrated.scenes[-1].subtitle == "คำถามสุดท้าย แล้วคุณคิดว่าอย่างไร"
    assert image == "images/mamase-outro.png"


def test_new_outro_is_not_a_narration_scene():
    script = make_script(outro={"enabled": True, "duration": 2.0})
    migrated, legacy = migrate_legacy_outro_scene(script)
    assert legacy is None
    assert len(migrated.scenes) == 2
    assert not hasattr(script.outro, "narration")


def test_missing_outro_config_uses_saved_default(tmp_path: Path):
    image = tmp_path / "reels-end-scene.png"
    image.write_bytes(b"png")
    resolved = resolve_reel_outro(make_script(), tmp_path, ReelOutroSettings(image=image))
    assert resolved.enabled is True
    assert resolved.duration == 2.0
    assert resolved.image == image


def test_disabled_outro_needs_no_image(tmp_path: Path):
    resolved = resolve_reel_outro(
        make_script(outro={"enabled": False}),
        tmp_path,
        ReelOutroSettings(image=tmp_path / "missing.png"),
    )
    assert resolved.enabled is False
    assert resolved.image is None


def test_custom_duration_is_respected(tmp_path: Path):
    image = tmp_path / "custom.png"
    image.write_bytes(b"png")
    script = make_script(outro={"enabled": True, "image": "custom.png", "duration": 2.4})
    assert resolve_reel_outro(script, tmp_path, ReelOutroSettings(image=tmp_path / "missing.png")).duration == 2.4


def test_missing_outro_image_has_clear_error(tmp_path: Path):
    with pytest.raises(AppError) as error:
        resolve_reel_outro(make_script(), tmp_path, ReelOutroSettings(image=tmp_path / "missing.png"))
    assert error.value.code == "REEL_OUTRO_ASSET_NOT_FOUND"
