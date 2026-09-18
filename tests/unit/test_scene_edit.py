from unittest.mock import patch
import json
import zipfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.config import load_settings
from app.domain.enums import JobStatus
from app.domain.models import JobRecord
from app.infrastructure.filesystem import WorkspaceManager
from app.main import app
from app.services.job_service import JobService

client = TestClient(app)


def _make_zip(path: Path, members: dict):
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in members.items():
            if isinstance(content, str):
                content = content.encode("utf-8")
            archive.writestr(name, content)


@pytest.fixture
def dummy_job_setup(tmp_path):
    settings = load_settings()
    settings.app.workspace = tmp_path / "workspaces"
    settings.app.workspace.mkdir(parents=True, exist_ok=True)
    wm = WorkspaceManager(settings.app.workspace)
    job_id = "test-scene-edit-01"
    workspace = wm.create(job_id)

    script_data = {
        "project": {"id": "test-proj", "title": "Test Project", "language": "th-TH"},
        "voice": {"provider": "dummy", "voice": "test", "speed": 1.0},
        "scenes": [
            {
                "id": "scene-01",
                "image": "images/scene-01.png",
                "narration": "ซีนที่หนึ่งข้อความเดิม",
                "subtitle": "ซีนที่หนึ่งข้อความเดิม",
                "motion": "gentle_float",
            },
            {
                "id": "scene-02",
                "image": "images/scene-02.png",
                "narration": "ซีนที่สองข้อความเดิม",
                "subtitle": "ซีนที่สองข้อความเดิม",
                "motion": "cinematic_push_in",
            },
        ],
    }

    (workspace.extracted / "images").mkdir(parents=True, exist_ok=True)
    (workspace.extracted / "script.json").write_text(json.dumps(script_data, ensure_ascii=False), encoding="utf-8")
    (workspace.extracted / "images" / "scene-01.png").write_bytes(b"PNG-01")
    (workspace.extracted / "images" / "scene-02.png").write_bytes(b"PNG-02")

    _make_zip(
        workspace.source / "input.zip",
        {
            "script.json": json.dumps(script_data, ensure_ascii=False),
            "images/scene-01.png": b"PNG-01",
            "images/scene-02.png": b"PNG-02",
        },
    )

    (workspace.generated_audio / "scene-01.wav").write_bytes(b"WAV-01" * 200)
    (workspace.generated_audio / "scene-02.wav").write_bytes(b"WAV-02" * 200)
    (workspace.rendered_scenes / "scene-01.mp4").write_bytes(b"MP4-01" * 200)
    (workspace.rendered_scenes / "scene-02.mp4").write_bytes(b"MP4-02" * 200)
    (workspace.output / "final.mp4").write_bytes(b"FINAL-MP4" * 200)

    service = JobService(settings)
    record = JobRecord(
        job_id=job_id,
        status=JobStatus.COMPLETED,
        progress=100,
        current_step="Video is ready",
        metadata={"projectTitle": "Test Project"},
    )
    service.registry.set(record)

    return service, job_id, workspace


def test_get_scenes(dummy_job_setup):
    service, job_id, workspace = dummy_job_setup
    result = service.get_scenes(job_id)

    assert result["jobId"] == job_id
    assert result["projectType"] == "reel"
    assert result["sceneCount"] == 2
    assert len(result["scenes"]) == 2

    s1 = result["scenes"][0]
    assert s1["id"] == "scene-01"
    assert s1["narration"] == "ซีนที่หนึ่งข้อความเดิม"
    assert s1["hasAudio"] is True
    assert s1["hasVideo"] is True
    assert s1["hasImage"] is True


def test_edit_scene_narration_invalidates_audio_and_video(dummy_job_setup):
    service, job_id, workspace = dummy_job_setup

    res = service.edit_scene(job_id, "scene-01", narration="ข้อความใหม่สำหรับซีน 1")

    assert res["status"] == "SCENE_UPDATED"
    assert res["audioInvalidated"] is True
    assert res["videoInvalidated"] is True

    assert not (workspace.generated_audio / "scene-01.wav").exists()
    assert not (workspace.rendered_scenes / "scene-01.mp4").exists()
    assert not (workspace.output / "final.mp4").exists()

    assert (workspace.generated_audio / "scene-02.wav").exists()
    assert (workspace.rendered_scenes / "scene-02.mp4").exists()

    script_after = json.loads((workspace.extracted / "script.json").read_text(encoding="utf-8"))
    assert script_after["scenes"][0]["narration"] == "ข้อความใหม่สำหรับซีน 1"


