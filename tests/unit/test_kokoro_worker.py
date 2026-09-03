from app.infrastructure.tts.kokoro_worker import split_text


def test_kokoro_worker_splits_long_thai_text_into_safe_chunks():
    chunks = split_text("ก" * 320)
    assert len(chunks) >= 3
    assert all(len(chunk) <= 140 for chunk in chunks)


def test_kokoro_worker_keeps_short_text_intact():
    text = "สวัสดีครับ"
    assert split_text(text) == [text]
