from pathlib import Path


STATIC = Path("app/web/static")


def test_progress_ui_uses_event_source_and_handles_terminal_states():
    script = (STATIC / "app.js").read_text(encoding="utf-8")
    assert "new EventSource" in script
    assert "addEventListener('progress'" in script
    assert "addEventListener('log'" in script
    assert "addEventListener('completed'" in script
    assert "location.replace" in script
    assert "addEventListener('failed'" in script
    assert "showFailure" in script


def test_preview_contains_video_download_and_generate_another():
    page = (STATIC / "preview.html").read_text(encoding="utf-8")
    assert '<video id="video"' in page
    assert "Download MP4" in page
    assert "Generate Another Video" in page


def test_home_contains_thai_tts_preview_and_download():
    page = (STATIC / "index.html").read_text(encoding="utf-8")
    script = (STATIC / "app.js").read_text(encoding="utf-8")
    assert "Text to Speech ภาษาไทย" in page
    assert 'id="ttsText"' in page
    assert '<audio id="ttsAudio" controls>' in page
    assert 'id="ttsDownload"' in page
    assert "fetch('/api/tts'" in script
    assert "URL.createObjectURL" in script
