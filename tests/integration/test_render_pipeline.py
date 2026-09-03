import json
import hashlib
import shutil
import subprocess
import zipfile

import pytest

from app.config.settings import Settings
from app.infrastructure.ffmpeg import FfmpegRunner, FfprobeRunner
from app.infrastructure.tts import DummyTtsProvider
from app.domain.models import Scene
from app.services.package_service import PackageService
from app.services.video_service import SceneRenderer, SubtitleRenderer, VideoComposer


@pytest.mark.integration
def test_thai_render_pipeline(tmp_path):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg tools unavailable")
    sample = tmp_path / "sample.zip"
    source = tmp_path / "source"
    source.mkdir()
    # Create an image using FFmpeg so the test exercises only container-provided dependencies.
    image = source / "scene.png"
    FfmpegRunner().run(["-f", "lavfi", "-i", "color=c=#6b1d37:s=720x1280", "-frames:v", "1", str(image)], "SCENE_RENDER_FAILED")
    payload = {"project": {"id": "thai-test", "title": "Thai test", "language": "th-TH"}, "voice": {"provider": "dummy", "voice": "test", "speed": 1}, "scenes": [{"id": "scene-01", "image": "images/scene.png", "narration": "คุณเชื่อไหม เรื่องนี้มีอยู่จริงบนโลกของเรา", "motion": "none"}]}
    with zipfile.ZipFile(sample, "w") as archive:
        archive.writestr("script.json", json.dumps(payload, ensure_ascii=False))
        archive.write(image, "images/scene.png")
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    script, _ = PackageService(10_000_000).extract_and_validate(sample, extracted)
    settings = Settings()
    audio = DummyTtsProvider().synthesize(script.scenes[0].narration, "th-TH", "test", 1, tmp_path / "scene.wav")
    duration = FfprobeRunner().duration(audio) + settings.video.scene_padding_seconds
    subtitle = SubtitleRenderer().write(script.scenes[0].subtitle, duration, tmp_path / "scene.srt")
    rendered = SceneRenderer(FfmpegRunner(), settings).render(script.scenes[0], extracted / script.scenes[0].image, audio, subtitle, duration, tmp_path / "scene.mp4")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    final = VideoComposer(FfmpegRunner(), settings).compose([rendered], output_dir, None)
    probe = FfprobeRunner().probe(final)
    video = next(stream for stream in probe["streams"] if stream["codec_type"] == "video")
    audio_stream = next(stream for stream in probe["streams"] if stream["codec_type"] == "audio")
    assert (video["width"], video["height"], video["codec_name"]) == (1080, 1920, "h264")
    assert audio_stream["codec_name"] == "aac"
    assert float(probe["format"]["duration"]) > 0


@pytest.mark.integration
def test_motion_is_visibly_different_across_scene(tmp_path):
    """Render real 5s clips and compare beginning/middle/end frames."""
    if not shutil.which("ffmpeg"):
        pytest.skip("FFmpeg unavailable")
    image = tmp_path / "detailed.png"
    FfmpegRunner().run(["-f", "lavfi", "-i", "testsrc2=size=720x1280:rate=30", "-frames:v", "1", str(image)], "SCENE_RENDER_FAILED")
    audio = DummyTtsProvider().synthesize("ภาพทดสอบ motion", "th-TH", "test", 1, tmp_path / "audio.wav")
    renderer = SceneRenderer(FfmpegRunner(), Settings())
    for index, motion in enumerate(("slow_zoom_in", "cinematic_push_in", "pan_left_to_right", "drift_top_left", "auto")):
        scene = Scene(
            id=f"motion-{index}", image="images/detailed.png", narration="ภาพทดสอบ", motion=motion,
            motion_intensity=0.18,
        )
        clip = tmp_path / f"{motion}.mp4"
        renderer.render(scene, image, audio, None, 5.0, clip)
        frames = []
        for timestamp in (0, 2.5, 4.8):
            frame = tmp_path / f"{motion}-{timestamp}.png"
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(timestamp), "-i", str(clip), "-frames:v", "1", str(frame)], check=True)
            frames.append(hashlib.md5(frame.read_bytes()).hexdigest())
        assert len(set(frames)) >= 2, f"{motion} rendered no visible frame change"
