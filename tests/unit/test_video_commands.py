from pathlib import Path

from app.config.settings import Settings
from app.domain.models import Scene
from app.infrastructure.ffmpeg import FfmpegRunner
from app.services.video_service import RenderProfile, SceneRenderer, SubtitleRenderer, VideoComposer, srt_timestamp


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


def test_scene_filter_uses_job_level_youtube_profile():
    scene = Scene(id="landscape", image="images/a.png", narration="สารคดี", motion="cinematic_push_in")
    profile = RenderProfile.from_project(Settings(), "1920x1080", 30)

    value = SceneRenderer(FfmpegRunner(), Settings(), profile).build_filter(scene, 2)

    assert "1920:1080" in value
    assert "s=1920x1080" in value


def test_srt_timestamp():
    assert srt_timestamp(4.8) == "00:00:04,800"


def test_subtitle_window_can_leave_transition_free():
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        path = SubtitleRenderer().write("ทดสอบ", 5.0, Path(directory) / "scene.srt", start_seconds=0.45, end_seconds=4.55)
        assert "00:00:00,450 --> 00:00:04,550" in path.read_text(encoding="utf-8")


def test_subtitle_without_keywords_keeps_full_caption_unchanged(tmp_path):
    text = "จักรวาลยังมีกฎฟิสิกส์เหมือนเดิม"
    path = SubtitleRenderer().write(text, 5.0, tmp_path / "plain.srt")
    assert text in path.read_text(encoding="utf-8")
    assert "<font" not in path.read_text(encoding="utf-8")


def test_subtitle_keywords_emphasize_without_removing_full_caption(tmp_path):
    text = "จักรวาลอาจมีกฎฟิสิกส์และ Multiverse"
    path = SubtitleRenderer().write(text, 5.0, tmp_path / "keywords.srt", keywords=["กฎฟิสิกส์", "Multiverse"])
    rendered = path.read_text(encoding="utf-8")
    assert '<font color="#55D7FF"><b>กฎฟิสิกส์</b></font>' in rendered
    assert '<font color="#55D7FF"><b>Multiverse</b></font>' in rendered
    assert "จักรวาลอาจมี" in rendered


def test_auto_motion_uses_focus_instead_of_scene_id():
    renderer = SceneRenderer(FfmpegRunner(), Settings())
    left = Scene(id="anything", image="images/a.png", narration="ทดสอบ", motion="auto", focus="left")
    right = Scene(id="same-content", image="images/a.png", narration="ทดสอบ", motion="auto", focus="right")
    left_filter = renderer.build_filter(left, 4.0)
    right_filter = renderer.build_filter(right, 4.0)
    assert "*on/" in left_filter
    assert "*(1-on/" in right_filter


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


def test_long_transition_timeline_is_composed_in_bounded_groups(tmp_path):
    class RecordingRunner:
        def __init__(self):
            self.commands: list[list[str]] = []

        def run(self, args, error_code, timeout_seconds=None):
            self.commands.append(args)

    runner = RecordingRunner()
    composer = VideoComposer(runner, Settings())
    scenes = [tmp_path / f"scene-{index:02}.mp4" for index in range(25)]
    durations = [3.0] * len(scenes)

    final = composer.compose(scenes, tmp_path, None, durations, ["fade"] * (len(scenes) - 1))

    # Three bounded first-pass groups (10, 10, 5), one three-input final
    # transition pass, and the final audio normalization pass.
    assert len(runner.commands) == 5
    transition_commands = [command for command in runner.commands if "-filter_complex" in command]
    assert len(transition_commands) == 4
    assert max(command.count("-i") for command in transition_commands) == 10
    assert final == tmp_path / "final.mp4"


def test_long_composition_timeout_scales_with_timeline_duration():
    assert VideoComposer._composition_timeout([10.0] * 79) == 1700


def test_outro_render_uses_silence_and_no_subtitle_or_narration_input(tmp_path):
    class RecordingRunner:
        def __init__(self):
            self.command = None

        def run(self, args, error_code, timeout_seconds=None):
            self.command = args

    runner = RecordingRunner()
    SceneRenderer(runner, Settings()).render_outro(tmp_path / "end.png", 2.0, tmp_path / "outro.mp4")
    command = runner.command
    assert "anullsrc=r=48000:cl=stereo" in command
    assert "2.000" in command
    assert not any("subtitles=" in item for item in command)
    assert not any(item.endswith(".wav") for item in command)


def test_bgm_fades_across_post_roll(tmp_path):
    class RecordingRunner:
        def __init__(self):
            self.commands = []

        def run(self, args, error_code, timeout_seconds=None):
            self.commands.append(args)

    runner = RecordingRunner()
    VideoComposer(runner, Settings()).compose(
        [tmp_path / "story.mp4", tmp_path / "outro.mp4"],
        tmp_path,
        tmp_path / "bgm.mp3",
        durations=[5.0, 2.0],
        transitions=["none"],
        bgm_fade_out_seconds=2.0,
    )
    final_filter = next(command[command.index("-filter_complex") + 1] for command in runner.commands if "-stream_loop" in command)
    assert "afade=t=out:st=5.000:d=2.000" in final_filter


def test_scene_filter_supports_gentle_float_and_hook_punch_in():
    runner = FfmpegRunner()
    renderer = SceneRenderer(runner, Settings())

    float_scene = Scene(id="flt", image="images/a.png", narration="ลอย", motion="gentle_float")
    float_filter = renderer.build_filter(float_scene, 10.0)
    assert "1.060" in float_filter
    assert "sin((on-1)/" in float_filter
    assert "zoompan=" in float_filter

    punch_scene = Scene(id="pnch", image="images/a.png", narration="ฮุก", motion="hook_punch_in")
    punch_filter = renderer.build_filter(punch_scene, 10.0)
    assert "lte(on,90)" in punch_filter
    assert "sin((on-90)" in punch_filter
    assert "zoompan=" in punch_filter
