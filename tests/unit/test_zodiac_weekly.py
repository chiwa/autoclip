from __future__ import annotations

import csv
import json
import zipfile
from datetime import date
from pathlib import Path

import pytest
from PIL import Image

from app.domain.errors import AppError
from app.domain.zodiac_models import ZodiacBatchImport, ZodiacWeek
from app.services.zodiac_service import ZODIACS, ZodiacWeeklyService, thai_week_range


class StubJobs:
    def __init__(self):
        self.remuxes = 0

    def final_video(self, _job_id: str) -> Path:
        return Path("/not-ready")

    def update_video_metadata_tags(self, *_args) -> bool:
        self.remuxes += 1
        return True


class StubPersistence:
    pass


def service(tmp_path: Path) -> ZodiacWeeklyService:
    assets = tmp_path / "assets"
    templates = assets / "12ราศี"
    templates.mkdir(parents=True)
    fonts = assets / "fonts"
    fonts.mkdir()
    source_font = Path("assets/fonts/Kanit-Bold.ttf")
    (fonts / "Kanit-Bold.ttf").write_bytes(source_font.read_bytes())
    for zodiac in ZODIACS:
        Image.new("RGB", (941, 1672), (30 + zodiac.order, 20, 50)).save(templates / zodiac.template)
    return ZodiacWeeklyService(tmp_path / "workspace", assets, StubJobs(), StubPersistence())


def test_master_has_exactly_twelve_unique_signs(tmp_path: Path):
    item = service(tmp_path)
    item.validate_assets()
    assert len(ZODIACS) == 12
    assert len({z.id for z in ZODIACS}) == 12


def test_thai_week_range_handles_all_date_boundaries():
    # 1. same month
    assert thai_week_range(date(2026, 9, 14), date(2026, 9, 20)) == "14 - 20 ก.ย. 2569"
    # 2. cross month
    assert thai_week_range(date(2026, 9, 28), date(2026, 10, 4)) == "28 ก.ย. - 4 ต.ค. 2569"
    # 3. cross year
    assert thai_week_range(date(2026, 12, 28), date(2027, 1, 3)) == "28 ธ.ค. 2569 - 3 ม.ค. 2570"
    assert thai_week_range(date(2026, 12, 29), date(2027, 1, 4)) == "29 ธ.ค. 2569 - 4 ม.ค. 2570"


def test_zodiac_week_auto_derives_and_serializes_display_th():
    week = ZodiacWeek(start_date=date(2026, 9, 14), end_date=date(2026, 9, 20))
    assert week.display_th == "14 - 20 ก.ย. 2569"

    # Serializes across ZodiacBatchImport.model_dump
    batch_import = ZodiacBatchImport.model_validate({
        "week": {"start_date": "2026-09-14", "end_date": "2026-09-20"},
        "zodiacs": [],
    })
    dumped = batch_import.model_dump(by_alias=True, mode="json")
    assert dumped["week"]["display_th"] == "14 - 20 ก.ย. 2569"

    # Custom display_th is preserved
    custom_week = ZodiacWeek(start_date=date(2026, 9, 14), end_date=date(2026, 9, 20), display_th="กำหนดเอง")
    assert custom_week.display_th == "กำหนดเอง"


def test_import_accepts_empty_or_exactly_twelve_readings():
    body = ZodiacBatchImport.model_validate({"week": {"start_date": "2026-09-14", "end_date": "2026-09-20"}, "zodiacs": []})
    assert body.start_date == date(2026, 9, 14)
    assert body.week.display_th == "14 - 20 ก.ย. 2569"
    assert body.visual.motion.enabled is False
    assert body.voice.speed == 1.10
    assert body.visual.motion.preset == "none"
    with pytest.raises(ValueError):
        ZodiacBatchImport.model_validate({"week": {"start_date": "2026-09-14", "end_date": "2026-09-20"}, "zodiacs": [{"id": "aries"}]})


