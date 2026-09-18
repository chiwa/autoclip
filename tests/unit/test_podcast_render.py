from __future__ import annotations

from pathlib import Path
from PIL import Image

import pytest

from app.config.settings import Settings
from app.domain.errors import AppError
from app.infrastructure.ffmpeg import FfmpegRunner, FfprobeRunner
from app.infrastructure.tts.providers import DummyTtsProvider
from app.services.podcast_audio_mix import build_podcast_audio_mix_filter, build_podcast_ending_filter
from app.services.podcast_ending_song import resolve_podcast_ending_scene
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
    ending = tmp_path / "ending.wav"
    bgm = tmp_path / "bgm.wav"
    ending_image = tmp_path / "ending.png"
    Image.new("RGB", (1672, 941), color=(80, 20, 20)).save(ending_image)
    ffmpeg.run(
        ["-y", "-f", "lavfi", "-i", "sine=frequency=880:duration=0.4", "-c:a", "pcm_s16le", str(ending)],
        "TEST_AUDIO_FAILED",
    )
    ffmpeg.run(
        ["-y", "-f", "lavfi", "-i", "sine=frequency=180:duration=0.4", "-c:a", "pcm_s16le", str(bgm)],
        "TEST_AUDIO_FAILED",
    )
    ending_duration = ffprobe.duration(ending)
    subtitle = tmp_path / "subtitles.srt"
    subtitle.write_text("1\n00:00:00,000 --> 00:00:01,000\nทดสอบคำบรรยาย\n", encoding="utf-8")

    # 3. Render video
    out_video = tmp_path / "final.mp4"
    renderer.render(
        job_id="smoke-job",
        workspace_root=tmp_path,
        cover_image=cover,
        narration_audio=audio,
        total_duration=duration,
        output_path=out_video,
        ending_song_path=ending,
        ending_song_duration=ending_duration,
        ending_image_path=ending_image,
        bgm_path=bgm,
        subtitle_path=subtitle,
    )

    assert out_video.is_file()
    probe = ffprobe.probe(out_video)
    v_stream = next(s for s in probe["streams"] if s.get("codec_type") == "video")
    a_stream = next(s for s in probe["streams"] if s.get("codec_type") == "audio")

    assert v_stream["width"] == 1920
    assert v_stream["height"] == 1080
    assert a_stream["codec_name"] == "aac"
    assert abs(float(probe["format"]["duration"]) - (duration + ending_duration)) <= 0.15
    ffmpeg.validate_video_packets(out_video)


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


def test_ending_filter_concatenates_after_program_without_overlap_or_stretch():
    graph = build_podcast_ending_filter("main", 3, 20.0)
    assert "[program][theme]concat=n=2:v=0:a=1[a]" in graph
    assert "[3:a]" in graph
    assert "amix" not in graph
    assert "atempo" not in graph
    assert "aloop" not in graph


def test_resolve_ending_song_disabled_preserves_old_behavior(tmp_path):
    settings = Settings()
    settings.podcast.ending_scene.enabled = False
    settings.podcast.ending_scene.song = tmp_path / "missing.mp3"
    assert resolve_podcast_ending_scene(settings, FfprobeRunner()) == (None, None, 0.0)


def test_resolve_ending_song_missing_is_clear_error(tmp_path):
    settings = Settings()
    settings.podcast.ending_scene.image = tmp_path / "missing.png"
    with pytest.raises(AppError) as exc_info:
        resolve_podcast_ending_scene(settings, FfprobeRunner())
    assert exc_info.value.code == "PODCAST_ENDING_IMAGE_MISSING"


def test_resolve_ending_scene_missing_song_is_clear_error(tmp_path):
    settings = Settings()
    image = tmp_path / "end-of-scence.png"
    Image.new("RGB", (320, 180), color=(20, 30, 50)).save(image)
    settings.podcast.ending_scene.image = image
    settings.podcast.ending_scene.song = tmp_path / "missing.mp3"
    with pytest.raises(AppError) as exc_info:
        resolve_podcast_ending_scene(settings, FfprobeRunner())
    assert exc_info.value.code == "PODCAST_ENDING_SONG_MISSING"
