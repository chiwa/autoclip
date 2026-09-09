from __future__ import annotations

from pathlib import Path
from PIL import Image

import pytest

from app.config.settings import Settings
from app.domain.errors import AppError
from app.infrastructure.ffmpeg import FfmpegRunner, FfprobeRunner
from app.infrastructure.tts.providers import DummyTtsProvider
from app.services.podcast_audio_mix import build_podcast_audio_mix_filter
from app.services.podcast_subtitle_service import PodcastSubtitleService
from app.services.podcast_video_renderer import PodcastVideoRenderer


def test_validate_and_prepare_image(tmp_path):
    settings = Settings()
    ffmpeg = FfmpegRunner()
    ffprobe = FfprobeRunner()
    renderer = PodcastVideoRenderer(ffmpeg, ffprobe, settings)

    # 1. Create a non-16:9 image
    src_img = tmp_path / "portrait.png"
    im = Image.new("RGB", (1000, 1000), color=(50, 100, 150))
    im.save(src_img)

    prepared_img = tmp_path / "prepared.png"
    w, h, is_16_9 = renderer.validate_and_prepare_image(src_img, prepared_img)

    assert (w, h) == (1000, 1000)
    assert not is_16_9
    assert prepared_img.is_file()

    with Image.open(prepared_img) as res:
        assert res.size == (1920, 1080)


def test_validate_image_invalid_extension(tmp_path):
    settings = Settings()
    renderer = PodcastVideoRenderer(FfmpegRunner(), FfprobeRunner(), settings)

    bad_file = tmp_path / "test.txt"
    bad_file.write_text("not an image")

    with pytest.raises(AppError) as exc_info:
        renderer.validate_and_prepare_image(bad_file, tmp_path / "out.png")
    assert exc_info.value.code == "PODCAST_IMAGE_INVALID"


def test_podcast_subtitle_generation(tmp_path):
    sub_service = PodcastSubtitleService()
    chunks = [
        "ยามค่ำคืนที่เงียบสงบ แสงดาวส่องประกายระยิบระยับ",
        "เรามาร่วมเดินทางสู่ห้วงลึกของจักรวาลไปด้วยกัน",
    ]
    durations = [3.5, 4.0]
    srt_out = tmp_path / "podcast.srt"

    sub_service.generate_srt(chunks, durations, srt_out)
    assert srt_out.is_file()
    content = srt_out.read_text(encoding="utf-8")
    assert "00:00:00,000 --> " in content
    assert "ยามค่ำคืนที่เงียบสงบ" in content


def test_podcast_video_render_smoke(tmp_path):
    settings = Settings()
    ffmpeg = FfmpegRunner()
    ffprobe = FfprobeRunner()
    renderer = PodcastVideoRenderer(ffmpeg, ffprobe, settings)

    # 1. Create cover image
    cover = tmp_path / "cover.png"
    im = Image.new("RGB", (1920, 1080), color=(20, 30, 50))
    im.save(cover)

    # 2. Create short dummy audio
    audio = tmp_path / "audio.wav"
    DummyTtsProvider().synthesize("สวัสดีครับ", "th-TH", "Enceladus", 1.0, audio)
    duration = ffprobe.duration(audio)

    # 3. Render video
    out_video = tmp_path / "final.mp4"
    renderer.render(
        job_id="smoke-job",
        workspace_root=tmp_path,
        cover_image=cover,
        narration_audio=audio,
        total_duration=duration,
        output_path=out_video,
    )

    assert out_video.is_file()
    probe = ffprobe.probe(out_video)
    v_stream = next(s for s in probe["streams"] if s.get("codec_type") == "video")
    a_stream = next(s for s in probe["streams"] if s.get("codec_type") == "audio")

    assert v_stream["width"] == 1920
    assert v_stream["height"] == 1080
    assert a_stream["codec_name"] == "aac"


def test_podcast_audio_mix_filter_is_shared_for_video_and_alternate_track():
    video_filter = build_podcast_audio_mix_filter(1, 2, 60.0, 0.08)
    alternate_filter = build_podcast_audio_mix_filter(0, 1, 60.0, 0.08)

    assert "[1:a]volume=1.0,asplit=2[n1][n2]" in video_filter
    assert "[0:a]volume=1.0,asplit=2[n1][n2]" in alternate_filter
    for expected in (
        "volume=0.08",
        "afade=t=in:st=0:d=1.0",
        "afade=t=out:st=58.00:d=2.0",
        "sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300",
        "loudnorm=I=-16:LRA=11:TP=-1.5",
    ):
        assert expected in video_filter
        assert expected in alternate_filter
