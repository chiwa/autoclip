from __future__ import annotations

from io import BytesIO
import json
import zipfile

import pytest

from app.services.job_service import wan_frames_for_duration
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


def test_wan_selection_fails_explicitly_until_connector_is_enabled(tmp_path, monkeypatch):
    service = build_service(tmp_path)
    job_id = "wan-not-configured"
    workspace = service.workspaces.create(job_id)
    service.registry.set(JobRecord(job_id=job_id, status=JobStatus.RECEIVED, progress=0, current_step="Upload received", render_engine="wan2.2"))
    script = Script.model_validate({
        "project": {"id": "lake-natron", "title": "Lake Natron", "language": "th-TH"},
        "voice": {"provider": "dummy", "voice": "test", "speed": 1},
        "scenes": [{"id": "scene-01", "image": "images/scene-01.png", "narration": "ทดสอบ", "motion": "none"}],
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
