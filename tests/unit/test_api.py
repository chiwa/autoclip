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
