"""Unit tests for AutoClip Reusable Asset Catalog and Search system."""

import json
import os
import shutil
from pathlib import Path
import pytest
from PIL import Image

from scripts.build_asset_catalog import (
    AssetCatalogBuilder,
    compute_sha256,
    copy_file_apfs_clone,
    get_image_info,
    is_production_asset,
    classify_role_and_reuse,
)
from scripts.search_assets import search_assets, tokenize_query, score_record


@pytest.fixture
def temp_repo(tmp_path: Path):
    """Create a simulated AutoClip repository structure in a temporary folder."""
    repo = tmp_path / "repo"
    repo.mkdir()
    assets = repo / "assets"
    assets.mkdir()

    # Create dummy images with distinct colors
    def create_dummy_img(path: Path, size=(1080, 1920), color=(255, 0, 0)):
        path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGB", size, color)
        img.save(path, "PNG")

    # Project 1: Titan reel
    proj1 = assets / "dragonfly_titan_reel"
    create_dummy_img(proj1 / "images" / "01.png", (1080, 1920), (200, 100, 50))
    create_dummy_img(proj1 / "images" / "02.png", (1080, 1920), (100, 50, 200))
    create_dummy_img(proj1 / "images" / "03.png", (1080, 1920), (50, 200, 100))

    # script.json for Project 1
    script1 = {
        "project": {"id": "dragonfly_titan_reel", "title": "สำรวจไททัน ดวงจันทร์ดาวเสาร์"},
        "description": "เรื่องราวของโดรน Dragonfly สำรวจทะเลมีเทนบนดวงจันทร์ไททัน บรรยากาศสีส้ม",
        "hashtags": ["#Titan", "#Dragonfly", "#Space"],
        "scenes": [
            {
                "id": "01",
                "image": "images/01.png",
                "role": "hook",
                "narration": "ทำไมไททันถึงมีบรรยากาศสีส้มหนาทึบ?",
                "visual_prompt": "Colossal orange haze atmosphere of moon Titan with drone flying",
            },
            {
                "id": "02",
                "image": "images/02.png",
                "role": "content",
                "narration": "โดรน Dragonfly กำลังบินร่อนเหนือทะเลมีเทน",
                "visual_prompt": "Dragonfly octocopter drone hovering over liquid methane lakes",
            },
            {
                "id": "03",
                "image": "images/03.png",
                "role": "content",
                "narration": "ใต้ผิวน้ำแข็งอาจมีสิ่งมีชีวิต",
                "visual_prompt": "Subsurface ocean beneath icy crust of Titan",
            },
        ],
    }
    with open(proj1 / "script.json", "w", encoding="utf-8") as f:
        json.dump(script1, f, ensure_ascii=False)

    # Project 2: Duplicate image test (re-using 02.png from Project 1)
    proj2 = assets / "titan_methane_short"
    proj2_img = proj2 / "images" / "methane_lake.png"
    proj2_img.parent.mkdir(parents=True, exist_ok=True)
    # Copy exact content so SHA-256 matches
    shutil.copy2(proj1 / "images" / "02.png", proj2_img)

    # Project 3: Black hole reel
    proj3 = assets / "black_hole_reel"
    create_dummy_img(proj3 / "images" / "01.png", (1080, 1920), (10, 10, 10))
    create_dummy_img(proj3 / "images" / "02.png", (1080, 1920), (20, 20, 20))
    script3 = {
        "project": {"id": "black_hole_reel", "title": "ความลับของหลุมดำยักษ์"},
        "description": "หลุมดำมวลยิ่งยวดและการสังเกตการณ์ accretion disk จานพอกพูนมวล",
        "scenes": [
            {
                "id": "01",
                "image": "images/01.png",
                "role": "hook",
                "narration": "ถ้าหลุมดำกลืนทุกอย่าง…แสงรอบๆ มันมาจากไหน?",
                "visual_prompt": "Supermassive black hole with glowing relativistic accretion disk",
            },
            {
                "id": "02",
                "image": "images/02.png",
                "role": "content",
                "narration": "จานพอกพูนมวลหมุนวนด้วยความเร็วเกือบเท่าแสง",
                "visual_prompt": "Glowing accretion disk spinning at near speed of light",
            },
        ],
    }
    with open(proj3 / "script.json", "w", encoding="utf-8") as f:
        json.dump(script3, f, ensure_ascii=False)

    # Scratch files in root assets/ that must be skipped
    create_dummy_img(assets / "test_thai_render.png", (500, 500))
    create_dummy_img(assets / "crop_orion.png", (300, 300))
    create_dummy_img(assets / "check_bottom.png", (400, 200))

    # Branding asset
    branding_dir = assets / "branding" / "mamase"
    create_dummy_img(branding_dir / "logo.png", (800, 200), (255, 255, 255))
    create_dummy_img(branding_dir / "mamase-reels-end-scence.png", (1080, 1920), (0, 0, 0))

    return repo


