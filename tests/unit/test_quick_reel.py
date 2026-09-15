from io import BytesIO
from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.services.quick_reel_service import QuickReelService

client = TestClient(app)


def test_quick_reel_tts_uses_provider_contract_and_style_property(tmp_path: Path):
    class Provider:
        style_prompt = None
        def synthesize(self, text, language, voice, speed, output_path):
            self.args = (text, language, voice, speed, output_path)
            return output_path

    provider = Provider()
    output = tmp_path / "voice.wav"
    result = QuickReelService._synthesize_narration(provider, "บทพูด", output, "Iapetus", 1.10)
    assert result == output
    assert provider.args == ("บทพูด", "th-TH", "Iapetus", 1.10, output)
    assert "อ่านเฉพาะเนื้อหาภาษาไทยในช่อง text ให้ตรงตามต้นฉบับ" in provider.style_prompt
    assert "ห้ามอ่านคำสั่งนี้" in provider.style_prompt
    assert "ห้ามอ่านแยกทีละคำ" in provider.style_prompt


def test_quick_reel_tts_uses_user_saved_style(tmp_path: Path):
    class Provider:
        style_prompt = None
        def synthesize(self, text, language, voice, speed, output_path):
            return output_path

    provider = Provider()
    QuickReelService._synthesize_narration(
        provider, "บทพูด", tmp_path / "voice.wav", "Iapetus", 1.10, "สไตล์ที่บันทึกไว้"
    )
    assert provider.style_prompt == "สไตล์ที่บันทึกไว้"


def test_quick_reel_audio_processor_uses_single_path_contract(tmp_path: Path):
    class Processor:
        def process(self, audio_path):
            self.path = audio_path
            return 12.5

    processor = Processor()
    audio = tmp_path / "voice.wav"
    clean_audio, duration = QuickReelService._process_narration(processor, audio)
    assert processor.path == audio
    assert clean_audio == audio
    assert duration == 12.5


def test_quick_reel_page_route():
    response = client.get("/quick-reel")
    assert response.status_code == 200
    assert "AutoClip · Quick Reel" in response.text
    assert "quickReelForm" in response.text
    assert "หลายภาพ • เสียงเดียว • พร้อมโพสต์" in response.text
    assert 'multiple hidden' in response.text
    assert 'id="imageOrderList"' in response.text
    assert "formData.append('images'" in response.text
    assert 'id="quickReelTtsStyle"' in response.text
    assert 'id="btnPreviewQuickReelVoice"' in response.text
    assert 'id="btnSaveQuickReelVoice"' in response.text
    assert "autoclip.quickReel.voice.v1" in response.text
    assert "formData.append('style_prompt'" in response.text
    assert "normalizeImportedTts" in response.text
    assert ".join('\\n\\n')" in response.text
    assert '"tts": ["บทพูดช่วงแรก", "บทพูดช่วงถัดไป"]' in response.text
    assert "Iapetus" in response.text
    assert "1.10" in response.text
    assert "chkHookOverlay" in response.text
    assert "btnFitCover" in response.text
    assert "btnFitContain" in response.text


def test_quick_reel_history_page_route():
    response = client.get("/quick-reel-history")
    assert response.status_code == 200
    assert "history-tabs" in response.text
    assert "quick-reel" in response.text


def test_prepare_image_cover_mode(tmp_path: Path):
    service = QuickReelService(
        app.state.settings,
        app.state.ffmpeg,
        app.state.ffprobe,
        app.state.job_service,
    )
    # Create landscape test image (1200x800)
    input_img = tmp_path / "test_input.png"
    Image.new("RGB", (1200, 800), color=(100, 150, 200)).save(input_img)

    output_img = tmp_path / "test_cover.png"
    service.prepare_image(input_img, output_img, fit="cover")

    with Image.open(output_img) as im:
        assert im.size == (1080, 1920)


def test_prepare_image_contain_mode(tmp_path: Path):
    service = QuickReelService(
        app.state.settings,
        app.state.ffmpeg,
        app.state.ffprobe,
        app.state.job_service,
    )
    # Create landscape test image (1200x800)
    input_img = tmp_path / "test_input.png"
    Image.new("RGB", (1200, 800), color=(100, 150, 200)).save(input_img)

    output_img = tmp_path / "test_contain.png"
    service.prepare_image(input_img, output_img, fit="contain")

    with Image.open(output_img) as im:
        assert im.size == (1080, 1920)
        # Verify corner is dark background (18, 20, 26)
        pixel = im.getpixel((10, 10))
        assert pixel == (18, 20, 26)


def test_apply_hook_overlay(tmp_path: Path):
    service = QuickReelService(
        app.state.settings,
        app.state.ffmpeg,
        app.state.ffprobe,
        app.state.job_service,
    )
    base_img = tmp_path / "base.png"
    Image.new("RGB", (1080, 1920), color=(50, 50, 50)).save(base_img)

    out_img = tmp_path / "with_hook.png"
    service.apply_hook_overlay(base_img, "ความลับของหลุมดำ", position="top", output_path=out_img)

    assert out_img.is_file()
    with Image.open(out_img) as im:
        assert im.size == (1080, 1920)


