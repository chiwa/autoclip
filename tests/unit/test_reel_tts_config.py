from app.config.settings import ReelTtsSettings, Settings
from app.domain.models import Script
from app.services.reel_tts_config import (
    MAMASE_REEL_HOOK_STYLE,
    MAMASE_REEL_NORMAL_STYLE,
    resolve_reel_tts_config,
)


def script_data(*, reel_tts=None, scenes=3, resolution="1080x1920"):
    data = {
        "project": {"id": "mamase-test-reel", "title": "Test", "language": "th-TH", "resolution": resolution},
        "voice": {"provider": "google-gemini", "voice": "Legacy", "speed": 0.9, "style_prompt": "legacy style"},
        "scenes": [
            {"id": f"scene-{index + 1:02d}", "image": f"images/{index + 1:02d}.png", "narration": f"scene {index + 1}", "motion": "none"}
            for index in range(scenes)
        ],
    }
    if reel_tts is not None:
        data["reel_tts"] = reel_tts
    return data


def test_old_reel_json_uses_hook_then_normal_defaults():
    settings = Settings()
    script = Script.model_validate(script_data())

    hook = resolve_reel_tts_config(script, 0, settings.reel_tts, settings.tts)
    normal = resolve_reel_tts_config(script, 1, settings.reel_tts, settings.tts)

    assert (hook.mode, hook.voice, hook.speed, hook.style) == ("HOOK", "Fenrir", 1.10, MAMASE_REEL_HOOK_STYLE)
    assert (normal.mode, normal.voice, normal.speed, normal.style) == ("NORMAL", "Fenrir", 1.05, MAMASE_REEL_NORMAL_STYLE)


def test_job_override_is_used_without_mutating_saved_defaults():
    saved = ReelTtsSettings(voice="Fenrir", hook_speed=1.10, normal_speed=1.05)
    settings = Settings(reel_tts=saved)
    script = Script.model_validate(script_data(reel_tts={
        "voice": "Iapetus",
        "hook": {"speed": 1.2, "style": "custom hook"},
        "normal": {"speed": 0.95, "style": "custom normal"},
    }))

    hook = resolve_reel_tts_config(script, 0, saved, settings.tts)
    normal = resolve_reel_tts_config(script, 2, saved, settings.tts)

    assert (hook.voice, hook.speed, hook.style, hook.source) == ("Iapetus", 1.2, "custom hook", "job")
    assert (normal.voice, normal.speed, normal.style, normal.source) == ("Iapetus", 0.95, "custom normal", "job")
    assert saved == ReelTtsSettings(voice="Fenrir", hook_speed=1.10, normal_speed=1.05)


def test_single_scene_is_hook():
    settings = Settings()
    script = Script.model_validate(script_data(scenes=1))
    assert resolve_reel_tts_config(script, 0, settings.reel_tts, settings.tts).mode == "HOOK"


def test_empty_hook_style_and_missing_speed_fall_back_to_job_normal():
    settings = Settings()
    script = Script.model_validate(script_data(reel_tts={
        "hook": {"style": "   "},
        "normal": {"speed": 0.95, "style": "normal override"},
    }))
    hook = resolve_reel_tts_config(script, 0, settings.reel_tts, settings.tts)
    assert hook.speed == 0.95
    assert hook.style == "normal override"


def test_invalid_hook_speed_falls_back_to_normal_speed():
    settings = Settings()
    script = Script.model_validate(script_data(reel_tts={
        "hook": {"speed": "too-fast"},
        "normal": {"speed": 1.0},
    }))
    assert resolve_reel_tts_config(script, 0, settings.reel_tts, settings.tts).speed == 1.0


def test_old_saved_settings_load_with_new_hook_defaults():
    saved = ReelTtsSettings.model_validate({"voice": "Fenrir", "normal_speed": 1.0})
    assert saved.hook_speed == 1.10
    assert saved.hook_style is None


def test_reel_tts_is_optional_and_does_not_change_scene_contract():
    old_script = Script.model_validate(script_data())
    new_script = Script.model_validate(script_data(reel_tts={"voice": "Fenrir"}))
    assert old_script.reel_tts is None
    assert new_script.scenes[0].image == old_script.scenes[0].image
    assert new_script.scenes[0].subtitle == old_script.scenes[0].subtitle


def test_preferred_reel_tts_json_can_omit_legacy_voice_block():
    data = script_data(reel_tts={"voice": "Fenrir"})
    data.pop("voice")
    script = Script.model_validate(data)
    assert script.voice.voice == "Fenrir"
    assert script.reel_tts.voice == "Fenrir"


def test_podcast_settings_are_untouched():
    settings = Settings()
    assert settings.podcast.default_voice == "Iapetus"
    assert settings.podcast.default_speed == 0.90