def test_image_metadata_extraction(tmp_path: Path):
    """Test dimension, format, and aspect ratio calculation."""
    img_path = tmp_path / "vertical.png"
    img = Image.new("RGB", (1080, 1920), (0, 128, 255))
    img.save(img_path, "PNG")

    w, h, fmt, aspect = get_image_info(img_path)
    assert w == 1080
    assert h == 1920
    assert fmt == "PNG"
    assert aspect == "9:16"

    # Test horizontal 16:9
    img_h = tmp_path / "horizontal.jpg"
    Image.new("RGB", (1920, 1080), (255, 128, 0)).save(img_h, "JPEG")
    w2, h2, fmt2, aspect2 = get_image_info(img_h)
    assert w2 == 1920
    assert h2 == 1080
    assert fmt2 == "JPEG"
    assert aspect2 == "16:9"


def test_skip_catalog_and_non_production(temp_repo: Path):
    """Test filtering of non-production scratch files and library directories."""
    builder = AssetCatalogBuilder(temp_repo)
    scanned = builder.scan_asset_files()
    rel_paths = [str(p.relative_to(temp_repo)) for p in scanned]

    # Must NOT include scratch files in root assets/
    assert not any("test_thai_render" in p for p in rel_paths)
    assert not any("crop_orion" in p for p in rel_paths)
    assert not any("check_bottom" in p for p in rel_paths)

    # Must NOT include anything inside reusable-library or catalog
    assert not any("reusable-library" in p for p in rel_paths)
    assert not any("catalog" in p for p in rel_paths)

    # Must include production images
    assert any("dragonfly_titan_reel" in p for p in rel_paths)
    assert any("black_hole_reel" in p for p in rel_paths)
    assert any("branding/mamase/logo.png" in p for p in rel_paths)


