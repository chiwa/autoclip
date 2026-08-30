import wave

import pytest

from app.domain.errors import AppError
from app.infrastructure.tts import DummyTtsProvider, LocalThaiTtsProvider, create_tts_provider


def test_dummy_tts_creates_valid_wav(tmp_path):
    output = DummyTtsProvider().synthesize("ภาษาไทย", "th-TH", "test", 1.0, tmp_path / "test.wav")
    with wave.open(str(output)) as wav:
        assert wav.getframerate() == 48000
        assert wav.getnframes() > 0


def test_provider_selection():
    assert isinstance(create_tts_provider("dummy"), DummyTtsProvider)
    assert isinstance(create_tts_provider("local"), LocalThaiTtsProvider)
    with pytest.raises(AppError) as caught:
        create_tts_provider("unknown")
    assert caught.value.code == "TTS_GENERATION_FAILED"


def test_local_provider_validates_language_and_voice(tmp_path):
    provider = LocalThaiTtsProvider()
    with pytest.raises(AppError) as language_error:
        provider.synthesize("hello", "en-US", "thai-male-01", 1, tmp_path / "en.wav")
    assert language_error.value.code == "TTS_GENERATION_FAILED"
    with pytest.raises(AppError) as voice_error:
        provider.synthesize("ภาษาไทย", "th-TH", "missing", 1, tmp_path / "missing.wav")
    assert voice_error.value.details["voice"] == "missing"
