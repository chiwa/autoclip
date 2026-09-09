from __future__ import annotations

from io import BytesIO
import json
import zipfile

import pytest

from app.services.job_service import scene_render_engine, wan_frames_for_duration
from app.services.ltx_service import ltx_frames_for_duration, RunpodLtxClient
from app.config.settings import AppSettings, Settings, load_settings
from app.domain.enums import JobStatus
from app.domain.errors import AppError
from app.domain.models import JobRecord, Script
from app.services.job_service import JobService
from app.services.persistence import Persistence
from app.services.wan_service import ComfyWanClient


class Upload:
    def __init__(self, body: bytes = b"zip"):
        self.file = BytesIO(body)


class NoopExecutor:
    def submit(self, *_args, **_kwargs):
        return None


def build_service(tmp_path) -> JobService:
    service = JobService(Settings(app=AppSettings(workspace=tmp_path / "workspaces")))
    service.executor = NoopExecutor()
    return service


def test_submit_records_selected_ffmpeg_motion_engine(tmp_path):
    service = build_service(tmp_path)

    record = service.submit(Upload(), tts_provider="dummy", render_engine="ffmpeg_motion")

    assert record.render_engine == "ffmpeg_motion"
    latest = service.registry.get(record.job_id)
    assert any("Render engine selected: ffmpeg_motion" in item["message"] for item in latest.logs)


def test_submit_rejects_unknown_render_engine(tmp_path):
    service = build_service(tmp_path)

    with pytest.raises(AppError, match="render engine") as error:
        service.submit(Upload(), tts_provider="dummy", render_engine="not-a-renderer")

    assert error.value.code == "RENDER_ENGINE_INVALID"


def test_wan_frame_count_covers_narration_even_when_package_requests_81_frames():
    # 7.85 seconds at Wan's 16 fps needs 129 frames (4k+1), not the package's
    # conventional 81-frame default, otherwise FFmpeg has to loop the shot.
    assert wan_frames_for_duration(7.85, requested_frames=81) == 129


def test_wan_frame_count_preserves_a_longer_package_request_and_4k_plus_one_shape():
    assert wan_frames_for_duration(5.0, requested_frames=101) == 101


def test_wan_steps_default_to_22_but_a_scene_can_request_25():
    settings = Settings()
    scene = Script.model_validate({
        "project": {"id": "wan-steps", "title": "Wan steps", "language": "th-TH"},
        "voice": {"provider": "dummy", "voice": "test", "speed": 1},
        "scenes": [{"id": "hook", "image": "images/hook.png", "narration": "ทดสอบ", "motion": "none", "wan": {"prompt": "Cinematic science hook", "steps": 25}}],
    }).scenes[0]
    client = ComfyWanClient(settings)
    assert settings.wan.steps == 22
    assert (settings.wan.width, settings.wan.height) == (640, 1152)
    assert client._workflow("job", scene, "hook.png")["9"]["inputs"]["steps"] == 25
    scene.wan.steps = None
    assert client._workflow("job", scene, "hook.png")["9"]["inputs"]["steps"] == 22


def test_ffmpeg_selection_overrides_wan_plan_for_every_scene():
    scene = Script.model_validate({
        "project": {"id": "hybrid", "title": "Hybrid", "language": "th-TH"},
        "voice": {"provider": "dummy", "voice": "test", "speed": 1},
        "scenes": [{"id": "hero", "image": "images/hero.png", "narration": "ทดสอบ", "motion": "none", "wan": {"prompt": "Cosmic particles move"}}],
    }).scenes[0]

    assert scene_render_engine("ffmpeg_motion", scene) == "ffmpeg_motion"


def test_wan_selection_is_hybrid_based_on_optional_wan_object():
    scenes = Script.model_validate({
        "project": {"id": "hybrid", "title": "Hybrid", "language": "th-TH"},
        "voice": {"provider": "dummy", "voice": "test", "speed": 1},
        "scenes": [
            {"id": "ai", "image": "images/ai.png", "narration": "ทดสอบ", "motion": "none", "wan": {"prompt": "Cosmic particles move"}},
            {"id": "still", "image": "images/still.png", "narration": "ทดสอบ", "motion": "slow_zoom_in"},
        ],
    }).scenes

    assert [scene_render_engine("wan2.2", scene) for scene in scenes] == ["wan2.2", "ffmpeg_motion"]


def test_submit_records_selected_output_format(tmp_path):
    service = build_service(tmp_path)
    archive = BytesIO()
    with zipfile.ZipFile(archive, "w") as package:
        package.writestr("script.json", json.dumps({
            "project": {"id": "format-test", "title": "Format", "language": "th-TH"},
            "voice": {"provider": "dummy", "voice": "test", "speed": 1},
            "scenes": [{"id": "scene", "image": "images/scene.png", "narration": "ทดสอบ", "motion": "none"}],
        }))
        package.writestr("images/scene.png", b"not-rendered-in-this-test")

    record = service.submit(Upload(archive.getvalue()), tts_provider="dummy", output_format="youtube")

    assert record.output_format == "youtube"
    assert record.api_dict()["outputFormat"] == "youtube"
    with zipfile.ZipFile(service.workspaces.root / record.job_id / "source" / "input.zip") as package:
        assert json.loads(package.read("script.json"))["project"]["resolution"] == "1920x1080"


