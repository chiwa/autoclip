from io import BytesIO
from unittest.mock import patch
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.config import load_settings

client = TestClient(app)


def test_podcast_page_route():
    response = client.get("/podcast")
    assert response.status_code == 200
    assert "AutoClip · สร้าง YouTube Podcast" in response.text
    assert "podcastForm" in response.text
    assert "Enceladus" in response.text
    assert "1.10" in response.text
    assert "1920×1080" in response.text
    assert "/static/podcast.js" in response.text


def test_podcast_settings_defaults():
    settings = load_settings()
    assert settings.podcast.default_voice == "Enceladus"
    assert settings.podcast.default_speed == 1.1
    assert settings.podcast.chunk_max_bytes == 1400
    assert settings.podcast.concurrency == 3
    assert settings.podcast.default_bgm_volume == 0.08
    assert "calm, warm, and gently formal Thai voice" in settings.podcast.default_style_prompt


def test_podcast_preview_audio(tmp_path):
    dummy_wav = tmp_path / "sample.wav"
    dummy_wav.write_bytes(b"RIFFdummywav")

    with patch.object(app.state.tts_preview_service, "synthesize", return_value=dummy_wav):
        response = client.post(
            "/api/podcast/preview-audio",
            data={
                "text": "สวัสดีครับ นี่คือเสียงตัวอย่าง",
                "voice": "Enceladus",
                "speed": "0.95",
                "style_prompt": "Gentle bedtime tone",
            },
        )
        assert response.status_code == 200
        assert response.content == b"RIFFdummywav"
        assert response.headers["content-type"] == "audio/wav"


def test_podcast_preview_audio_empty_text_uses_default(tmp_path):
    dummy_wav = tmp_path / "sample.wav"
    dummy_wav.write_bytes(b"RIFFfallbackwav")

    with patch.object(app.state.tts_preview_service, "synthesize", return_value=dummy_wav) as mock_synth:
        response = client.post("/api/podcast/preview-audio", data={"text": "   "})
        assert response.status_code == 200
        assert response.content == b"RIFFfallbackwav"
        assert mock_synth.called
        # Check that fallback text was passed
        args, kwargs = mock_synth.call_args
        assert "ยินดีต้อนรับ" in kwargs.get("text", "")


def test_podcast_submit_job_validation_empty_script():
    img = Image.new("RGB", (100, 100), color="blue")
    img_buf = BytesIO()
    img.save(img_buf, format="JPEG")
    img_bytes = img_buf.getvalue()

    response = client.post(
        "/api/podcast/jobs",
        data={"title": "Test Podcast", "script": "   ", "voice": "Enceladus"},
        files={"cover_image": ("cover.jpg", img_bytes, "image/jpeg")},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "PODCAST_SCRIPT_EMPTY"


def test_podcast_submit_job_success():
    img = Image.new("RGB", (1920, 1080), color="darkblue")
    img_buf = BytesIO()
    img.save(img_buf, format="PNG")
    img_bytes = img_buf.getvalue()

    with patch.object(app.state.job_service, "submit_podcast") as mock_submit:
        record = app.state.job_service.registry.create("podcast-test-job")
        mock_submit.return_value = record

        response = client.post(
            "/api/podcast/jobs",
            data={
                "title": "มหาสมุทรบนเอนเซลาดัส",
                "script": "ใต้ผืนน้ำแข็งอันหนาวเหน็บ มีมหาสมุทรน้ำเหลวซ่อนอยู่",
                "voice": "Enceladus",
                "speed": "0.95",
                "style_prompt": "Bedtime tone",
                "enable_subtitles": "true",
                "bgm_volume": "0.08",
            },
            files={"cover_image": ("cover.png", img_bytes, "image/png")},
        )
        assert response.status_code == 202
        data = response.json()
        assert data["jobId"] == "podcast-test-job"
        assert data["status"] == "RECEIVED"
        assert mock_submit.called


def test_podcast_bgm_tracks_catalog():
    response = client.get("/api/podcast/bgm-tracks")
    assert response.status_code == 200
    data = response.json()
    assert "tracks" in data
    tracks = data["tracks"]
    track_ids = [t["id"] for t in tracks]
    assert "space.mp3" in track_ids
    space_track = next(t for t in tracks if t["id"] == "space.mp3")
    assert space_track["is_default"] is True
    # Existing built-in tracks are also present
    assert "cosmic_drift" in track_ids
    assert "starlight_lullaby" in track_ids
    assert "deep_nebula" in track_ids
    assert "interstellar_voyage" in track_ids
    assert "enceladus_ocean" in track_ids


def test_podcast_bgm_preview(tmp_path):
    dummy_wav = tmp_path / "space.mp3"
    dummy_wav.write_bytes(b"ID3dummybgmmp3")

    with patch("app.api.routes.resolve_podcast_bgm", return_value=dummy_wav):
        response = client.get("/api/podcast/bgm-preview/space.mp3")
        assert response.status_code == 200
        assert response.content == b"ID3dummybgmmp3"
        assert response.headers["content-type"] == "audio/mpeg"


def test_podcast_submit_job_with_description_and_hashtags():
    img = Image.new("RGB", (1920, 1080), color="darkgreen")
    img_buf = BytesIO()
    img.save(img_buf, format="PNG")
    img_bytes = img_buf.getvalue()

    with patch.object(app.state.job_service, "submit_podcast") as mock_submit:
        record = app.state.job_service.registry.create("podcast-test-job2")
        mock_submit.return_value = record

        response = client.post(
            "/api/podcast/jobs",
            data={
                "title": "Podcast with desc",
                "script": "Sample script",
                "voice": "Enceladus",
                "speed": "1.0",
                "style_prompt": "",
                "enable_subtitles": "true",
                "bgm_volume": "0.08",
                "description": "This is a test description",
                "hashtags": "#test #podcast",
            },
            files={"cover_image": ("cover.png", img_bytes, "image/png")},
        )
        assert response.status_code == 202
        # Verify that the service received the description and hashtags
        _, kwargs = mock_submit.call_args
        assert kwargs["description"] == "This is a test description"
        assert kwargs["hashtags"] == "#test #podcast"
        assert mock_submit.called


def test_video_metadata_endpoint_with_hashtags():
    record = app.state.job_service.registry.create("meta-test-job")
    record.metadata = {
        "videoMetadata": {
            "title": "Old Title",
            "description": "Old Desc",
            "hashtags": "#old"
        }
    }
    with patch.object(app.state.persistence, "update_job_metadata", return_value=True):
        get_res = client.get("/api/jobs/meta-test-job/video-metadata")
        assert get_res.status_code == 200
        assert get_res.json()["hashtags"] == "#old"

        put_res = client.put(
            "/api/jobs/meta-test-job/video-metadata",
            json={
                "title": "New Title",
                "description": "New Desc",
                "hashtags": "#new #tags"
            }
        )
        assert put_res.status_code == 200
        data = put_res.json()
        assert data["title"] == "New Title"
        assert data["description"] == "New Desc"
        assert data["hashtags"] == "#new #tags"