def test_edit_scene_image_preserves_audio(dummy_job_setup):
    service, job_id, workspace = dummy_job_setup

    res = service.edit_scene(
        job_id,
        "scene-02",
        image_bytes=b"NEW-PNG-02",
        image_filename="new_scene2.png",
    )

    assert res["status"] == "SCENE_UPDATED"
    assert res["audioInvalidated"] is False
    assert res["videoInvalidated"] is True

    assert (workspace.generated_audio / "scene-02.wav").exists()
    assert not (workspace.rendered_scenes / "scene-02.mp4").exists()
    assert (workspace.extracted / "images" / "scene-02.png").read_bytes() == b"NEW-PNG-02"


def test_edit_scene_motion_preserves_audio(dummy_job_setup):
    service, job_id, workspace = dummy_job_setup

    res = service.edit_scene(job_id, "scene-01", motion="cinematic_pull_out")

    assert res["audioInvalidated"] is False
    assert res["videoInvalidated"] is True
    assert (workspace.generated_audio / "scene-01.wav").exists()
    assert not (workspace.rendered_scenes / "scene-01.mp4").exists()


def test_api_scenes_and_edit_endpoint(monkeypatch, dummy_job_setup):
    service, job_id, workspace = dummy_job_setup
    monkeypatch.setattr(app.state, "job_service", service)

    resp = client.get(f"/api/jobs/{job_id}/scenes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["sceneCount"] == 2

    edit_resp = client.post(
        f"/api/jobs/{job_id}/scenes/scene-01/edit",
        json={"narration": "ผ่าน API แล้วนะ"},
    )
    assert edit_resp.status_code == 200
    edit_data = edit_resp.json()
    assert edit_data["status"] == "SCENE_UPDATED"
    assert edit_data["audioInvalidated"] is True

    img_resp = client.get(f"/api/jobs/{job_id}/scenes/scene-01/image")
    assert img_resp.status_code == 200
    assert img_resp.headers["content-type"].startswith("image/")


def test_re_render_calls_process(dummy_job_setup):
    service, job_id, workspace = dummy_job_setup
    with patch.object(service, "_process") as mock_process:
        res = service.re_render(job_id)
        assert res.job_id == job_id
        # Wait slightly or check submit
        assert service.registry.get(job_id).status == JobStatus.RECEIVED


def test_swap_podcast_cover(tmp_path):
    settings = load_settings()
    settings.app.workspace = tmp_path / "workspaces"
    settings.app.workspace.mkdir(parents=True, exist_ok=True)
    wm = WorkspaceManager(settings.app.workspace)
    job_id = "test-pc-swap"
    workspace = wm.create(job_id)

    (workspace.source / "script.txt").write_text("Thai podcast script", encoding="utf-8")
    (workspace.source / "cover.png").write_bytes(b"OLD-COVER")
    (workspace.source / "podcast-settings.json").write_text(json.dumps({"title": "Test Pod"}), encoding="utf-8")
    (workspace.source / "motion_cycle.mp4").write_bytes(b"OLD-CYCLE")

    service = JobService(settings)
    record = JobRecord(job_id=job_id, status=JobStatus.COMPLETED, progress=100, current_step="Ready")
    service.registry.set(record)

    with patch.object(service, "_process_podcast") as mock_pc:
        res = service.swap_podcast_cover(job_id, b"NEW-COVER-BYTES", "new_art.jpg")
        assert res["status"] == "COVER_SWAPPED"
        # Verify old cycle removed
        assert not (workspace.source / "motion_cycle.mp4").exists()
        # Verify new cover written
        assert (workspace.source / "cover.jpg").read_bytes() == b"NEW-COVER-BYTES"