def test_render_engine_is_persisted_with_job(tmp_path):
    settings = Settings(app=AppSettings(workspace=tmp_path / "workspaces"))
    persistence = Persistence(settings.app.workspace)
    service = JobService(settings, persistence=persistence)
    service.executor = NoopExecutor()

    record = service.submit(Upload(), tts_provider="dummy", render_engine="wan2.2")

    assert persistence.get_job(record.job_id)["render_engine"] == "wan2.2"


def test_native_wan_settings_are_read_from_dotenv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "AUTOCLIP_WAN_ENABLED=true\n"
        "AUTOCLIP_WAN_COMFY_URL=http://127.0.0.1:18188\n"
        "AUTOCLIP_WAN_REQUEST_TIMEOUT_SECONDS=240\n",
        encoding="utf-8",
    )

    settings = load_settings(tmp_path / "config.yaml")

    assert settings.wan.enabled is True
    assert settings.wan.comfy_url == "http://127.0.0.1:18188"
    assert settings.wan.request_timeout_seconds == 240


def test_ffmpeg_scene_parallelism_defaults_to_two_and_reads_dotenv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert load_settings(tmp_path / "config.yaml").video.ffmpeg_scene_parallelism == 2
    (tmp_path / ".env").write_text("AUTOCLIP_FFMPEG_SCENE_PARALLELISM=3\n", encoding="utf-8")
    assert load_settings(tmp_path / "config.yaml").video.ffmpeg_scene_parallelism == 3


def test_wan_selection_fails_explicitly_until_connector_is_enabled(tmp_path, monkeypatch):
    service = build_service(tmp_path)
    job_id = "wan-not-configured"
    workspace = service.workspaces.create(job_id)
    service.registry.set(JobRecord(job_id=job_id, status=JobStatus.RECEIVED, progress=0, current_step="Upload received", render_engine="wan2.2"))
    script = Script.model_validate({
        "project": {"id": "lake-natron", "title": "Lake Natron", "language": "th-TH"},
        "voice": {"provider": "dummy", "voice": "test", "speed": 1},
        "scenes": [{"id": "scene-01", "image": "images/scene-01.png", "narration": "ทดสอบ", "motion": "none", "wan": {"prompt": "Wan connection test"}}],
    })

    class FakePackageService:
        def __init__(self, *_args):
            pass

        def extract_and_validate(self, *_args):
            return script, workspace.extracted / "bgm.wav"

    monkeypatch.setattr("app.services.job_service.PackageService", FakePackageService)

    service._process(job_id, workspace)

    record = service.registry.get(job_id)
    assert record.status == JobStatus.FAILED
    assert record.error["code"] == "WAN_NOT_CONFIGURED"
    assert not any("Generating narration" in item["message"] for item in record.logs)


def test_submit_applies_motion_resolution_2k_and_4k(tmp_path):
    service = build_service(tmp_path)
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("script.json", json.dumps({
            "project": {"id": "test", "title": "Test", "language": "th-TH", "resolution": "1080x1920"},
            "voice": {"provider": "dummy", "voice": "test", "speed": 1},
            "scenes": [{"id": "scene-01", "image": "images/scene-01.png", "narration": "ทดสอบ", "motion": "none"}],
        }))
    buffer.seek(0)

    record_2k = service.submit(Upload(buffer.getvalue()), tts_provider="dummy", render_engine="ffmpeg_motion", motion_resolution="2k")
    zip_2k = service.workspaces.root / record_2k.job_id / "source" / "input.zip"
    with zipfile.ZipFile(zip_2k) as zf:
        patched = json.loads(zf.read("script.json"))
        assert patched["project"]["resolution"] == "1440x2560"

    record_4k = service.submit(Upload(buffer.getvalue()), tts_provider="dummy", render_engine="ffmpeg_motion", motion_resolution="4k")
    zip_4k = service.workspaces.root / record_4k.job_id / "source" / "input.zip"
    with zipfile.ZipFile(zip_4k) as zf:
        patched = json.loads(zf.read("script.json"))
        assert patched["project"]["resolution"] == "2160x3840"


