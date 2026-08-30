#!/usr/bin/env python3
from __future__ import annotations

import json
import struct
import zlib
import zipfile
from pathlib import Path


def png(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    rows = b"".join(b"\0" + bytes(rgb) * width for _ in range(height))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sample = root / "sample-package" / "lake-natron"
    images = sample / "images"
    images.mkdir(parents=True, exist_ok=True)
    script = {
        "project": {"id": "lake-natron", "title": "Lake Natron", "language": "th-TH", "resolution": "1080x1920", "fps": 30},
        "voice": {"provider": "local", "voice": "thai-male-01", "speed": 1.0},
        "scenes": [
            {"id": "scene-01", "image": "images/scene-01.png", "narration": "คุณเชื่อไหม เรื่องนี้มีอยู่จริงบนโลกของเรา", "subtitle": "คุณเชื่อไหม เรื่องนี้มีอยู่จริงบนโลกของเรา", "motion": "slow_zoom_in", "transition": "dissolve"},
            {"id": "scene-02", "image": "images/scene-02.png", "narration": "ทะเลสาบแนตรอนมีสีแดงโดดเด่นและสวยงาม", "motion": "pan_left_to_right"},
        ],
    }
    (sample / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (images / "scene-01.png").write_bytes(png(720, 1280, (103, 31, 56)))
    (images / "scene-02.png").write_bytes(png(720, 1280, (22, 82, 91)))
    dist = root / "dist"
    dist.mkdir(exist_ok=True)
    output = dist / "lake-natron.zip"
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(sample.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(sample).as_posix())
    print(output)


if __name__ == "__main__":
    main()
