from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".agents/skills/mamase-reels-cover/scripts/generate_mamase_reels_cover.py"
SPEC = importlib.util.spec_from_file_location("mamase_cover_compositor", SCRIPT)
assert SPEC and SPEC.loader
cover = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cover)


def _base(tmp_path: Path) -> Path:
    path = tmp_path / "raw.png"
    Image.new("RGB", (1080, 1920), "#071329").save(path)
    return path


def test_compositor_uses_only_one_brand_and_required_copy(tmp_path: Path) -> None:
    output = tmp_path / "scene-01-hook.png"
    report = cover.create_reels_cover(
        str(_base(tmp_path)),
        str(output),
        "ดาวพฤหัส",
        "ทำไมมันไม่กลายเป็นดาวฤกษ์?",
        protected_subjects={
            "hero": [(600, 600, 1050, 1100)],
            "celestial": [(700, 1100, 1000, 1400)],
            "characters": [(600, 1400, 780, 1800), (800, 1400, 1050, 1850)],
        },
    )

    assert Image.open(output).size == (1080, 1920)
    assert report["brand_asset_count"] == 1
    assert report["text_layers"] == ["topic_title", "thai_hook"]
    assert report["forbidden_layers"] == []


def test_text_block_never_intersects_protected_zone(tmp_path: Path) -> None:
    report = cover.create_reels_cover(
        str(_base(tmp_path)),
        str(tmp_path / "cover.png"),
        "ALPHA CENTAURI",
        "ดาวข้างบ้านของเราอยู่ไกลแค่ไหน?",
        protected_subjects={
            "hero": [(0, 170, 1080, 500)],
            "celestial": [(700, 1700, 900, 1800)],
            "characters": [(600, 1700, 780, 1900), (800, 1700, 1050, 1900)],
        },
    )

    text = tuple(report["text_rect"])
    assert text[1] >= 520
    assert not cover._intersects(text, (0, 170, 1080, 500))


def test_missing_protected_subject_category_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Missing protected subject categories"):
        cover.create_reels_cover(
            str(_base(tmp_path)),
            str(tmp_path / "cover.png"),
            "หัวข้อ",
            "คำถาม",
            protected_subjects={"characters": [(1, 1, 2, 2), (3, 3, 4, 4)]},
        )


def test_legacy_clutter_options_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Legacy cover clutter"):
        cover.create_reels_cover(
            str(_base(tmp_path)),
            str(tmp_path / "cover.png"),
            "หัวข้อ",
            "คำถาม",
            protected_subjects={
                "hero": [(700, 700, 1000, 1300)],
                "celestial": [(600, 200, 900, 500)],
                "characters": [(600, 1400, 780, 1800), (800, 1400, 1050, 1850)],
            },
            sub_en="UNWANTED ENGLISH FILLER",
        )


def test_unlabelled_zones_cannot_bypass_subject_gate(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unlabelled protected zones"):
        cover.create_reels_cover(
            str(_base(tmp_path)), str(tmp_path / "cover.png"), "หัวข้อ", "คำถาม",
            protected_zones=[(10, 10, 100, 100)],
        )