def test_imported_reading_does_not_invent_closing_after_advice():
    reading = {
        "id": "capricorn", "hook": "ราศีมังกร เริ่มทันที", "work": "เรื่องงาน",
        "finance": "เรื่องเงิน", "love": "เรื่องรัก", "advice": "คำแนะนำสุดท้าย",
    }
    sections = ZodiacWeeklyService._sections_from_reading(reading)
    assert sections[-1] == ("advice", "คำแนะนำสุดท้าย")
    assert [name for name, _ in sections] == ["hook", "work", "finance", "love", "advice"]


def test_overview_and_closing_are_included_only_when_explicit():
    reading = {
        "id": "capricorn", "hook": "Hook", "overview": "Overview", "work": "Work",
        "finance": "Finance", "love": "Love", "advice": "Advice", "closing": "Closing",
    }
    assert [name for name, _ in ZodiacWeeklyService._sections_from_reading(reading)] == [
        "hook", "overview", "work", "finance", "love", "advice", "closing",
    ]


def test_date_overlay_outputs_vertical_full_hd_and_rejects_blank(tmp_path: Path):
    item = service(tmp_path)
    source = item.templates_root / ZODIACS[0].template
    output = tmp_path / "dated.png"
    item._overlay_date(source, output, "14 - 20 ก.ย. 2569")
    with Image.open(output) as image:
        assert image.size == (1080, 1920)

    # Master template must remain strictly immutable
    assert source.is_file()
    with Image.open(source) as master_img:
        assert master_img.size == (941, 1672)

    # Reject blank / whitespace dates
    with pytest.raises(AppError) as err1:
        item._overlay_date(source, tmp_path / "blank1.png", "")
    assert err1.value.code == "ZODIAC_DATE_EMPTY"

    with pytest.raises(AppError) as err2:
        item._overlay_date(source, tmp_path / "blank2.png", "   ")
    assert err2.value.code == "ZODIAC_DATE_EMPTY"


def test_package_and_metadata_are_valid_and_match_content(tmp_path: Path):
    item = service(tmp_path)
    zodiac = ZODIACS[0]
    sections = item._content(zodiac, date(2026, 9, 14))
    metadata = item._metadata(zodiac, date(2026, 9, 14), date(2026, 9, 20), "14 - 20 ก.ย. 2569", sections)
    package = item._build_package(tmp_path / "batch", zodiac, date(2026, 9, 14), date(2026, 9, 20), "14 - 20 ก.ย. 2569", sections, metadata)
    with zipfile.ZipFile(package) as archive:
        script = json.loads(archive.read("script.json"))
        packaged_metadata = json.loads(archive.read("video-metadata.json"))
    assert len(script["scenes"]) == 6
    assert script["voice"]["voice"] == "Iapetus"
    assert script["voice"]["speed"] == 1.10
    assert "อ่านเฉพาะเนื้อหาภาษาไทยในช่อง text ให้ตรงตามต้นฉบับ" in script["voice"]["style_prompt"]
    assert "ห้ามอ่านแยกทีละคำ" in script["voice"]["style_prompt"]
    assert "หยุดทันทีหลังประโยคสุดท้าย" in script["voice"]["style_prompt"]
    assert "ไม่ช้าและไม่รีบ" in script["voice"]["style_prompt"]
    assert "ปานกลางค่อนข้างเร็ว" not in script["voice"]["style_prompt"]
    assert all(scene["motion"] == "none" for scene in script["scenes"])
    assert packaged_metadata["hook"] == sections[0][1]
    assert "ราศีมังกร" in packaged_metadata["title"]
    assert "การดูดวงเป็นความเชื่อส่วนบุคคล" in packaged_metadata["description"]
    assert "#ราศีมังกร" in packaged_metadata["hashtags"]