def test_quick_reel_validation_empty_script():
    img = Image.new("RGB", (500, 500), color="red")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    response = client.post(
        "/api/quick-reel",
        data={"script": "   ", "voice": "Iapetus"},
        files={"image": ("test.jpg", img_bytes, "image/jpeg")},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "QUICK_REEL_SCRIPT_EMPTY"


def test_quick_reel_submit_success():
    img = Image.new("RGB", (1080, 1920), color="blue")
    buf = BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    with patch.object(app.state.quick_reel_service, "submit_quick_reel") as mock_submit:
        record = app.state.job_service.registry.create("test-quick-reel-job")
        mock_submit.return_value = record

        response = client.post(
            "/api/quick-reel",
            data={
                "script": "นี่คือคลิป Quick Reel แบบรวดเร็วที่สุด",
                "voice": "Iapetus",
                "speed": "1.10",
                "motion": "static",
                "fit": "cover",
                "hook_enabled": "true",
                "hook_text": "หยุดดูตรงนี้ก่อน!",
                "hook_position": "top",
                "subtitles_enabled": "true",
                "bgm_enabled": "false",
            },
            files={"image": ("photo.png", img_bytes, "image/png")},
        )
        assert response.status_code == 200
        assert response.json()["jobId"] == record.job_id
        assert mock_submit.called


def test_quick_reel_submit_preserves_multiple_image_order():
    first = BytesIO()
    second = BytesIO()
    Image.new("RGB", (1080, 1920), color="blue").save(first, format="PNG")
    Image.new("RGB", (1080, 1920), color="gold").save(second, format="PNG")

    with patch.object(app.state.quick_reel_service, "submit_quick_reel") as mock_submit:
        record = app.state.job_service.registry.create("test-quick-reel-multiple")
        mock_submit.return_value = record
        response = client.post(
            "/api/quick-reel",
            data={
                "script": "บทพูดภาพแรก\n\nบทพูดภาพสอง",
                "tts_segments": '["บทพูดภาพแรก", "บทพูดภาพสอง"]',
                "style_prompt": "สไตล์ Quick Reel ที่แก้ไขแล้ว",
            },
            files=[
                ("images", ("first.png", first.getvalue(), "image/png")),
                ("images", ("second.png", second.getvalue(), "image/png")),
            ],
        )

        assert response.status_code == 200
        uploads = mock_submit.call_args.kwargs["image_files"]
        assert [upload.filename for upload in uploads] == ["first.png", "second.png"]
        assert mock_submit.call_args.kwargs["image_file"] is None
        assert mock_submit.call_args.kwargs["tts_segments"] == ["บทพูดภาพแรก", "บทพูดภาพสอง"]
        assert mock_submit.call_args.kwargs["style_prompt"] == "สไตล์ Quick Reel ที่แก้ไขแล้ว"


def test_quick_reel_rejects_invalid_tts_segments_json():
    image = BytesIO()
    Image.new("RGB", (1080, 1920), color="blue").save(image, format="PNG")
    response = client.post(
        "/api/quick-reel",
        data={"script": "บทพูด", "tts_segments": "not-json"},
        files={"image": ("image.png", image.getvalue(), "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "QUICK_REEL_TTS_SEGMENTS_INVALID"


def test_multi_image_slideshow_keeps_narration_out_of_xfade(tmp_path: Path):
    ffmpeg = MagicMock()
    ffmpeg.has_filter.return_value = False
    service = QuickReelService(
        app.state.settings,
        ffmpeg,
        app.state.ffprobe,
        app.state.job_service,
    )
    images = []
    for index in range(2):
        path = tmp_path / f"image-{index}.png"
        Image.new("RGB", (1080, 1920), color=(index * 40, 20, 80)).save(path)
        images.append(path)
    narration = tmp_path / "narration.wav"
    narration.touch()

    service._render_multi_image_slideshow(
        images, narration, None, 10.0, "none", tmp_path / "scene.mp4"
    )

    assert ffmpeg.run.call_count == 2
    visual_args = ffmpeg.run.call_args_list[0].args[0]
    final_args = ffmpeg.run.call_args_list[1].args[0]
    visual_filter = visual_args[visual_args.index("-filter_complex") + 1]
    assert "xfade=transition=fade:duration=0.400" in visual_filter
    assert "acrossfade" not in visual_filter
    assert str(narration) not in visual_args
    assert final_args[final_args.index("-i", 2) + 1] == str(narration)


def test_multi_image_slideshow_uses_tts_duration_for_matching_image(tmp_path: Path):
    ffmpeg = MagicMock()
    ffmpeg.has_filter.return_value = False
    service = QuickReelService(app.state.settings, ffmpeg, app.state.ffprobe, app.state.job_service)
    images = []
    for index in range(2):
        path = tmp_path / f"image-{index}.png"
        Image.new("RGB", (1080, 1920), color=(20, index * 40, 80)).save(path)
        images.append(path)
    narration = tmp_path / "narration.wav"
    narration.touch()

    service._render_multi_image_slideshow(
        images, narration, None, 10.0, "none", tmp_path / "scene.mp4",
        image_durations=[3.0, 7.0],
    )

    visual_args = ffmpeg.run.call_args_list[0].args[0]
    visual_filter = visual_args[visual_args.index("-filter_complex") + 1]
    assert "trim=duration=3.400" in visual_filter
    assert "trim=duration=7.000" in visual_filter
    assert "offset=3.000" in visual_filter


def test_segment_subtitles_follow_tts_boundaries(tmp_path: Path):
    output = tmp_path / "segments.srt"
    QuickReelService._write_segment_subtitles(["หนึ่ง", "สอง"], [2.5, 3.0], output)
    content = output.read_text(encoding="utf-8")
    assert "00:00:00,000 --> 00:00:02,500" in content
    assert "00:00:02,500 --> 00:00:05,500" in content


def test_quick_reel_get_job():
    record = app.state.job_service.registry.create("test-qr-lookup")
    response = client.get(f"/api/quick-reel/{record.job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["jobId"] == record.job_id


def test_quick_reel_delete_job(tmp_path: Path):
    record = app.state.job_service.registry.create("test-qr-delete")
    record = app.state.job_service.registry.set(record.model_copy(update={"project_id": "qr-proj-del"}))
    response = client.delete(f"/api/quick-reel/{record.job_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "DELETED"
