from fastapi.testclient import TestClient

from app.main import app
from app.infrastructure.tts.providers import DummyTtsProvider


client = TestClient(app)


def test_unknown_job():
    response = client.get("/api/jobs/nope")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "JOB_NOT_FOUND"


def test_video_not_ready():
    record = app.state.job_service.registry.create("waiting")
    response = client.get(f"/api/jobs/{record.job_id}/video")
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "VIDEO_NOT_READY"


def test_reject_non_zip():
    response = client.post("/api/jobs", files={"file": ("bad.txt", b"x", "text/plain")})
    assert response.status_code == 400


def test_sse_unknown_job():
    response = client.get("/api/jobs/missing/events")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "JOB_NOT_FOUND"


def test_sse_completed_snapshot_includes_progress_log_and_completed():
    registry = app.state.job_service.registry
    registry.create("done")
    registry.add_log("done", "SUCCESS", "Video generation completed")
    registry.update("done", "COMPLETED", 100, "Video is ready")
    response = client.get("/api/jobs/done/events")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: progress" in response.text
    assert "event: log" in response.text
    assert "event: completed" in response.text


def test_sse_failed_snapshot_is_user_safe():
    registry = app.state.job_service.registry
    registry.create("failed")
    registry.add_log("failed", "ERROR", "Package is invalid")
    registry.update("failed", "FAILED", 5, "Validating ZIP package", {"code": "PACKAGE_INVALID", "message": "Package is invalid"})
    response = client.get("/api/jobs/failed/events")
    assert "event: failed" in response.text
    assert "PACKAGE_INVALID" in response.text
    assert "Traceback" not in response.text


def test_completed_snapshot_exposes_metadata():
    registry = app.state.job_service.registry
    registry.create("metadata")
    registry.set_metadata("metadata", {"projectTitle": "Lake Natron", "durationSeconds": 4.2, "resolution": "1080x1920", "sceneCount": 1, "fileSizeBytes": 123, "createdAt": "2026-08-30T10:33:15+07:00"})
    registry.update("metadata", "COMPLETED", 100, "Video is ready")
    response = client.get("/api/jobs/metadata")
    assert response.json()["metadata"]["resolution"] == "1080x1920"


def test_job_preview_can_read_and_change_publish_status():
    project_id = "preview-publication-project"
    job_id = "preview-publication-job"
    app.state.persistence.ensure_project(project_id, "Preview publication", 1, project_type="reel")
    record = app.state.job_service.registry.create(job_id)
    app.state.job_service.registry.set_project(record.job_id, project_id)

    initial = client.get(f"/api/jobs/{job_id}/publication")
    assert initial.status_code == 200
    assert initial.json()["projectId"] == project_id

    changed = client.patch(f"/api/jobs/{job_id}/publication", json={"published": True})
    assert changed.status_code == 200
    assert changed.json()["published"] is True
    assert app.state.persistence.get_published(project_id) is True

    restored = client.patch(f"/api/jobs/{job_id}/publication", json={"published": False})
    assert restored.status_code == 200
    assert restored.json()["published"] is False
    app.state.persistence.delete_project(project_id)


def test_channels_can_be_created_renamed_and_assigned_from_preview():
    created = client.post("/api/channels", json={"name": "API Channel"})
    assert created.status_code == 201
    channel_id = created.json()["id"]
    project_id = "preview-channel-project"
    try:
        renamed = client.patch(f"/api/channels/{channel_id}", json={"name": "API Channel Renamed"})
        assert renamed.status_code == 200
        job_id = "preview-channel-job"
        app.state.persistence.ensure_project(project_id, "Preview channel", 1)
        record = app.state.job_service.registry.create(job_id)
        app.state.job_service.registry.set_project(record.job_id, project_id)
        changed = client.patch(f"/api/jobs/{job_id}/channel", json={"channelId": channel_id})
        assert changed.status_code == 200
        assert changed.json()["channelName"] == "API Channel Renamed"
        current = client.get(f"/api/jobs/{job_id}/channel")
        assert current.json()["channelId"] == channel_id
    finally:
        app.state.persistence.set_project_channel(project_id, "undefined")
        app.state.persistence.delete_unused_channel(channel_id)
        app.state.persistence.delete_project(project_id)


def test_restore_replaces_stale_failed_memory_job_with_repaired_completed_record(tmp_path):
    from app.services.job_service import JobService
    from app.services.persistence import Persistence
    from app.domain.models import JobRecord

    settings = app.state.settings.model_copy(deep=True)
    settings.app.workspace = tmp_path
    persistence = Persistence(tmp_path)
    video = tmp_path / "repair" / "output" / "final.mp4"
    video.parent.mkdir(parents=True)
    video.write_bytes(b"video")
    service = JobService(settings, persistence=persistence)
    record = service.registry.create("repaired")
    service.registry.update(record.job_id, "FAILED", 92, "Creating final video", {"code": "VIDEO_COMPOSITION_FAILED"})
    repaired = service.registry.get(record.job_id).model_copy(update={"status": "COMPLETED", "progress": 100, "error": None})
    persistence.upsert_job(repaired, final_path=video)

    restored = service.restore(record.job_id)

    assert restored is not None
    assert restored.status == "COMPLETED"
    assert service.final_video(record.job_id) == video


def test_thai_tts_returns_downloadable_wav(monkeypatch):
    monkeypatch.setattr(app.state.tts_preview_service, "provider", DummyTtsProvider())
    response = client.post(
        "/api/tts",
        data={"text": "คุณเชื่อไหม เรื่องนี้มีอยู่จริงบนโลกของเรา", "voice": "thai-male-01", "speed": "1.0"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert "autoclip-thai-speech.wav" in response.headers["content-disposition"]
    assert response.content.startswith(b"RIFF")


def test_thai_tts_rejects_empty_text():
    response = client.post("/api/tts", data={"text": "   "})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "TTS_GENERATION_FAILED"


def test_thai_tts_rejects_unsupported_speed():
    response = client.post("/api/tts", data={"text": "สวัสดี", "speed": "3.0"})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "TTS_GENERATION_FAILED"


def test_retry_unknown_job():
    response = client.post("/api/jobs/missing-job/retry")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "JOB_NOT_FOUND"


def test_retry_non_failed_job():
    registry = app.state.job_service.registry
    registry.create("running-job")
    registry.update("running-job", "RENDERING_SCENES", 50, "Rendering scene")
    response = client.post("/api/jobs/running-job/retry")
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "JOB_NOT_RETRYABLE"


def test_job_thumbnail_missing_returns_404():
    response = client.get("/api/jobs/non-existent-job/thumbnail")
    assert response.status_code == 404
