from __future__ import annotations

import pytest
from app.services.podcast_chunker import PodcastChunker


def test_empty_script():
    assert PodcastChunker.chunk("") == []
    assert PodcastChunker.chunk("   \n\n  ") == []


def test_short_script_single_chunk():
    text = "สวัสดีครับ ยินดีต้อนรับสู่พอดแคสต์ของเราในค่ำคืนนี้"
    chunks = PodcastChunker.chunk(text, max_bytes=2800)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_paragraph_splitting():
    p1 = "นี่คือย่อหน้าที่หนึ่ง เล่าเรื่องราวดวงดาวบนท้องฟ้า"
    p2 = "นี่คือย่อหน้าที่สอง เล่าเรื่องราวของหลุมดำใจกลางกาแล็กซี"
    full_text = f"{p1}\n\n{p2}"

    # If max_bytes is smaller than full text but larger than each paragraph
    max_b = max(len(p1.encode("utf-8")), len(p2.encode("utf-8"))) + 5
    chunks = PodcastChunker.chunk(full_text, max_bytes=max_b)
    assert len(chunks) == 2
    assert chunks[0] == p1
    assert chunks[1] == p2


def test_all_chunks_within_byte_limit():
    long_thai_paragraph = (
        "จักรวาลของเรามีความลี้ลับมากมายที่นักวิทยาศาสตร์ยังคงค้นหาคำตอบ "
        "ดาวเคราะห์น้อยและดาวหางโคจรรอบดวงอาทิตย์เป็นระยะเวลาหลายล้านปี "
        "การสำรวจอวกาศในยุคปัจจุบันทำให้เราเข้าใจกำเนิดของระบบสุริยะมากขึ้น "
        "เมื่อเรามองขึ้นไปบนท้องฟ้าในคืนที่มืดสนิท แสงจากดวงดาวนับพันล้านดวงกำลังเดินทางมาหาเรา "
    ) * 15  # Many repetitions

    max_bytes = 1500
    chunks = PodcastChunker.chunk(long_thai_paragraph, max_bytes=max_bytes)
    assert len(chunks) > 1
    for i, c in enumerate(chunks):
        b = len(c.encode("utf-8"))
        assert b <= max_bytes, f"Chunk {i} has {b} bytes, exceeding {max_bytes}"


def test_word_boundary_preservation():
    # Test with small max_bytes
    text = "ดาวพฤหัสบดีเป็นดาวเคราะห์ที่มีขนาดใหญ่ที่สุดในระบบสุริยะ"
    chunks = PodcastChunker.chunk(text, max_bytes=60)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c.encode("utf-8")) <= 60
    # Make sure text can be reassembled without missing content
    combined = "".join(chunks).replace(" ", "")
    assert "ดาวพฤหัสบดี" in combined


def test_utf8_byte_calculation():
    thai_char = "ก"
    assert len(thai_char.encode("utf-8")) == 3
    assert PodcastChunker.byte_len(thai_char) == 3
