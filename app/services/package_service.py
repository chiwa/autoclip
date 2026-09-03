from __future__ import annotations

import json
import stat
import zipfile
from pathlib import Path, PurePosixPath

from pydantic import ValidationError

from app.domain.errors import AppError
from app.domain.models import Script

IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
AUDIO_TYPES = {".mp3", ".wav", ".m4a", ".aac"}
REJECTED_TYPES = {".exe", ".dll", ".so", ".dylib", ".sh", ".bash", ".py", ".pyc", ".bat", ".cmd", ".com", ".scr", ".msi"}


class PackageService:
    def __init__(self, max_extracted_bytes: int):
        self.max_extracted_bytes = max_extracted_bytes

    def extract_and_validate(self, zip_path: Path, destination: Path) -> tuple[Script, Path | None]:
        try:
            archive = zipfile.ZipFile(zip_path)
        except (zipfile.BadZipFile, OSError) as exc:
            raise AppError("PACKAGE_INVALID", "Uploaded file is not a valid ZIP archive") from exc
        with archive:
            entries = archive.infolist()
            names: set[str] = set()
            total = 0
            for entry in entries:
                normalized = self._validate_entry(entry)
                if normalized in names:
                    raise AppError("ZIP_SECURITY_VIOLATION", "ZIP contains duplicate paths")
                names.add(normalized)
                total += entry.file_size
                if total > self.max_extracted_bytes:
                    raise AppError("UPLOAD_TOO_LARGE", "Extracted package exceeds the configured size limit")
            if "script.json" not in names:
                raise AppError("PACKAGE_INVALID", "script.json must exist at ZIP root")
            for entry in entries:
                self._extract_entry(archive, entry, destination)
        script = self._parse_script(destination / "script.json")
        self._validate_assets(script, destination)
        return script, self._find_bgm(destination)

    def _validate_entry(self, entry: zipfile.ZipInfo) -> str:
        name = entry.filename
        path = PurePosixPath(name)
        if not name or path.is_absolute() or name.startswith(("/", "\\")) or "\\" in name or ".." in path.parts:
            raise AppError("ZIP_SECURITY_VIOLATION", "ZIP contains an unsafe path")
        mode = entry.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise AppError("ZIP_SECURITY_VIOLATION", "ZIP symbolic links are not allowed")
        if not entry.is_dir() and path.suffix.lower() in REJECTED_TYPES:
            raise AppError("ZIP_SECURITY_VIOLATION", "ZIP contains a prohibited file type")
        if not entry.is_dir() and path.as_posix() not in {"script.json", "video-metadata.json"} and path.suffix.lower() not in IMAGE_TYPES | AUDIO_TYPES:
            raise AppError("UNSUPPORTED_ASSET_TYPE", "ZIP contains an unsupported file type", {"path": path.as_posix()})
        if entry.file_size > 10 * 1024 * 1024 and entry.compress_size and entry.file_size / entry.compress_size > 1000:
            raise AppError("ZIP_SECURITY_VIOLATION", "ZIP entry has a suspicious compression ratio")
        return path.as_posix().rstrip("/")

    def _extract_entry(self, archive: zipfile.ZipFile, entry: zipfile.ZipInfo, destination: Path) -> None:
        target = (destination / PurePosixPath(entry.filename)).resolve()
        if target != destination.resolve() and destination.resolve() not in target.parents:
            raise AppError("ZIP_SECURITY_VIOLATION", "ZIP entry escapes the job workspace")
        if entry.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(entry) as source, target.open("wb") as output:
            remaining = entry.file_size
            while remaining:
                chunk = source.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                output.write(chunk)
                remaining -= len(chunk)

    def _parse_script(self, path: Path) -> Script:
        try:
            content = path.read_text(encoding="utf-8")
            return Script.model_validate(json.loads(content))
        except (UnicodeDecodeError, json.JSONDecodeError, ValidationError) as exc:
            # Keep the public error actionable while avoiding absolute paths or a traceback.
            validation = str(exc).replace("\\n", " ")[:500]
            raise AppError("SCRIPT_JSON_INVALID", f"script.json is invalid: {validation}", {"validation": validation}) from exc

    def _validate_assets(self, script: Script, root: Path) -> None:
        for scene in script.scenes:
            suffix = Path(scene.image).suffix.lower()
            if suffix not in IMAGE_TYPES:
                raise AppError("UNSUPPORTED_ASSET_TYPE", "Scene image type is unsupported", {"sceneId": scene.id, "path": scene.image})
            asset = (root / scene.image).resolve()
            if root.resolve() not in asset.parents or not asset.is_file():
                raise AppError("ASSET_NOT_FOUND", "Referenced asset was not found", {"sceneId": scene.id, "path": scene.image})

    def _find_bgm(self, root: Path) -> Path | None:
        audio_dir = root / "audio"
        if not audio_dir.is_dir():
            return None
        matches = [p for p in audio_dir.iterdir() if p.is_file() and p.stem.lower() == "bgm"]
        unsupported = [p for p in matches if p.suffix.lower() not in AUDIO_TYPES]
        if unsupported:
            raise AppError("UNSUPPORTED_ASSET_TYPE", "Background music type is unsupported", {"path": f"audio/{unsupported[0].name}"})
        supported = [p for p in matches if p.suffix.lower() in AUDIO_TYPES]
        if len(supported) > 1:
            raise AppError("PACKAGE_INVALID", "Package contains multiple background music files")
        return supported[0] if supported else None