def test_visual_config_disables_motion_and_preserves_master(tmp_path: Path):
    item = service(tmp_path)
    zodiac = ZODIACS[0]
    source = item.templates_root / zodiac.template
    original = source.read_bytes()
    sections = item._content(zodiac, date(2026, 9, 14))
    metadata = item._metadata(zodiac, date(2026, 9, 14), date(2026, 9, 20), "14 - 20 ก.ย. 2569", sections)
    visual = {"date_overlay": {"enabled": True}, "motion": {"enabled": False, "preset": "none"}}
    package = item._build_package(tmp_path / "visual-batch", zodiac, date(2026, 9, 14), date(2026, 9, 20), "14 - 20 ก.ย. 2569", sections, metadata, visual)
    with zipfile.ZipFile(package) as archive:
        script = json.loads(archive.read("script.json"))
    assert all(scene["motion"] == "none" for scene in script["scenes"])
    assert source.read_bytes() == original


def test_visual_config_rejects_new_image_generation():
    with pytest.raises(ValueError):
        ZodiacBatchImport.model_validate({
            "week": {"start_date": "2026-09-14", "end_date": "2026-09-20"},
            "visual": {"generate_new_images": True},
        })


def test_voice_speed_is_read_from_json_and_written_to_script(tmp_path: Path):
    body = ZodiacBatchImport.model_validate({
        "week": {"start_date": "2026-09-14", "end_date": "2026-09-20"},
        "voice": {"speed": 1.15},
    })
    item = service(tmp_path)
    zodiac = ZODIACS[0]
    sections = item._content(zodiac, body.start_date)
    metadata = item._metadata(zodiac, body.start_date, body.end_date, "14 - 20 ก.ย. 2569", sections)
    package = item._build_package(tmp_path / "speed-batch", zodiac, body.start_date, body.end_date, "14 - 20 ก.ย. 2569", sections, metadata, body.visual.model_dump(), body.voice.model_dump())
    with zipfile.ZipFile(package) as archive:
        script = json.loads(archive.read("script.json"))
    assert script["voice"]["speed"] == 1.15


def test_csv_is_thai_safe_multiline_and_has_twelve_rows(tmp_path: Path):
    item = service(tmp_path)
    batch_id = "zodiac-weekly-test"
    batch_dir = item.root / batch_id
    batch_dir.mkdir(parents=True)
    children = []
    for zodiac in ZODIACS:
        sections = item._content(zodiac, date(2026, 9, 14))
        metadata = item._metadata(zodiac, date(2026, 9, 14), date(2026, 9, 20), "14 - 20 ก.ย. 2569", sections)
        path = batch_dir / f"{zodiac.order:02d}.metadata.json"
        item._write(path, metadata)
        children.append({"zodiac": zodiac.model_dump(), "metadataPath": str(path)})
    path = item._write_upload_csv({"batchId": batch_id, "children": children})
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 12
    assert rows[0]["zodiac_th"] == "ราศีมังกร"
    assert "\n" in rows[0]["description"]
    assert len({row["title"] for row in rows}) == 12


def test_missing_template_is_clear_error(tmp_path: Path):
    item = service(tmp_path)
    (item.templates_root / ZODIACS[0].template).unlink()
    with pytest.raises(AppError) as error:
        item.validate_assets()
    assert error.value.code == "ZODIAC_TEMPLATE_MISSING"


def test_zodiac_page_exposes_json_first_and_metadata_controls():
    html = Path("app/web/static/zodiac-weekly.html").read_text(encoding="utf-8")
    assert "Import weekly-zodiac-batch.json" in html
    assert "Generate 12 ราศี" in html
    assert "Regenerate Metadata" in html
    assert "Download Upload CSV" in html
    history = Path("app/web/static/zodiac-history.html").read_text(encoding="utf-8")
    assert "WEEKLY BATCH HISTORY" in history
    assert "Regenerate Failed" in history
    assert "Delete Batch" in history


def test_separate_history_routes_are_registered():
    from app.main import create_app

    paths = {route.path for route in create_app().routes}
    assert {"/reels-history", "/podcast-history", "/zodiac-history"} <= paths