def test_ltx_frame_count_covers_narration_and_respects_8n_plus_1():
    # 7.85s at 15 fps = 118 raw frames -> n = ceil((118-1)/8) = ceil(117/8) = 15 -> 15*8+1 = 121 frames
    # 121 frames / 15 fps = 8.067s >= 7.85s
    assert ltx_frames_for_duration(7.85) == 121
    # 3.0s at 15 fps = 45 frames -> n = ceil(44/8) = 6 -> 6*8+1 = 49 frames
    assert ltx_frames_for_duration(3.0) == 49
    # 0.5s at 15 fps = 8 frames -> n = ceil(7/8) = 1 -> 1*8+1 = 9 frames
    assert ltx_frames_for_duration(0.5) == 9
    # Preserves longer requested frames: 5.0s requires 73 frames; requested 97 (8*12+1) -> 97 frames
    assert ltx_frames_for_duration(5.0, requested_frames=97) == 97
    # If requested is not an 8n+1 multiple, round up to 8n+1: requested 80 -> 81 (8*10+1)
    assert ltx_frames_for_duration(5.0, requested_frames=80) == 81


def test_scene_model_supports_both_ltx_and_wan_keys():
    scene_from_wan = Script.model_validate({
        "project": {"id": "test-wan", "title": "Test", "language": "th-TH"},
        "voice": {"provider": "dummy", "voice": "test", "speed": 1},
        "scenes": [{"id": "s1", "image": "images/s1.png", "narration": "ทดสอบ", "motion": "none", "wan": {"prompt": "A cosmic nebula", "steps": 8}}],
    }).scenes[0]
    assert scene_from_wan.wan is not None
    assert scene_from_wan.ltx is not None
    assert scene_from_wan.ltx.prompt == "A cosmic nebula"
    assert scene_from_wan.ltx.steps == 8

    scene_from_ltx = Script.model_validate({
        "project": {"id": "test-ltx", "title": "Test", "language": "th-TH"},
        "voice": {"provider": "dummy", "voice": "test", "speed": 1},
        "scenes": [{"id": "s2", "image": "images/s2.png", "narration": "ทดสอบ", "motion": "none", "ltx": {"prompt": "A solar flare", "frames": 49}}],
    }).scenes[0]
    assert scene_from_ltx.ltx is not None
    assert scene_from_ltx.wan is not None
    assert scene_from_ltx.wan.prompt == "A solar flare"
    assert scene_from_ltx.wan.frames == 49


def test_scene_render_engine_handles_ltx_hybrid_and_fallbacks():
    scene_ai = Script.model_validate({
        "project": {"id": "test", "title": "Test", "language": "th-TH"},
        "voice": {"provider": "dummy", "voice": "test", "speed": 1},
        "scenes": [{"id": "s1", "image": "images/s1.png", "narration": "ทดสอบ", "motion": "none", "ltx": {"prompt": "Star formation"}}],
    }).scenes[0]
    scene_still = Script.model_validate({
        "project": {"id": "test", "title": "Test", "language": "th-TH"},
        "voice": {"provider": "dummy", "voice": "test", "speed": 1},
        "scenes": [{"id": "s2", "image": "images/s2.png", "narration": "ทดสอบ", "motion": "slow_zoom_in"}],
    }).scenes[0]

    assert scene_render_engine("ltx", scene_ai) == "ltx"
    assert scene_render_engine("ltx", scene_still) == "ffmpeg_motion"
    assert scene_render_engine("ffmpeg_motion", scene_ai) == "ffmpeg_motion"
    assert scene_render_engine("wan2.2", scene_ai) == "wan2.2"


def test_submit_records_selected_ltx_engine(tmp_path):
    service = build_service(tmp_path)
    record = service.submit(Upload(), tts_provider="dummy", render_engine="ltx")

    assert record.render_engine == "ltx"
    latest = service.registry.get(record.job_id)
    assert any("Render engine selected: ltx" in item["message"] for item in latest.logs)


def test_ltx_settings_read_from_dotenv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "AUTOCLIP_LTX_ENABLED=true\n"
        "AUTOCLIP_LTX_RUNPOD_HOST=100.200.30.40\n"
        "AUTOCLIP_LTX_RUNPOD_PORT=2222\n"
        "AUTOCLIP_LTX_STEPS=8\n",
        encoding="utf-8",
    )

    settings = load_settings(tmp_path / "config.yaml")
    assert settings.ltx.enabled is True
    assert settings.ltx.runpod_host == "100.200.30.40"
    assert settings.ltx.runpod_port == 2222
    assert settings.ltx.steps == 8


def test_job_service_retry(tmp_path):
    service = build_service(tmp_path)
    record = service.submit(Upload(), tts_provider="dummy", render_engine="ffmpeg_motion")
    service.registry.update(record.job_id, JobStatus.FAILED, 40, "Rendering failed", {"code": "SCENE_RENDER_FAILED", "message": "Failed"})

    retried = service.retry(record.job_id)
    assert retried.status == JobStatus.RECEIVED
    assert retried.progress == 5
    assert retried.error is None
    latest = service.registry.get(record.job_id)
    assert any("กำลังเริ่มประมวลผลใหม่อีกครั้ง" in item["message"] for item in latest.logs)
