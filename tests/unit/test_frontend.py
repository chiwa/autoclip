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


def test_ai_page_uses_no_chat_automatic_zip_flow_with_live_progress():
    page = (STATIC / "ai.html").read_text(encoding="utf-8")
    assert "สร้างบทอัตโนมัติ" in page
    assert "/api/ai/projects/automatic" in page
    assert "/generate-images" in page
    assert "/approve-and-package" in page
    assert "LIVE CREATION PROGRESS" in page
    assert "setInterval(refresh,1500)" in page
    assert "อัปเดตล่าสุด" in page
    assert "คุยกับ AutoClip" not in page
    assert 'id="download" class="button" download' in page


def test_antigravity_prompt_page_is_copyable_and_uses_durable_visual_brief():
    page = (STATIC / "antigravity.html").read_text(encoding="utf-8")
    app = Path("app/main.py").read_text(encoding="utf-8")
    assert 'id="copy"' in page
    assert "navigator.clipboard.writeText" in page
    assert "assets/parker_solar_probe_reel/visual-reference.md" in page
    assert "@application.get(\"/antigravity\"" in app
