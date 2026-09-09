import pytest
from pathlib import Path
from unittest.mock import MagicMock

from app.infrastructure.ffmpeg.runner import build_ffmpeg_metadata_args


def test_build_ffmpeg_metadata_args_basic():
    args = build_ffmpeg_metadata_args(
        title="My Cool Title",
        description="Line 1\nLine 2\n#hashtag",
        artist="Mamase",
    )
    assert "-metadata" in args
    assert "title=My Cool Title" in args
    assert "description=Line 1\nLine 2\n#hashtag" in args
    assert "comment=Line 1\nLine 2\n#hashtag" in args
    assert "artist=Mamase" in args


def test_build_ffmpeg_metadata_args_truncation():
    giant_title = "A" * 500
    giant_desc = "B" * 10000
    giant_artist = "C" * 200

    args = build_ffmpeg_metadata_args(
        title=giant_title,
        description=giant_desc,
        artist=giant_artist,
    )
    # Find metadata values
    meta_dict = {}
    for i in range(0, len(args), 2):
        if args[i] == "-metadata" and i + 1 < len(args):
            key, val = args[i + 1].split("=", 1)
            meta_dict[key] = val

    assert len(meta_dict["title"]) == 250
    assert len(meta_dict["description"]) == 4000
    assert len(meta_dict["comment"]) == 4000
    assert len(meta_dict["artist"]) == 100


def test_build_ffmpeg_metadata_args_null_bytes_and_control_chars():
    dirty_title = "Title\x00with\x07weird\x08chars"
    dirty_desc = "Desc\x00with\x1fcontrols\nand\tkeeps\nnewlines"

    args = build_ffmpeg_metadata_args(
        title=dirty_title,
        description=dirty_desc,
    )
    meta_dict = {}
    for i in range(0, len(args), 2):
        if args[i] == "-metadata" and i + 1 < len(args):
            key, val = args[i + 1].split("=", 1)
            meta_dict[key] = val

    assert "\x00" not in meta_dict["title"]
    assert "\x07" not in meta_dict["title"]
    assert "\x00" not in meta_dict["description"]
    assert "\x1f" not in meta_dict["description"]
    # Preserves legitimate newlines
    assert "\n" in meta_dict["description"]


def test_build_ffmpeg_metadata_args_empty_and_none():
    assert build_ffmpeg_metadata_args(None, None, None) == []
    assert build_ffmpeg_metadata_args("", "", "") == []
    assert build_ffmpeg_metadata_args("   ", "   ", "   ") == []


def test_build_ffmpeg_metadata_args_never_crashes():
    class BadObj:
        def __str__(self):
            raise RuntimeError("Boom!")

    res = build_ffmpeg_metadata_args(title=BadObj(), description=BadObj())
    assert res == []


def test_ffmpeg_runner_handles_broken_utf8(monkeypatch):
    from app.infrastructure.ffmpeg.runner import FfmpegRunner
    import subprocess

    # Mock subprocess.run to return broken UTF-8 bytes if text=False,
    # or ensure subprocess.run doesn't crash when called with encoding="utf-8", errors="replace"
    runner = FfmpegRunner()
    # Execute a small python command through runner by patching executable to python
    monkeypatch.setattr(runner, "executable", "python3")
    # Output broken utf-8 bytes directly to stderr and exit 0
    # e.g. sys.stderr.buffer.write(b'broken \xff\xfe byte')
    script = "import sys; sys.stderr.buffer.write(b'broken \\xff\\xfe byte'); sys.exit(0)"
    # Must not raise UnicodeDecodeError!
    runner.run(["-c", script], error_code="TEST_FAILED")
