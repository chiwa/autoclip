import shutil
import wave

import pytest

from app.infrastructure.ffmpeg import FfprobeRunner
from app.infrastructure.tts import LocalThaiTtsProvider


@pytest.mark.integration
def test_real_local_thai_tts_generates_speech(tmp_path):
    if not shutil.which("ffprobe"):
        pytest.skip("ffprobe unavailable")
    output = LocalThaiTtsProvider().synthesize(
        "คุณเชื่อไหม เรื่องนี้มีอยู่จริงบนโลกของเรา",
        "th-TH",
        "thai-male-01",
        1.0,
        tmp_path / "thai.wav",
    )
    with wave.open(str(output)) as audio:
        assert audio.getnframes() > 1000
        assert audio.getframerate() > 0
    assert FfprobeRunner().duration(output) > 0.5
