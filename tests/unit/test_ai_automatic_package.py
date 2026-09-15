from __future__ import annotations

import json
import zipfile
from pathlib import Path

from app.config.settings import AppSettings, ReelHookGateSettings, Settings, load_settings
from app.domain.ai_models import AiProjectStatus, AiScene
from app.services.ai_service import AiProjectService, AntigravityAutoProvider, GeminiAutoProvider


def test_gemini_key_is_loaded_from_dotenv_without_exposing_it(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("GEMINI_API_KEY=test-key\n", encoding="utf-8")

    settings = load_settings(tmp_path / "config.yaml")

    assert settings.gemini_api_key == "test-key"


def test_gemini_key_accepts_legacy_compose_style_dotenv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("GEMINI_API_KEY: test-key\n", encoding="utf-8")

    assert load_settings(tmp_path / "config.yaml").gemini_api_key == "test-key"


def test_automatic_package_builder_writes_metadata_tts_and_wan(tmp_path):
    settings = Settings(
        app=AppSettings(workspace=tmp_path / "workspaces"),
        reel_hook_gate=ReelHookGateSettings(enabled=False),
    )
    service = AiProjectService(settings)
    project = service.create("เรื่องทดสอบ")
    image = service.root / project.project_id / "preview-images" / "scene-01.png"
    image.parent.mkdir(parents=True)
    image.write_bytes((Path("assets/characters/mamase-presenter-v1.png")).read_bytes())
    project.scenes = [AiScene(
        id="scene-01",
        narration="เจมส์ เว็บบ์ กำลังมองย้อนอดีตของจักรวาล",
        tts_text="เจมส์ เว็บบ์ กำลังมองย้อนอดีตของจักรวาล",
        image_prompt="test",
        image_path="preview-images/scene-01.png",
        motion="cinematic_push_in",
        wan={"prompt": "test", "frames": 81, "steps": 25},
    )]
    project.revision = 1
    project.confirmed_revision = 1
    project.status = AiProjectStatus.PREVIEW_CONFIRMED
    service._save(project)

    package = service.build_package(project.project_id)

    with zipfile.ZipFile(package) as archive:
        script = json.loads(archive.read("script.json"))
        metadata = json.loads(archive.read("video-metadata.json"))
        assert script["voice"]["provider"] == "google-gemini"
        assert script["voice"]["voice"] == "Fenrir"
        assert script["voice"]["speed"] == 1.05
        assert script["scenes"][0]["tts_text"].startswith("เจมส์")
        assert script["scenes"][0]["wan"]["steps"] == 25
        assert metadata["title"] == "เรื่องทดสอบ"
    completed = service.get(project.project_id)
    assert completed.package_summary["validated"] is True
    assert completed.package_summary["wanReadyScenes"] == 1


def test_ai_scene_validation_accepts_transitions_promised_to_gemini(tmp_path):
    service = AiProjectService(Settings(app=AppSettings(workspace=tmp_path / "workspaces")))
    scenes = service._validate_scenes([AiScene(
        id="scene-01",
        narration="ทดสอบ",
        image_prompt="test",
        motion="cinematic_push_in",
        transition="smooth_left",
    )])

    assert scenes[0].transition == "smooth_left"


def test_gemini_planner_normalises_harmless_scene_format_errors():
    provider = GeminiAutoProvider(Settings(gemini_api_key="test-key"))
    notes: list[str] = []

    scene = provider._normalise_scene({
        "id": "Scene 1 / Hook",
        "narration": "เรื่องทดสอบ",
        "motion": "dramatic_spin",
        "transition": "glitch",
        "estimated_duration": "not-a-number",
    }, 1, notes)

    assert scene.id == "Scene-1-Hook"
    assert scene.motion == "cinematic_push_in"
    assert scene.transition == "fade"
    assert scene.estimated_duration == 5.0
    assert scene.wan["steps"] == 25
    assert len(notes) >= 4


def test_gemini_planner_preserves_selective_ellipses_in_tts_text():
    provider = GeminiAutoProvider(Settings(gemini_api_key="test-key"))

    scene = provider._normalise_scene({
        "id": "scene-01",
        "narration": "เว้นจังหวะได้ตามข้อความ",
        "tts_text": "ประโยคแรก... ประโยคต่อไป… และจบ",
    }, 1, [])

    assert scene.tts_text == "ประโยคแรก... ประโยคต่อไป… และจบ"


def test_editing_script_before_images_keeps_project_in_script_review(tmp_path):
    service = AiProjectService(Settings(app=AppSettings(workspace=tmp_path / "workspaces")))
    project = service.create("เรื่องทดสอบ")
    project.scenes = [AiScene(id="scene-01", narration="เดิม", image_prompt="prompt", motion="slow_zoom_in")]
    project.status = AiProjectStatus.SCRIPT_READY
    service._save(project)

    updated = service.update_scene(project.project_id, "scene-01", {"narration": "แก้แล้ว"})

    assert updated.status == AiProjectStatus.SCRIPT_READY
    assert updated.scenes[0].narration == "แก้แล้ว"


def test_provider_wait_wrapper_returns_a_fast_result(tmp_path):
    service = AiProjectService(Settings(app=AppSettings(workspace=tmp_path / "workspaces")))
    project = service.create("เรื่องทดสอบ")

    result = service._wait_with_heartbeat(project.project_id, "ทดสอบ", "รอ", lambda: "done")

    assert result == "done"


def test_gemini_defaults_use_current_flash_models():
    settings = Settings()

    assert settings.gemini_text_model == "gemini-3.6-flash"
    assert settings.gemini_image_model == "gemini-2.5-flash-image"


def test_google_tts_uses_approved_mamase_defaults():
    settings = Settings()

    assert settings.tts.google_voice == "Fenrir"
    assert settings.tts.google_speaking_rate == 1.05
    assert settings.tts.google_style_prompt.startswith("Read aloud in a natural, playful")
    assert settings.tts.silence_trim.enabled is False


def test_gemini_image_request_uses_image_config_not_legacy_response_format(tmp_path, monkeypatch):
    class Response:
        status_code = 200
        ok = True

        def json(self):
            return {"candidates": [{"content": {"parts": [{"inlineData": {"data": "cG5n"}}]}}]}

    captured = {}

    def post(url, **kwargs):
        captured.update(kwargs)
        return Response()

    monkeypatch.setattr("app.services.ai_service.requests.post", post)
    output = tmp_path / "image.png"
    GeminiAutoProvider(Settings(gemini_api_key="test-key")).image("test", output)

    config = captured["json"]["generationConfig"]
    assert config["imageConfig"] == {"aspectRatio": "9:16", "imageSize": "1K"}
    assert "responseFormat" not in config


def test_antigravity_is_the_default_automatic_provider(tmp_path):
    cli = tmp_path / "agy"
    cli.write_text("#!/bin/sh\n", encoding="utf-8")
    cli.chmod(0o755)
    settings = Settings(app=AppSettings(workspace=tmp_path / "workspaces"), antigravity_cli_path=cli)

    service = AiProjectService(settings)

    assert settings.ai_provider == "antigravity"
    assert settings.antigravity_model == "gemini-3.8-flash-medium"
    assert service.configured is True
    assert isinstance(service._automatic_provider(), AntigravityAutoProvider)


def test_antigravity_planner_normalises_json_without_gemini_key(tmp_path, monkeypatch):
    cli = tmp_path / "agy"
    cli.write_text("#!/bin/sh\n", encoding="utf-8")
    cli.chmod(0o755)
    provider = AntigravityAutoProvider(Settings(antigravity_cli_path=cli))
    monkeypatch.setattr(provider, "_run", lambda *args, **kwargs: json.dumps({"scenes": [{"id": "hook", "narration": "ทดสอบ", "image_prompt": "test"}]}))

    scenes, notes = provider.plan("เรื่องทดสอบ", "")

    assert scenes[0].id == "hook"
    assert scenes[0].wan["steps"] == 25
    assert notes


def test_antigravity_passes_prompt_as_print_flag_value(tmp_path, monkeypatch):
    cli = tmp_path / "agy"
    cli.write_text("#!/bin/sh\n", encoding="utf-8")
    cli.chmod(0o755)
    provider = AntigravityAutoProvider(Settings(antigravity_cli_path=cli))
    captured: dict[str, list[str]] = {}

    class Result:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(command, **_kwargs):
        captured["command"] = command
        return Result()

    monkeypatch.setattr("app.services.ai_service.subprocess.run", fake_run)

    assert provider._run("plan this", mode="plan") == "ok"
    command = captured["command"]
    assert "--output-format" in command
    assert "text" in command
    assert command[-1] == "--print=plan this"
    assert "--print" not in command