def test_complete_archive_supports_partial_batch_and_report(tmp_path: Path):
    item = service(tmp_path)
    batch_id = "zodiac-weekly-partial"
    batch_dir = item.root / batch_id
    batch_dir.mkdir(parents=True)
    children = []
    for zodiac in ZODIACS[:2]:
        sections = item._content(zodiac, date(2026, 9, 14))
        metadata = item._metadata(zodiac, date(2026, 9, 14), date(2026, 9, 20), "14 - 20 ก.ย. 2569", sections)
        metadata_path = batch_dir / f"{zodiac.order:02d}.metadata.json"
        item._write(metadata_path, metadata)
        video = batch_dir / metadata["video_file"]
        video.write_bytes(b"video")
        children.append({"zodiac": zodiac.model_dump(), "jobId": zodiac.id, "metadataPath": str(metadata_path), "metadata": metadata, "videoAvailable": zodiac.order == 1})
    item.job_service.final_video = lambda job_id: batch_dir / f"01-capricorn.mp4"  # type: ignore[method-assign]
    batch = {"batchId": batch_id, "week": {"startDate": "2026-09-14", "endDate": "2026-09-20"}, "summary": {"completed": 1}, "children": children}
    item.get_batch = lambda _batch_id: batch  # type: ignore[method-assign]
    output = item.complete_archive(batch_id)
    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        report = json.loads(archive.read(next(name for name in names if name.endswith("batch-report.json"))))
    assert any(name.endswith("01-capricorn.mp4") for name in names)
    assert report == {"expected": 12, "completed": 1, "failed": 1, "failed_zodiacs": ["aquarius"]}


def test_delete_batch_never_deletes_master_assets(tmp_path: Path):
    item = service(tmp_path)
    deleted_projects = []
    item.persistence.delete_project = deleted_projects.append  # type: ignore[attr-defined]
    batch_id = "zodiac-weekly-delete"
    batch_dir = item.root / batch_id
    batch_dir.mkdir(parents=True)
    job_id = "safe-child-job"
    job_dir = item.root.parent / job_id
    job_dir.mkdir()
    master = item.templates_root / ZODIACS[0].template
    batch = {"batchId": batch_id, "summary": {"running": 0}, "children": [{"jobId": job_id, "projectId": "zodiac-capricorn"}]}
    item.get_batch = lambda _batch_id: batch  # type: ignore[method-assign]
    result = item.delete_batch(batch_id)
    assert result["deletedChildren"] == 1
    assert not batch_dir.exists() and not job_dir.exists()
    assert master.is_file()
    assert deleted_projects == ["zodiac-capricorn", batch_id]


def test_regenerate_metadata_does_not_submit_or_render(tmp_path: Path):
    item = service(tmp_path)
    zodiac = ZODIACS[0]
    batch_id = "zodiac-weekly-regenerate"
    batch_dir = item.root / batch_id
    batch_dir.mkdir(parents=True)
    sections = item._content(zodiac, date(2026, 9, 14))
    metadata = item._metadata(zodiac, date(2026, 9, 14), date(2026, 9, 20), "14 - 20 ก.ย. 2569", sections)
    metadata_path = batch_dir / "01-capricorn.metadata.json"
    item._write(metadata_path, metadata | {"title": "ราศีมังกร ชื่อที่ผู้ใช้แก้เอง"})
    package = item._build_package(batch_dir, zodiac, date(2026, 9, 14), date(2026, 9, 20), "14 - 20 ก.ย. 2569", sections, metadata)
    item._write(batch_dir / "batch.json", {
        "batchId": batch_id,
        "week": {"startDate": "2026-09-14", "endDate": "2026-09-20", "displayTh": "14 - 20 ก.ย. 2569"},
        "children": [{"zodiac": zodiac.model_dump(), "projectId": "zodiac-capricorn", "jobId": "job-1", "package": str(package), "metadataPath": str(metadata_path)}],
    })
    item.get_batch = lambda _batch_id: item._load(_batch_id)  # type: ignore[method-assign]
    regenerated = item.regenerate_metadata(batch_id)
    assert regenerated["children"][0]["jobId"] == "job-1"
    assert json.loads(metadata_path.read_text(encoding="utf-8"))["title"] == metadata["title"]
    assert item.job_service.remuxes == 0
