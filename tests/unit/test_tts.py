import wave

import pytest

from app.domain.errors import AppError
from app.config.settings import Settings
from app.infrastructure.tts import DummyTtsProvider, GoogleGeminiTtsProvider, LocalThaiTtsProvider, RunpodF5ThaiTtsProvider, create_tts_provider


def test_dummy_tts_creates_valid_wav(tmp_path):
    output = DummyTtsProvider().synthesize("ภาษาไทย", "th-TH", "test", 1.0, tmp_path / "test.wav")
    with wave.open(str(output)) as wav:
        assert wav.getframerate() == 48000
        assert wav.getnframes() > 0


def test_provider_selection():
    assert isinstance(create_tts_provider("dummy"), DummyTtsProvider)
    assert isinstance(create_tts_provider("local"), LocalThaiTtsProvider)
    assert isinstance(create_tts_provider("google-gemini", Settings()), GoogleGeminiTtsProvider)
    with pytest.raises(AppError) as caught:
        create_tts_provider("unknown")
    assert caught.value.code == "TTS_GENERATION_FAILED"


def test_google_gemini_chunker_never_exceeds_utf8_byte_limit_for_unpunctuated_thai():
    text = "ข้อความภาษาไทยที่ไม่มีช่องว่างและไม่มีเครื่องหมายจบประโยค" * 220

    chunks = GoogleGeminiTtsProvider._chunk_text(text, max_bytes=2800)

    assert len(chunks) > 1
    assert all(chunk for chunk in chunks)
    assert all(len(chunk.encode("utf-8")) <= 2800 for chunk in chunks)
    assert "".join(chunks) == text


def test_google_gemini_chunker_preserves_short_text_as_one_chunk():
    assert GoogleGeminiTtsProvider._chunk_text("บทพูดสั้น") == ["บทพูดสั้น"]


def test_runpod_f5_provider_requires_configured_connector(tmp_path):
    settings = Settings()
    provider = create_tts_provider("runpod-f5", settings)
    assert isinstance(provider, RunpodF5ThaiTtsProvider)
    with pytest.raises(AppError) as caught:
        provider.synthesize("สวัสดีครับ", "th-TH", "thai-male-01", 1.0, tmp_path / "speech.wav")
    assert caught.value.code == "RUNPOD_F5_NOT_CONFIGURED"


def test_local_provider_validates_language_and_voice(tmp_path):
    provider = LocalThaiTtsProvider()
    with pytest.raises(AppError) as language_error:
        provider.synthesize("hello", "en-US", "thai-male-01", 1, tmp_path / "en.wav")
    assert language_error.value.code == "TTS_GENERATION_FAILED"
    with pytest.raises(AppError) as voice_error:
        provider.synthesize("ภาษาไทย", "th-TH", "missing", 1, tmp_path / "missing.wav")
    assert voice_error.value.details["voice"] == "missing"


def test_local_provider_accepts_legacy_kokoro_voice_alias():
    assert LocalThaiTtsProvider.VOICES["m_young_clear"] == "th_m_1"
