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
    script = (STATIC / "preview.js").read_text(encoding="utf-8")
    assert '<video id="video"' in page
    assert "Download MP4" in page
    assert "Generate Another Video" in page
    assert 'id="publicationToggle"' in page
    assert "PUBLISH STATUS" in page
    assert "`/api/jobs/${jobId}/publication`" in script
    assert "method: 'PATCH'" in script


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
    assert "ให้ Antigravity วางบท" in page
    assert "/api/ai/projects/automatic" in page
    assert "/generate-images" in page
    assert "/approve-and-package" in page
    assert "LIVE CREATION PROGRESS" in page
    assert "setInterval(refresh,1500)" in page
    assert "อัปเดตล่าสุด" in page
    assert "คุยกับ AutoClip" not in page
    assert "ANTIGRAVITY" in page
    assert "ให้ Antigravity วางบท" in page
    assert 'id="download" class="button" download' in page


def test_ai_script_review_uses_its_own_full_width_scene_layout():
    page = (STATIC / "ai.html").read_text(encoding="utf-8")
    css = (STATIC / "style.css").read_text(encoding="utf-8")
    assert 'class="tool-card script-review-card"' in page
    assert "className=images?'scene-card ai-scene-card':'ai-scene-card'" in page
    assert "ai-scene-header" in page
    assert ".ai-scene-card{display:block" in css
    assert ".ai-scene-meta{display:grid" in css


def test_antigravity_prompt_page_is_copyable_and_uses_durable_visual_brief():
    page = (STATIC / "antigravity.html").read_text(encoding="utf-8")
    app = Path("app/main.py").read_text(encoding="utf-8")
    assert 'id="copy"' in page
    assert "navigator.clipboard.writeText" in page
    assert "assets/parker_solar_probe_reel/visual-reference.md" in page
    assert "@application.get(\"/antigravity\"" in app


def test_history_has_publish_and_project_type_tabs_and_progress_action():
    page = (STATIC / "history.html").read_text(encoding="utf-8")
    assert 'data-filter="unpublished"' in page
    assert 'data-filter="published"' in page
    assert 'data-type="reel"' in page
    assert 'data-type="quick-reel"' in page
    assert 'data-type="podcast"' in page
    assert "/published" in page
    assert "ยังไม่เผยแพร่" in page
    assert "เผยแพร่แล้ว" in page
    assert "ดูความคืบหน้า" in page
    assert "RENDERING_SCENES" in page
    assert "ดูคลิปทั้งหมด (View All)" in page
    assert "autoclip.history.filters." in page
    assert "localStorage.setItem(historyFilterStorageKey" in page
    assert "readHistoryFilters" in page
    assert "syncHistoryFilterTabs" in page
    assert 'id="channelFilter"' in page
    assert "activeChannel" in page
    assert "channel:activeChannel" in page
    assert "data-channel-editor" in page
    assert "บันทึก Channel" in page
    assert "`/api/history/${encodeURIComponent(project.id)}/channel`" in page


def test_channel_management_and_creation_pickers_are_available():
    channels = (STATIC / "channels.html").read_text(encoding="utf-8")
    picker = (STATIC / "channels.js").read_text(encoding="utf-8")
    preview = (STATIC / "preview.html").read_text(encoding="utf-8")
    preview_js = (STATIC / "preview.js").read_text(encoding="utf-8")
    assert "จัดการ Channel" in channels
    assert "'/api/podcast/jobs'" in picker
    assert "'/api/quick-reel'" in picker
    assert "'/api/ai/projects/automatic'" in picker
    assert 'id="previewChannelPicker"' in preview
    assert "`/api/jobs/${jobId}/channel`" in preview_js
    nav = (STATIC / "nav.js").read_text(encoding="utf-8")
    assert "app-nav-primary" in nav
    assert "app-nav-history" in nav
    assert "nav.append(primary, histories)" in nav


def test_zodiac_history_has_view_all_videos_and_vertical_feed():
    page = (STATIC / "zodiac-history.html").read_text(encoding="utf-8")
    css = (STATIC / "style.css").read_text(encoding="utf-8")
    assert "ดูคลิปทั้งหมด (View All)" in page
    assert "toggleViewAll" in page
    assert "zodiac-video-feed" in page
    assert "zodiac-video-card" in page
    assert "zodiac-video-player" in page
    assert ".zodiac-video-feed{" in css
    assert ".zodiac-video-player{" in css
    assert ".zodiac-video-card{" in css