def test_deduplication_and_no_duplicates(temp_repo: Path):
    """Test that identical images share one library copy and multiple original_sources."""
    builder = AssetCatalogBuilder(temp_repo)
    res = builder.run(rebuild=True)

    # Read JSONL index
    records = []
    with open(builder.index_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    # Check for no duplicate asset_ids in index
    asset_ids = [r["asset_id"] for r in records]
    assert len(asset_ids) == len(set(asset_ids)), "Duplicate asset_ids found in assets-index.jsonl"

    # Find the record for the duplicated image (02.png in dragonfly_titan_reel and methane_lake.png in titan_methane_short)
    dedup_rec = None
    for r in records:
        if len(r["original_sources"]) > 1:
            dedup_rec = r
            break

    assert dedup_rec is not None, "Deduplication did not aggregate multiple sources"
    assert any("dragonfly_titan_reel" in s for s in dedup_rec["original_sources"])
    assert any("titan_methane_short" in s for s in dedup_rec["original_sources"])

    # Verify physical file exists in originals/
    orig_file = temp_repo / dedup_rec["library_path"]
    assert orig_file.is_file()
    assert orig_file.stat().st_size > 0


def test_scene_matching_with_script_json(temp_repo: Path):
    """Test scene extraction, visual prompts, and narrations from script.json."""
    builder = AssetCatalogBuilder(temp_repo)
    builder.run(rebuild=True)

    records = []
    with open(builder.index_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    # Look for scene 01 of dragonfly_titan_reel
    hook_rec = next(
        r for r in records if r["source_project"] == "dragonfly_titan_reel" and r["scene_number"] == "01"
    )
    assert hook_rec["role"] == "hook"
    assert hook_rec["reuse"] == "reuse_as_reference"  # Scene 01 must never be reuse_direct
    assert "ส้ม" in hook_rec["narration"]
    assert "drone" in hook_rec["visual_prompt"].lower()

    # Look for scene 02 of dragonfly_titan_reel
    content_rec = next(
        r for r in records if r["source_project"] == "dragonfly_titan_reel" and r["scene_number"] == "02"
    )
    assert content_rec["role"] == "content"
    assert content_rec["reuse"] == "reuse_direct"


def test_incremental_update(temp_repo: Path):
    """Test that incremental run skips unchanged files and processes new ones."""
    builder = AssetCatalogBuilder(temp_repo)
    res1 = builder.run(rebuild=True)
    assert res1["processed_count"] > 0
    assert res1["copied_count"] > 0

    # Second run without changes -> should skip all files
    res2 = builder.run(incremental=True, rebuild=False)
    assert res2["processed_count"] == 0
    assert res2["copied_count"] == 0
    assert res2["skipped_count"] == res1["total_scanned"]

    # Add a new file
    new_img = temp_repo / "assets" / "dragonfly_titan_reel" / "images" / "04.png"
    Image.new("RGB", (1080, 1920), (70, 70, 70)).save(new_img, "PNG")

    res3 = builder.run(incremental=True, rebuild=False)
    assert res3["processed_count"] == 1
    assert res3["copied_count"] == 1


def test_library_persistence_after_source_deletion(temp_repo: Path):
    """Test that library files and search continue to work after deleting the source project directory."""
    builder = AssetCatalogBuilder(temp_repo)
    builder.run(rebuild=True)

    # Pick an asset from black_hole_reel
    with open(builder.index_jsonl_path, "r", encoding="utf-8") as f:
        records = [json.loads(l) for l in f]

    bh_rec = next(r for r in records if r["source_project"] == "black_hole_reel" and r["scene_number"] == "01")
    lib_file = temp_repo / bh_rec["library_path"]
    thumb_file = temp_repo / bh_rec["thumbnail_path"]
    assert lib_file.is_file()
    assert thumb_file.is_file()

    # Now SIMULATE DELETION of the original clip directory
    shutil.rmtree(temp_repo / "assets" / "black_hole_reel")
    assert not (temp_repo / "assets" / "black_hole_reel").exists()

    # Verify that the physical file in reusable-library/originals is STILL intact!
    assert lib_file.is_file(), "Library file was lost after source directory deletion!"
    assert lib_file.stat().st_size > 0

    # Verify that search still finds the asset and points to the valid library_path
    results = search_assets(builder.index_jsonl_path, "black hole accretion disk", limit=5)
    assert len(results) > 0
    top_score, top_rec = results[0]
    assert top_rec["library_path"] == bh_rec["library_path"]
    assert (temp_repo / top_rec["library_path"]).is_file()


def test_search_assets_thai_and_english(temp_repo: Path):
    """Test bilingual search with Thai and English queries."""
    builder = AssetCatalogBuilder(temp_repo)
    builder.run(rebuild=True)

    # 1. Thai query
    thai_results = search_assets(builder.index_jsonl_path, "โดรนบน Titan บรรยากาศสีส้ม")
    assert len(thai_results) > 0
    top_score, top_rec = thai_results[0]
    assert "titan" in top_rec["source_project"].lower()

    # 2. English query
    en_results = search_assets(builder.index_jsonl_path, "black hole accretion disk")
    assert len(en_results) > 0
    top_score_en, top_rec_en = en_results[0]
    assert "black_hole" in top_rec_en["source_project"].lower()

    # 3. Filter by role
    hook_results = search_assets(builder.index_jsonl_path, "titan", role_filter="hook")
    assert all(r["role"] == "hook" for _, r in hook_results)

    # 4. Filter by reuse recommendation
    direct_results = search_assets(builder.index_jsonl_path, "titan", reuse_filter="reuse_direct")
    assert all(r["reuse"] == "reuse_direct" for _, r in direct_results)
