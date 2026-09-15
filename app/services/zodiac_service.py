from __future__ import annotations

import json
import csv
import hashlib
import shutil
import threading
import uuid
import zipfile
from datetime import date, datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.domain.errors import AppError
from app.domain.models import Script
from app.domain.zodiac_models import THAI_MONTHS, ZodiacDefinition, thai_week_range
from app.services.package_service import PackageService


ZODIACS: tuple[ZodiacDefinition, ...] = (
    ZodiacDefinition(id="capricorn", order=1, name_th="มังกร", name_en="Capricorn", birth_range_th="22 ธันวาคม - 19 มกราคม", template="มังกร.png"),
    ZodiacDefinition(id="aquarius", order=2, name_th="กุมภ์", name_en="Aquarius", birth_range_th="20 มกราคม - 18 กุมภาพันธ์", template="กุมภ์.png"),
    ZodiacDefinition(id="pisces", order=3, name_th="มีน", name_en="Pisces", birth_range_th="19 กุมภาพันธ์ - 20 มีนาคม", template="มีน.png"),
    ZodiacDefinition(id="aries", order=4, name_th="เมษ", name_en="Aries", birth_range_th="21 มีนาคม - 19 เมษายน", template="เมษ.png"),
    ZodiacDefinition(id="taurus", order=5, name_th="พฤษภ", name_en="Taurus", birth_range_th="20 เมษายน - 20 พฤษภาคม", template="พฤษภ.png"),
    ZodiacDefinition(id="gemini", order=6, name_th="เมถุน", name_en="Gemini", birth_range_th="21 พฤษภาคม - 20 มิถุนายน", template="เมถุน.png"),
    ZodiacDefinition(id="cancer", order=7, name_th="กรกฎ", name_en="Cancer", birth_range_th="21 มิถุนายน - 22 กรกฎาคม", template="กรกฎ.png"),
    ZodiacDefinition(id="leo", order=8, name_th="สิงห์", name_en="Leo", birth_range_th="23 กรกฎาคม - 22 สิงหาคม", template="สิงห์.png"),
    ZodiacDefinition(id="virgo", order=9, name_th="กันย์", name_en="Virgo", birth_range_th="23 สิงหาคม - 22 กันยายน", template="กันย์.png"),
    ZodiacDefinition(id="libra", order=10, name_th="ตุลย์", name_en="Libra", birth_range_th="23 กันยายน - 22 ตุลาคม", template="ตุลย์.png"),
    ZodiacDefinition(id="scorpio", order=11, name_th="พิจิก", name_en="Scorpio", birth_range_th="23 ตุลาคม - 21 พฤศจิกายน", template="พิจิก.png"),
    ZodiacDefinition(id="sagittarius", order=12, name_th="ธนู", name_en="Sagittarius", birth_range_th="22 พฤศจิกายน - 21 ธันวาคม", template="ธนู.png"),
)

# Keep this deliberately short. Long English style prompts occasionally leak
# into Gemini's spoken audio. Thai instructions also make accidental leakage
# immediately detectable instead of sounding like part of the horoscope.
TTS_STYLE = (
    "อ่านเฉพาะเนื้อหาภาษาไทยในช่อง text ให้ตรงตามต้นฉบับ เริ่มที่ประโยคแรกและหยุดทันทีหลังประโยคสุดท้าย "
    "ห้ามอ่านคำสั่งนี้ ห้ามเติมคำนำ คำส่งท้าย หรือคำชวนติดตาม "
    "ใช้น้ำเสียงผู้ชายไทยอบอุ่น มั่นใจ และเป็นธรรมชาติ เหมือนผู้เล่าเรื่องที่คุยกับผู้ฟังโดยตรง "
    "พูดเป็นวลีและประโยคที่เชื่อมต่อกันอย่างลื่นไหล ใช้จังหวะสนทนาตามธรรมชาติ ไม่ช้าและไม่รีบ "
    "ห้ามอ่านแยกทีละคำ ห้ามเว้นช่องระหว่างคำ ห้ามลากเสียง และห้ามหยุดโดยไม่มีเครื่องหมายวรรคตอน "
    "เว้นสั้น ๆ เฉพาะเมื่อจบประโยคหรือเปลี่ยนหัวข้อ รักษาความชัดเจนและน้ำหนักเสียงให้สม่ำเสมอ"
)


