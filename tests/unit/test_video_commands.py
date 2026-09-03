from pathlib import Path

from app.config.settings import Settings
from app.domain.models import Scene
from app.infrastructure.ffmpeg import FfmpegRunner
from app.services.video_service import SceneRenderer, SubtitleRenderer, VideoComposer, srt_timestamp


def test_scene_filter_has_uniform_output_and_thai_subtitles():
    # Note: Create a real temp srt so is_file() evaluates true
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".srt") as tmp:
        scene = Scene(id="s", image="images/a.png", narration="ภาษาไทย", motion="slow_zoom_in")
        runner = FfmpegRunner()
        runner._filters = {"subtitles"}
        value = SceneRenderer(runner, Settings()).build_filter(scene, 2, Path(tmp.name))
        assert "1080:1920" in value
        assert "subtitles=" in value
        assert "FontSize=8.70" in value
        assert "format=yuv420p" in value


def test_scene_filter_skips_subtitles_when_disabled():
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".srt") as tmp:
        scene_disabled = Scene(id="s", image="images/a.png", narration="ภาษาไทย", show_subtitle=False, motion="slow_zoom_in")
        value = SceneRenderer(FfmpegRunner(), Settings()).build_filter(scene_disabled, 2, Path(tmp.name))
        assert "1080:1920" in value
        assert "subtitles=" not in value

        scene_none_sub = Scene(id="s2", image="images/a.png", narration="ภาษาไทย", motion="slow_zoom_in")
        value_no_path = SceneRenderer(FfmpegRunner(), Settings()).build_filter(scene_none_sub, 2, None)
        assert "subtitles=" not in value_no_path


def test_srt_timestamp():
    assert srt_timestamp(4.8) == "00:00:04,800"


def test_subtitle_window_can_leave_transition_free():
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        path = SubtitleRenderer().write("ทดสอบ", 5.0, Path(directory) / "scene.srt", start_seconds=0.45, end_seconds=4.55)
        assert "00:00:00,450 --> 00:00:04,550" in path.read_text(encoding="utf-8")


def test_transition_filter_crossfades_video_and_audio_at_real_offsets():
    filters, video_label, audio_label = VideoComposer(FfmpegRunner(), Settings()).build_transition_filter([3.0, 4.0, 2.0], ["fade", "wipe_left"], 0.2)
    assert "xfade=transition=fade:duration=0.200:offset=2.800" in filters
    assert "xfade=transition=wipeleft:duration=0.200:offset=6.600" in filters
    assert filters.count("acrossfade=d=0.200") == 2
    assert video_label == "vx2"
    assert audio_label == "ax2"


def test_transition_filter_supports_hard_cut():
    filters, _, _ = VideoComposer(FfmpegRunner(), Settings()).build_transition_filter([3.0, 4.0], ["none"], 0.2)
    assert "concat=n=2:v=1:a=0" in filters
    assert "xfade=" not in filters


def test_transition_names_from_script_map_to_ffmpeg():
    composer = VideoComposer(FfmpegRunner(), Settings())
    filters, _, _ = composer.build_transition_filter([2.0, 2.0], ["fade_black"], 0.2)
    assert "xfade=transition=fadeblack" in filters