class ZodiacWeeklyService:
    def __init__(self, root: Path, assets_root: Path, job_service, persistence):
        self.root = root / "zodiac-batches"
        self.root.mkdir(parents=True, exist_ok=True)
        self.assets_root = assets_root
        self.templates_root = assets_root / "12ราศี"
        self.font_path = assets_root / "fonts" / "Kanit-Bold.ttf"
        self.job_service = job_service
        self.persistence = persistence
        self._lock = threading.RLock()

    def master(self) -> dict:
        return {
            "brand": "คนเหนือดวง",
            "title": "ดวง 12 ราศีประจำสัปดาห์",
            "zodiacs": [item.model_dump() | {"previewUrl": f"/assets/12ราศี/{item.template}"} for item in ZODIACS],
        }

    def validate_assets(self) -> None:
        if len(ZODIACS) != 12 or len({item.id for item in ZODIACS}) != 12:
            raise AppError("ZODIAC_MASTER_INVALID", "ข้อมูลหลัก 12 ราศีไม่ครบหรือมีรหัสซ้ำ")
        missing = [item.template for item in ZODIACS if not (self.templates_root / item.template).is_file()]
        if missing:
            raise AppError("ZODIAC_TEMPLATE_MISSING", "ไม่พบภาพต้นแบบราศี", {"files": missing})
        if not self.font_path.is_file():
            raise AppError("ZODIAC_FONT_MISSING", "ไม่พบฟอนต์ภาษาไทยสำหรับวันที่")

    def create_batch(self, start: date, end: date, tts_provider: str = "google-gemini", readings: dict[str, dict] | None = None, visual: dict | None = None, voice: dict | None = None, channel_id: str = "undefined") -> dict:
        self.validate_assets()
        channel_id = self.persistence.valid_channel_id(channel_id)
        display = thai_week_range(start, end)
        batch_id = f"zodiac-weekly-{start.isoformat()}-{uuid.uuid4().hex[:8]}"
        batch_dir = self.root / batch_id
        batch_dir.mkdir(parents=True)
        children = []
        for item in ZODIACS:
            reading = (readings or {}).get(item.id)
            sections = self._sections_from_reading(reading) if reading else self._content(item, start)
            metadata = self._metadata(item, start, end, display, sections)
            metadata_path = batch_dir / f"{item.order:02d}-{item.id}.metadata.json"
            self._write(metadata_path, metadata)
            package = self._build_package(batch_dir, item, start, end, display, sections, metadata, visual or {}, voice or {})
            record = self.job_service.submit_path(package, tts_provider=tts_provider, render_engine="ffmpeg_motion", output_format="vertical", channel_id=channel_id)
            project_id = f"zodiac-{item.id}-{start.isoformat()}-{batch_id[-8:]}"
            self.job_service.registry.set_project(record.job_id, project_id)
            metadata = {
                "workflow": "zodiac-weekly",
                "brand": "คนเหนือดวง",
                "batchId": batch_id,
                "week": display,
                "zodiacId": item.id,
                "zodiacTh": item.name_th,
                "packagePath": str(package),
            }
            self.job_service.registry.set_metadata(record.job_id, metadata)
            current = self.job_service.registry.get(record.job_id)
            if current:
                self.persistence.upsert_job(current)
            self.persistence.ensure_project(project_id, f"ราศี{item.name_th} · {display}", 1, "RENDERING", "zodiac", channel_id)
            children.append({
                "zodiac": item.model_dump(),
                "projectId": project_id,
                "jobId": record.job_id,
                "package": str(package),
                "metadataPath": str(metadata_path),
            })
        batch = {
            "schema": "autoclip.zodiac-weekly-batch.v1",
            "batchId": batch_id,
            "brand": "คนเหนือดวง",
            "status": "RUNNING",
            "createdAt": datetime.now().astimezone().isoformat(),
            "ttsProvider": tts_provider,
            "channelId": channel_id,
            "visual": visual or {},
            "voice": voice or {"voice": "Iapetus", "language": "th-TH", "speed": 1.10},
            "week": {
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "displayTh": display,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "display_th": display,
            },
            "children": children,
        }
        self._write(batch_dir / "batch.json", batch)
        self._write_upload_csv(batch)
        self.persistence.ensure_project(batch_id, f"คนเหนือดวง · {display}", 12, "RENDERING", "zodiac_batch", channel_id)
        return self.get_batch(batch_id)

    def get_batch(self, batch_id: str) -> dict:
        batch = self._load(batch_id)
        completed = failed = running = 0
        for child in batch["children"]:
            record = self.job_service.restore(child["jobId"])
            status = str(record.status) if record else "FAILED"
            child["status"] = status
            child["progress"] = record.progress if record else 0
            child["currentStep"] = record.current_step if record else "ไม่พบงาน"
            child["error"] = record.error if record else {"code": "JOB_NOT_FOUND", "message": "ไม่พบงาน"}
            child["videoAvailable"] = bool(record and status == "COMPLETED" and self.job_service.final_video(record.job_id).is_file())
            child["published"] = self.persistence.get_published(child["projectId"]) if "projectId" in child else False
            child["metadata"] = json.loads(Path(child["metadataPath"]).read_text(encoding="utf-8"))
            if child["videoAvailable"]:
                self._sync_video_metadata(child)
            if status == "COMPLETED": completed += 1
            elif status == "FAILED": failed += 1
            else: running += 1
        batch["summary"] = {"total": 12, "completed": completed, "failed": failed, "running": running}
        titles = [child["metadata"]["title"] for child in batch["children"]]
        if len(batch["children"]) != 12 or len(set(titles)) != len(titles):
            raise AppError("ZODIAC_METADATA_INVALID", "ข้อมูลเผยแพร่ต้องครบ 12 ราศีและชื่อวิดีโอต้องไม่ซ้ำกัน")
        if completed == 12:
            batch["status"] = "COMPLETED"
        elif running:
            batch["status"] = "RUNNING"
        elif completed and failed:
            batch["status"] = "PARTIAL"
        else:
            batch["status"] = "FAILED"
        self._write(self.root / batch_id / "batch.json", batch)
        self.persistence.update_project_status(batch_id, batch["status"])
        return batch

    def list_batches(self) -> list[dict]:
        batches = []
        for path in self.root.glob("zodiac-weekly-*/batch.json"):
            try:
                batches.append(self.get_batch(path.parent.name))
            except (AppError, OSError, ValueError, json.JSONDecodeError):
                continue
        return sorted(batches, key=lambda item: item.get("createdAt", ""), reverse=True)

    def retry_failed(self, batch_id: str) -> dict:
        batch = self.get_batch(batch_id)
        retried = 0
        for child in batch["children"]:
            if child["status"] != "FAILED":
                continue
            package = Path(child["package"])
            record = self.job_service.submit_path(package, render_engine="ffmpeg_motion", output_format="vertical", channel_id=batch.get("channelId", "undefined"))
            child["jobId"] = record.job_id
            self.job_service.registry.set_project(record.job_id, child["projectId"])
            self.job_service.registry.set_metadata(record.job_id, {
                "workflow": "zodiac-weekly", "brand": "คนเหนือดวง", "batchId": batch_id,
                "week": batch["week"]["displayTh"], "zodiacId": child["zodiac"]["id"],
                "zodiacTh": child["zodiac"]["name_th"], "packagePath": child["package"],
            })
            retried += 1
        if not retried:
            raise AppError("ZODIAC_NOTHING_TO_RETRY", "ไม่มีราศีที่ล้มเหลวให้ลองใหม่")
        stored = {key: value for key, value in batch.items() if key not in {"summary"}}
        for child in stored["children"]:
            for key in ("status", "progress", "currentStep", "error", "videoAvailable"):
                child.pop(key, None)
        self._write(self.root / batch_id / "batch.json", stored)
        return self.get_batch(batch_id)

    def regenerate_child(self, batch_id: str, zodiac_id: str) -> dict:
        batch = self.get_batch(batch_id)
        child = self._child(batch, zodiac_id)
        if child["status"] not in {"FAILED", "COMPLETED"}:
            raise AppError("ZODIAC_JOB_RUNNING", "ราศีนี้กำลังทำงานอยู่")
        record = self.job_service.submit_path(
            Path(child["package"]), tts_provider=batch.get("ttsProvider", "google-gemini"),
            render_engine="ffmpeg_motion", output_format="vertical", channel_id=batch.get("channelId", "undefined"),
        )
        child["jobId"] = record.job_id
        self.job_service.registry.set_project(record.job_id, child["projectId"])
        self.job_service.registry.set_metadata(record.job_id, {
            "workflow": "zodiac-weekly", "brand": "คนเหนือดวง", "batchId": batch_id,
            "week": batch["week"]["displayTh"], "zodiacId": zodiac_id,
            "zodiacTh": child["zodiac"]["name_th"], "packagePath": child["package"],
        })
        self._store_batch_without_runtime(batch)
        return self.get_batch(batch_id)

    def delete_batch(self, batch_id: str) -> dict:
        batch = self.get_batch(batch_id)
        if batch["summary"]["running"]:
            raise AppError("ZODIAC_BATCH_RUNNING", "ลบชุดงานที่กำลังประมวลผลไม่ได้")
        workspace = self.root.parent.resolve()
        batch_dir = (self.root / batch_id).resolve()
        if batch_dir.parent != self.root.resolve():
            raise AppError("ZIP_SECURITY_VIOLATION", "ตำแหน่งชุดงานไม่ปลอดภัย")
        for child in batch["children"]:
            job_dir = (workspace / child["jobId"]).resolve()
            if job_dir.parent != workspace:
                raise AppError("ZIP_SECURITY_VIOLATION", "ตำแหน่งงานลูกไม่ปลอดภัย")
            if job_dir.is_dir() and not job_dir.is_symlink():
                shutil.rmtree(job_dir)
            self.persistence.delete_project(child["projectId"])
        self.persistence.delete_project(batch_id)
        if batch_dir.is_dir() and not batch_dir.is_symlink():
            shutil.rmtree(batch_dir)
        return {"status": "DELETED", "batchId": batch_id, "deletedChildren": len(batch["children"])}

    def update_metadata(self, batch_id: str, zodiac_id: str, values: dict) -> dict:
        batch = self._load(batch_id)
        child = self._child(batch, zodiac_id)
        metadata = json.loads(Path(child["metadataPath"]).read_text(encoding="utf-8"))
        metadata.update(values)
        self._validate_metadata(metadata, child["zodiac"])
        self._write(Path(child["metadataPath"]), metadata)
        self._write_upload_csv(batch)
        if self.job_service.final_video(child["jobId"]).is_file():
            self._sync_video_metadata(child, metadata)
        return metadata

    def regenerate_metadata(self, batch_id: str) -> dict:
        batch = self._load(batch_id)
        start = date.fromisoformat(batch["week"]["startDate"])
        end = date.fromisoformat(batch["week"]["endDate"])
        for child in batch["children"]:
            definition = ZodiacDefinition.model_validate(child["zodiac"])
            with zipfile.ZipFile(child["package"]) as archive:
                script = Script.model_validate_json(archive.read("script.json"))
            sections = [(scene.id.split("-")[-1], scene.tts_text or scene.narration) for scene in script.scenes]
            metadata = self._metadata(definition, start, end, batch["week"]["displayTh"], sections)
            self._write(Path(child["metadataPath"]), metadata)
            if self.job_service.final_video(child["jobId"]).is_file():
                self._sync_video_metadata(child, metadata)
        self._write_upload_csv(batch)
        return self.get_batch(batch_id)

    def metadata_path(self, batch_id: str, zodiac_id: str) -> Path:
        return Path(self._child(self._load(batch_id), zodiac_id)["metadataPath"])

    def csv_path(self, batch_id: str) -> Path:
        batch = self._load(batch_id)
        return self._write_upload_csv(batch)

    def metadata_archive(self, batch_id: str) -> Path:
        batch = self._load(batch_id)
        output = self.root / batch_id / f"{batch_id}-metadata.zip"
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for child in batch["children"]:
                path = Path(child["metadataPath"])
                archive.write(path, path.name)
            csv_path = self._write_upload_csv(batch)
            archive.write(csv_path, csv_path.name)
        return output

    def package_path(self, batch_id: str, zodiac_id: str) -> Path:
        batch = self._load(batch_id)
        child = next((item for item in batch["children"] if item["zodiac"]["id"] == zodiac_id), None)
        if not child:
            raise AppError("ZODIAC_NOT_FOUND", "ไม่พบราศีในชุดงานนี้")
        path = Path(child["package"])
        if not path.is_file():
            raise AppError("PACKAGE_NOT_READY", "ไม่พบ ZIP ของราศีนี้")
        return path

    def video_path(self, batch_id: str, zodiac_id: str) -> Path:
        batch = self.get_batch(batch_id)
        child = next((item for item in batch["children"] if item["zodiac"]["id"] == zodiac_id), None)
        if not child or not child["videoAvailable"]:
            raise AppError("VIDEO_NOT_READY", "วิดีโอราศีนี้ยังไม่พร้อม")
        return self.job_service.final_video(child["jobId"])

    def video_filename(self, batch_id: str, zodiac_id: str) -> str:
        child = self._child(self._load(batch_id), zodiac_id)
        metadata = json.loads(Path(child["metadataPath"]).read_text(encoding="utf-8"))
        return metadata["video_file"]

    @staticmethod
    def _container_description(metadata: dict) -> str:
        return metadata["description"]

    def _sync_video_metadata(self, child: dict, metadata: dict | None = None) -> None:
        metadata = metadata or json.loads(Path(child["metadataPath"]).read_text(encoding="utf-8"))
        digest = hashlib.sha256(json.dumps(metadata, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        marker = Path(child["metadataPath"]).with_suffix(".mp4-metadata.sha256")
        if marker.is_file() and marker.read_text(encoding="utf-8").strip() == digest:
            return
        if self.job_service.update_video_metadata_tags(
            child["jobId"], metadata["title"], self._container_description(metadata), "คนเหนือดวง", ", ".join(metadata["tags"])
        ):
            marker.write_text(digest, encoding="utf-8")

    def archive(self, batch_id: str, kind: str) -> Path:
        batch = self.get_batch(batch_id)
        output = self.root / batch_id / f"{batch_id}-{kind}.zip"
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for child in batch["children"]:
                if kind == "packages":
                    path = Path(child["package"])
                else:
                    path = self.job_service.final_video(child["jobId"]) if child["videoAvailable"] else Path()
                if path.is_file():
                    arcname = path.name if kind == "packages" else child["metadata"]["video_file"]
                    archive.write(path, arcname)
        if not output.is_file() or output.stat().st_size < 100:
            raise AppError("ZODIAC_ARCHIVE_EMPTY", "ยังไม่มีไฟล์พร้อมดาวน์โหลด")
        return output

    def complete_archive(self, batch_id: str) -> Path:
        batch = self.get_batch(batch_id)
        start, end = batch["week"]["startDate"], batch["week"]["endDate"]
        folder = f"คนเหนือดวง-{start}-to-{end}"
        output = self.root / batch_id / f"{folder}.zip"
        failed = []
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for child in batch["children"]:
                zodiac = child["zodiac"]
                if not child["videoAvailable"]:
                    failed.append(zodiac["id"])
                    continue
                directory = f"{zodiac['order']:02d}-{zodiac['id']}"
                video = self.job_service.final_video(child["jobId"])
                metadata = Path(child["metadataPath"])
                archive.write(video, f"{folder}/{directory}/{child['metadata']['video_file']}")
                archive.write(metadata, f"{folder}/{directory}/{metadata.name}")
            csv_path = self._write_upload_csv(batch)
            archive.write(csv_path, f"{folder}/youtube-upload.csv")
            report = {"expected": 12, "completed": batch["summary"]["completed"], "failed": len(failed), "failed_zodiacs": failed}
            archive.writestr(f"{folder}/batch-report.json", json.dumps(report, ensure_ascii=False, indent=2))
        return output

    def _store_batch_without_runtime(self, batch: dict) -> None:
        stored = {key: value for key, value in batch.items() if key != "summary"}
        for child in stored["children"]:
            for key in ("status", "progress", "currentStep", "error", "videoAvailable", "metadata"):
                child.pop(key, None)
        self._write(self.root / batch["batchId"] / "batch.json", stored)

    def _build_package(self, batch_dir: Path, zodiac: ZodiacDefinition, start: date, end: date, display: str, sections: list[tuple[str, str]], metadata: dict, visual: dict | None = None, voice: dict | None = None) -> Path:
        package_dir = batch_dir / zodiac.id
        images = package_dir / "images"
        images.mkdir(parents=True)
        visual = visual or {}
        date_overlay = visual.get("date_overlay") or {}
        source = self.templates_root / zodiac.template
        if not source.is_file():
            raise AppError("ZODIAC_TEMPLATE_MISSING", f"ไม่พบไฟล์ต้นแบบสำหรับราศี {zodiac.name_th} ({source.name})")
        if not display or not str(display).strip():
            display = thai_week_range(start, end)
        if date_overlay.get("enabled", True):
            self._overlay_date(source, images / "template.png", display)
        else:
            self._prepare_template(source, images / "template.png")
        motion_config = visual.get("motion") or {}
        motion_enabled = motion_config.get("enabled", False)
        voice = voice or {}
        motions = ("slow_zoom_in", "gentle_float", "slow_zoom_out", "pan_up", "documentary_pan", "slow_zoom_out")
        scenes = []
        for index, (label, text) in enumerate(sections, 1):
            scenes.append({
                "id": f"scene-{index:02d}-{label}",
                "image": "images/template.png",
                "narration": text,
                "tts_text": text,
                "subtitle": text,
                "motion": motions[index - 1] if motion_enabled else "none",
                "motion_speed": "slow",
                "motion_intensity": 0.04,
                "focus": "center",
                "transition": "fade" if index < len(sections) else "none",
            })
        project_id = f"zodiac-{zodiac.id}-{start.isoformat()}-{batch_dir.name[-8:]}"
        script = {
            "project": {"id": project_id, "title": f"ราศี{zodiac.name_th} · {display} | คนเหนือดวง", "language": "th-TH", "resolution": "1080x1920", "fps": 30},
            "voice": {"provider": "google-gemini", "voice": voice.get("voice", "Iapetus"), "speed": voice.get("speed", 1.10), "style_prompt": TTS_STYLE},
            "scenes": scenes,
        }
        Script.model_validate(script)
        (package_dir / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
        (package_dir / "video-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        zip_path = batch_dir / f"{zodiac.order:02d}-{zodiac.id}-{start.isoformat()}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in package_dir.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(package_dir).as_posix())
        check_dir = batch_dir / f"validate-{zodiac.id}"
        PackageService(100 * 1024 * 1024).extract_and_validate(zip_path, check_dir)
        shutil.rmtree(check_dir)
        return zip_path

    @staticmethod
    def _metadata(zodiac: ZodiacDefinition, start: date, end: date, display: str, sections: list[tuple[str, str]]) -> dict:
        content = dict(sections)
        hook = content["hook"].strip().rstrip("ครับ").rstrip("。.! ")
        short_hook = hook.replace(f"ราศี{zodiac.name_th} ", "", 1)
        if len(short_hook) > 70:
            short_hook = short_hook[:70].rsplit(" ", 1)[0].rstrip("…,. ") + "…"
        title = f"ราศี{zodiac.name_th} {short_hook} | {display}"
        disclaimer = "การดูดวงเป็นความเชื่อส่วนบุคคล โปรดใช้วิจารณญาณในการรับชม"
        description = "\n".join([
            f"ดวงรายสัปดาห์ราศี{zodiac.name_th}", f"ประจำวันที่ {display}", "",
            content.get("overview") or content["hook"], "", f"การงาน: {content['work'].replace('ด้านการงาน ', '', 1)}",
            f"การเงิน: {content['finance'].replace('ด้านการเงิน ', '', 1)}",
            f"ความรัก: {content['love'].replace('ด้านความรัก ', '', 1)}",
            f"คำแนะนำ: {content['advice'].replace('คำแนะนำคือ ', '', 1)}", "", disclaimer,
            "", f"#ราศี{zodiac.name_th} #ดวงรายสัปดาห์ #ดูดวง #คนเหนือดวง",
        ])
        metadata = {
            "zodiac_id": zodiac.id, "zodiac_th": f"ราศี{zodiac.name_th}", "zodiac_en": zodiac.name_en,
            "week": {"start_date": start.isoformat(), "end_date": end.isoformat(), "display_th": display},
            "video_file": f"{zodiac.order:02d}-{zodiac.id}.mp4", "title": title, "description": description,
            "hashtags": [f"#ราศี{zodiac.name_th}", "#ดวงรายสัปดาห์", "#ดูดวง", "#คนเหนือดวง"],
            "tags": [f"ราศี{zodiac.name_th}", f"ดวงราศี{zodiac.name_th}", "ดวงรายสัปดาห์", "ดวงสัปดาห์นี้", "ดูดวง", "ดูดวง 12 ราศี", zodiac.name_en.title(), f"{zodiac.name_en.title()} horoscope", "weekly horoscope"],
            "hook": content["hook"], "visibility": "private", "language": "th-TH", "made_for_kids": False,
        }
        ZodiacWeeklyService._validate_metadata(metadata, zodiac.model_dump())
        return metadata

    @staticmethod
    def _validate_metadata(metadata: dict, zodiac: dict) -> None:
        required = ("title", "description", "hashtags", "tags")
        if any(not metadata.get(key) for key in required):
            raise AppError("ZODIAC_METADATA_INVALID", "ข้อมูลสำหรับเผยแพร่ไม่ครบ")
        name = f"ราศี{zodiac['name_th']}"
        if name not in metadata["title"] or f"#{name}" not in metadata["hashtags"]:
            raise AppError("ZODIAC_METADATA_INVALID", "ชื่อหรือแฮชแท็กไม่ตรงกับราศี")
        if "การดูดวงเป็นความเชื่อส่วนบุคคล โปรดใช้วิจารณญาณในการรับชม" not in metadata["description"]:
            raise AppError("ZODIAC_METADATA_INVALID", "คำอธิบายไม่มีข้อความแจ้งเตือนมาตรฐาน")

    def _write_upload_csv(self, batch: dict) -> Path:
        path = self.root / batch["batchId"] / "youtube-upload.csv"
        fields = ["order", "zodiac_id", "zodiac_th", "filename", "title", "description", "hashtags", "tags", "week_start", "week_end", "visibility"]
        with self._lock, path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for child in batch["children"]:
                meta = json.loads(Path(child["metadataPath"]).read_text(encoding="utf-8"))
                writer.writerow({"order": child["zodiac"]["order"], "zodiac_id": meta["zodiac_id"], "zodiac_th": meta["zodiac_th"], "filename": meta["video_file"], "title": meta["title"], "description": meta["description"], "hashtags": " ".join(meta["hashtags"]), "tags": "|".join(meta["tags"]), "week_start": meta["week"]["start_date"], "week_end": meta["week"]["end_date"], "visibility": meta["visibility"]})
        return path

    @staticmethod
    def _child(batch: dict, zodiac_id: str) -> dict:
        child = next((item for item in batch["children"] if item["zodiac"]["id"] == zodiac_id), None)
        if not child:
            raise AppError("ZODIAC_NOT_FOUND", "ไม่พบราศีในชุดงานนี้")
        return child

    @staticmethod
    def _sections_from_reading(reading: dict) -> list[tuple[str, str]]:
        required = ("hook", "work", "finance", "love", "advice")
        missing = [key for key in required if not str(reading.get(key, "")).strip()]
        if missing:
            raise AppError("ZODIAC_CONTENT_INVALID", "ข้อมูลคำทำนายไม่ครบ", {"fields": missing})
        ordered = ("hook", "overview", "work", "finance", "love", "advice", "closing")
        # Preserve exactly the semantic sections explicitly supplied. In
        # particular, do not manufacture a closing/CTA after advice.
        return [(key, str(reading[key]).strip()) for key in ordered if reading.get(key) is not None and str(reading[key]).strip()]

    def _overlay_date(self, source: Path, output: Path, display: str) -> None:
        if not display or not str(display).strip():
            raise AppError("ZODIAC_DATE_EMPTY", "ข้อความวันที่สำหรับ date overlay ว่างเปล่า")
        if not source.is_file():
            raise AppError("ZODIAC_TEMPLATE_MISSING", f"ไม่พบไฟล์ต้นแบบ: {source.name}")
        image = Image.open(source).convert("RGB")
        draw = ImageDraw.Draw(image)
        # All supplied masters share 941x1672 and the same date plaque.
        box = (278, 1144, 663, 1198)
        draw.rounded_rectangle(box, radius=5, fill=(13, 15, 20))
        font = ImageFont.truetype(str(self.font_path), 39)
        left, top, right, bottom = draw.textbbox((0, 0), display, font=font)
        x = box[0] + (box[2] - box[0] - (right - left)) / 2
        y = box[1] + (box[3] - box[1] - (bottom - top)) / 2 - top
        draw.text((x, y), display, font=font, fill=(255, 242, 206), stroke_width=1, stroke_fill=(92, 59, 24))
        image = image.resize((1080, 1920), Image.Resampling.LANCZOS)
        image.save(output, format="PNG")

    @staticmethod
    def _prepare_template(source: Path, output: Path) -> None:
        image = Image.open(source).convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS)
        image.save(output, format="PNG")

    @staticmethod
    def _content(zodiac: ZodiacDefinition, start: date) -> list[tuple[str, str]]:
        i = (zodiac.order + start.toordinal()) % 4
        hooks = (
            f"ราศี{zodiac.name_th} สัปดาห์นี้มีจังหวะหนึ่งที่ไม่ควรรีบตัดสินใจ เพราะคำตอบที่ดีอาจมาช้ากว่าที่คิดครับ",
            f"ราศี{zodiac.name_th} มีโอกาสใหม่กำลังเข้ามา แต่สิ่งสำคัญคือเลือกให้ถูกจังหวะ ไม่ใช่รีบคว้าไว้ทุกอย่างครับ",
            f"ราศี{zodiac.name_th} สัปดาห์นี้ยิ่งใจเย็น ยิ่งเห็นทางออกของเรื่องที่เคยดูยุ่งยากชัดขึ้นครับ",
            f"ราศี{zodiac.name_th} ช่วงนี้อาจมีเรื่องให้เลือกสองทาง และรายละเอียดเล็ก ๆ จะช่วยบอกว่าทางไหนเหมาะกับคุณครับ",
        )
        work = (
            "ด้านการงาน งานที่ต้องประสานหลายคนควรยืนยันรายละเอียดให้ชัด มีโอกาสได้รับความไว้วางใจเพิ่มจากความสม่ำเสมอ",
            "ด้านการงาน เหมาะกับการปิดงานเก่าและวางระบบใหม่ ความคิดที่เสนออย่างใจเย็นมีโอกาสได้รับการรับฟัง",
            "ด้านการงาน อาจมีโจทย์เร่งด่วนเข้ามา แต่การแบ่งงานเป็นส่วนเล็ก ๆ จะช่วยให้ควบคุมสถานการณ์ได้ดี",
            "ด้านการงาน มีแนวโน้มได้ร่วมมือกับคนที่มีวิธีคิดต่างกัน ฟังให้ครบก่อนตอบจะสร้างผลลัพธ์ที่ดี",
        )
        finance = (
            "ด้านการเงิน ควรแยกรายจ่ายจำเป็นออกจากความอยากชั่วคราว มีโอกาสรักษาเงินได้มากขึ้นจากการวางแผนล่วงหน้า",
            "ด้านการเงิน เหมาะกับการตรวจค่าใช้จ่ายเล็ก ๆ ที่เกิดซ้ำ หลีกเลี่ยงการตัดสินใจเพราะความรีบร้อนหรือคำชวนเกินจริง",
            "ด้านการเงิน มีแนวโน้มจัดการได้ดีขึ้นเมื่อกำหนดวงเงินชัดเจน รายรับพิเศษถ้ามีควรแบ่งเก็บก่อนใช้",
            "ด้านการเงิน ช่วงนี้ควรรอบคอบกับข้อตกลงและตัวเลข อ่านรายละเอียดให้ครบก่อนตอบรับทุกครั้ง",
        )
        love = (
            "ด้านความรัก คนมีคู่ควรพูดความต้องการตรง ๆ อย่างอ่อนโยน คนโสดอาจได้รู้จักคนใหม่ผ่านกิจกรรมหรือเพื่อนร่วมงาน",
            "ด้านความรัก การฟังโดยไม่รีบสรุปจะช่วยลดความเข้าใจผิด คนโสดควรให้เวลาความสัมพันธ์ค่อย ๆ เปิดเผยตัวตน",
            "ด้านความรัก บรรยากาศจะดีขึ้นเมื่อแบ่งเวลาให้กันอย่างตั้งใจ คนโสดมีโอกาสพบคนที่คุยแล้วรู้สึกสบายใจ",
            "ด้านความรัก อย่าเก็บคำถามไว้นานเกินไป การคุยด้วยความจริงใจช่วยให้ทั้งความสัมพันธ์ใหม่และเดิมชัดเจนขึ้น",
        )
        advice = (
            "คำแนะนำคือ อย่าใช้ความเร็วแทนความชัดเจน หยุดคิดสักนิดก่อนตอบ แล้วคุณจะเลือกได้เบาใจกว่าเดิม",
            "คำแนะนำคือ ให้ความสำคัญกับสิ่งที่ควบคุมได้ และปล่อยเรื่องที่ยังไม่มีคำตอบให้ค่อย ๆ คลี่คลาย",
            "คำแนะนำคือ รักษาจังหวะของตัวเอง ความก้าวหน้าเล็ก ๆ ที่ทำต่อเนื่องมีค่ากว่าการเร่งจนหมดแรง",
            "คำแนะนำคือ เชื่อข้อมูลที่ตรวจสอบได้มากกว่าความกังวล แล้วสัปดาห์นี้จะจัดการง่ายขึ้นครับ",
        )
        closing = "คำทำนายนี้เป็นแนวทางเพื่อความบันเทิง ใช้สติและข้อมูลจริงประกอบการตัดสินใจเสมอ ขอให้สัปดาห์นี้เป็นช่วงเวลาที่ดีของคุณครับ"
        return [("hook", hooks[i]), ("work", work[i]), ("finance", finance[i]), ("love", love[i]), ("advice", advice[i]), ("closing", closing)]

    def _load(self, batch_id: str) -> dict:
        if not batch_id or "/" in batch_id or ".." in batch_id:
            raise AppError("ZODIAC_BATCH_NOT_FOUND", "ไม่พบชุดงานดวงรายสัปดาห์")
        path = self.root / batch_id / "batch.json"
        if not path.is_file():
            raise AppError("ZODIAC_BATCH_NOT_FOUND", "ไม่พบชุดงานดวงรายสัปดาห์")
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, path: Path, payload: dict) -> None:
        with self._lock:
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(path)
