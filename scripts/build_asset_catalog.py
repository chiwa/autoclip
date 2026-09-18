#!/usr/bin/env python3
"""AutoClip Reusable Asset Catalog Builder.

Scans `assets/` to build and maintain the permanent, deduplicated Reusable
Asset Library at `assets/reusable-library/`. Uses APFS clone copying when
available on macOS, computes SHA-256 fingerprints, generates thumbnails and
contact sheets, extracts rich scene metadata from project files, and produces
deterministic indexes (`assets-index.jsonl` and `assets-index.md`).
"""

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from PIL import Image, ImageDraw, ImageFont

# Allowed image extensions
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

# Directory names to strictly exclude from scanning
EXCLUDED_DIR_NAMES = {
    "reusable-library",
    "catalog",
    "thumbnails",
    "contact-sheets",
    "originals",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    ".native-venv",
    "node_modules",
    "tmp",
    "temp",
    "cache",
    "dist",
}

# Prefixes in root assets/ that indicate temporary or test scratch files
EXCLUDED_ROOT_PREFIXES = ("test_", "crop_", "check_")


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file efficiently."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def copy_file_apfs_clone(src: Path, dst: Path) -> bool:
    """Copy a file using macOS APFS clone (copy-on-write) with fallback to shutil.copy2."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return True

    # Try macOS native `cp -c` for instant APFS clone copy
    if sys.platform == "darwin":
        try:
            res = subprocess.run(
                ["cp", "-c", str(src), str(dst)],
                capture_output=True,
                check=False,
            )
            if res.returncode == 0 and dst.exists():
                return True
        except Exception:
            pass

    # Fallback to standard copy2
    shutil.copy2(src, dst)
    return dst.exists()


def get_image_info(filepath: Path) -> Tuple[int, int, str, str]:
    """Read image dimensions, format, and aspect ratio without loading full pixel data."""
    try:
        with Image.open(filepath) as img:
            w, h = img.size
            fmt = (img.format or filepath.suffix.lstrip(".").upper()).upper()

            # Calculate simplified aspect ratio
            if h == 0 or w == 0:
                aspect = "unknown"
            else:
                ratio = w / h
                if math.isclose(ratio, 9 / 16, rel_tol=0.08):
                    aspect = "9:16"
                elif math.isclose(ratio, 16 / 9, rel_tol=0.08):
                    aspect = "16:9"
                elif math.isclose(ratio, 1.0, rel_tol=0.05):
                    aspect = "1:1"
                elif math.isclose(ratio, 4 / 5, rel_tol=0.05):
                    aspect = "4:5"
                elif math.isclose(ratio, 4 / 3, rel_tol=0.05):
                    aspect = "4:3"
                elif math.isclose(ratio, 3 / 2, rel_tol=0.05):
                    aspect = "3:2"
                elif math.isclose(ratio, 2 / 3, rel_tol=0.05):
                    aspect = "2:3"
                else:
                    aspect = f"{w}:{h}"
            return w, h, fmt, aspect
    except Exception:
        return 0, 0, filepath.suffix.lstrip(".").upper(), "unknown"


def generate_thumbnail(src: Path, dst: Path, max_size: int = 320) -> bool:
    """Generate a high-quality, lightweight thumbnail preserving aspect ratio."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return True
    try:
        with Image.open(src) as img:
            # Convert RGBA/P to RGB for clean JPEG saving
            if img.mode in ("RGBA", "LA", "P"):
                rgb_img = Image.new("RGB", img.size, (18, 18, 18))
                if img.mode == "P":
                    img = img.convert("RGBA")
                rgb_img.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
            else:
                rgb_img = img.convert("RGB")

            rgb_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            rgb_img.save(dst, "JPEG", quality=85, optimize=True)
            return True
    except Exception as e:
        print(f"Warning: Failed to generate thumbnail for {src}: {e}", file=sys.stderr)
        return False


def is_production_asset(rel_path: Path) -> bool:
    """Filter out scratch, temporary, cache, and non-production files."""
    parts = rel_path.parts
    # Check if inside excluded directory
    for part in parts:
        if part in EXCLUDED_DIR_NAMES or part.startswith("."):
            return False

    # Check root assets/ files (length == 2 means assets/<filename>)
    if len(parts) == 2:
        filename = parts[1]
        for prefix in EXCLUDED_ROOT_PREFIXES:
            if filename.startswith(prefix):
                return False

    name_lower = rel_path.name.lower()
    if name_lower.startswith(".") or name_lower.endswith("~"):
        return False

    return True


def detect_brand(rel_path: Path, project_name: str, text_corpus: str) -> str:
    """Detect brand association based on path, project name, or metadata."""
    p_lower = str(rel_path).lower()
    proj_lower = project_name.lower()
    corpus_lower = text_corpus.lower()

    if "12ราศี" in p_lower or "zodiac" in p_lower or "12ราศี" in corpus_lower:
        return "12-zodiac"
    if "thai_java_zone" in p_lower or "thai-java-zone" in proj_lower or "thai java zone" in corpus_lower:
        return "thai-java-zone"
    if "mamase" in p_lower or "mamase" in proj_lower or "mamase" in corpus_lower:
        return "mamase"
    if "branding" in p_lower:
        if "mamase" in p_lower:
            return "mamase"
    return "generic"


def classify_role_and_reuse(
    rel_path: Path,
    scene_id: str,
    scene_role: str,
    brand: str,
    is_cover_scene: bool,
    has_topic_specific_text: bool,
    width: int,
    height: int,
) -> Tuple[str, str]:
    """Classify role and reuse recommendation following strict canonical rules."""
    p_lower = str(rel_path).lower()
    filename_lower = rel_path.name.lower()

    # Determine role
    if "branding" in p_lower or filename_lower in ("logo.png", "badge.png", "watermark.png"):
        role = "branding"
    elif "end-scene" in filename_lower or "end-scence" in filename_lower or "outro" in filename_lower or scene_role == "outro":
        role = "outro"
    elif "raw" in filename_lower or "artwork" in filename_lower:
        role = "raw artwork"
    elif "reference" in p_lower or "ref" in filename_lower:
        role = "reference"
    elif is_cover_scene or scene_role == "hook" or "hook" in filename_lower or scene_id in ("01", "scene-01", "1"):
        role = "hook"
    else:
        role = scene_role if scene_role in ("hook", "content", "outro", "branding", "reference") else "content"

    # Determine reuse recommendation
    # Rule 1: Scene 01 with topic-specific titles or hooks must NEVER be reuse_direct
    if role == "hook" and (has_topic_specific_text or is_cover_scene):
        reuse = "reuse_as_reference"
    elif role == "outro":
        # Outro cards can be directly reused ONLY for the same brand
        reuse = "reuse_direct" if brand in ("mamase", "12-zodiac", "thai-java-zone") else "reuse_as_reference"
    elif role == "branding":
        reuse = "reuse_direct"
    elif role == "reference":
        reuse = "reuse_as_reference"
    elif role == "raw artwork":
        reuse = "reuse_as_reference"
    elif role == "content":
        # Clean production content scenes
        if width > 0 and height > 0:
            reuse = "reuse_direct"
        else:
            reuse = "do_not_reuse"
    else:
        reuse = "reuse_as_reference"

    return role, reuse


def extract_manifest_metadata(proj_dir: Path) -> Dict[str, Any]:
    """Extract metadata from markdown manifests and READMEs in project dir."""
    manifest_data: Dict[str, Any] = {
        "visual_prompts": {},
        "descriptions": {},
        "topic": "",
        "notes": "",
    }
    manifest_names = [
        "asset-manifest.md",
        "visual-manifest.md",
        "visual-reference.md",
        "README.md",
        "readme.md",
    ]
    for m_name in manifest_names:
        m_path = proj_dir / m_name
        if not m_path.is_file():
            continue
        try:
            content = m_path.read_text(encoding="utf-8")
            # Look for title in first heading
            m_heading = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if m_heading and not manifest_data["topic"]:
                manifest_data["topic"] = m_heading.group(1).strip()

            # Parse scenes e.g. "### Scene 01: ..." or "### Scene 1: ..."
            scene_sections = re.split(r"(?=^###\s+Scene\s+\d+)", content, flags=re.MULTILINE)
            for sec in scene_sections:
                header_match = re.search(r"^###\s+Scene\s+(\d+)[:\s]*(.*)$", sec, re.MULTILINE)
                if header_match:
                    num_str = header_match.group(1).zfill(2)
                    sec_title = header_match.group(2).strip()
                    # Extract content or prompt
                    content_match = re.search(r"[-*]\s+\*\*Content:\*\*\s+(.+)$", sec, re.MULTILINE)
                    prompt_match = re.search(r"[-*]\s+\*\*Prompt:\*\*\s+(.+)$", sec, re.MULTILINE)
                    desc = content_match.group(1).strip() if content_match else sec_title
                    v_prompt = prompt_match.group(1).strip() if prompt_match else ""

                    manifest_data["descriptions"][num_str] = desc
                    if v_prompt:
                        manifest_data["visual_prompts"][num_str] = v_prompt
        except Exception:
            continue
    return manifest_data


def extract_project_context(proj_dir: Path) -> Dict[str, Any]:
    """Parse script.json and video-metadata.json in project directory."""
    context: Dict[str, Any] = {
        "project_id": proj_dir.name,
        "title": "",
        "topic": "",
        "description": "",
        "tags": [],
        "scenes": {},
        "outro_image": "",
    }

    # 1. script.json
    script_path = proj_dir / "script.json"
    if script_path.is_file():
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                s_data = json.load(f)
            proj_info = s_data.get("project", {})
            context["project_id"] = proj_info.get("id") or context["project_id"]
            context["title"] = proj_info.get("title", "")
            context["topic"] = proj_info.get("title", "")
            if "description" in s_data:
                context["description"] = s_data["description"]
            if "hashtags" in s_data:
                context["tags"] = [t.lstrip("#") for t in s_data["hashtags"]]

            # Parse scenes
            for s in s_data.get("scenes", []):
                s_id = str(s.get("id", ""))
                # normalized number if possible
                num_match = re.search(r"\d+", s_id)
                norm_num = num_match.group(0).zfill(2) if num_match else s_id
                img_ref = str(s.get("image", ""))
                img_name = Path(img_ref).name
                context["scenes"][img_name] = {
                    "scene_id": s_id,
                    "norm_num": norm_num,
                    "role": s.get("role", "content"),
                    "narration": s.get("narration", ""),
                    "motion": s.get("motion", ""),
                    "visual_prompt": s.get("visual_prompt", s.get("prompt", "")),
                }

            outro = s_data.get("outro", {})
            if outro and outro.get("enabled"):
                context["outro_image"] = Path(outro.get("image", "")).name
        except Exception:
            pass

    # 2. video-metadata.json
    vmeta_path = proj_dir / "video-metadata.json"
    if vmeta_path.is_file():
        try:
            with open(vmeta_path, "r", encoding="utf-8") as f:
                v_data = json.load(f)
            context["project_id"] = v_data.get("project_id") or context["project_id"]
            if not context["title"]:
                context["title"] = v_data.get("title", "")
            if not context["topic"]:
                context["topic"] = v_data.get("title", "")
            if not context["description"]:
                context["description"] = v_data.get("description", "")
            if not context["tags"] and "tags" in v_data:
                context["tags"] = v_data["tags"]
            if not context["outro_image"] and "outro" in v_data:
                context["outro_image"] = Path(v_data["outro"]).name
        except Exception:
            pass

    # 3. Markdown manifests
    manifest_data = extract_manifest_metadata(proj_dir)
    if not context["topic"] and manifest_data["topic"]:
        context["topic"] = manifest_data["topic"]
    context["manifest_scenes"] = manifest_data

    return context


class AssetCatalogBuilder:
    """Builds and manages the permanent Reusable Asset Library."""

    def __init__(self, repo_root: Path, library_dir: Optional[Path] = None):
        self.repo_root = repo_root.resolve()
        self.assets_dir = (self.repo_root / "assets").resolve()
        self.library_dir = (library_dir or (self.assets_dir / "reusable-library")).resolve()
        self.originals_dir = self.library_dir / "originals"
        self.thumbnails_dir = self.library_dir / "thumbnails"
        self.contact_sheets_dir = self.library_dir / "contact-sheets"
        self.index_jsonl_path = self.library_dir / "assets-index.jsonl"
        self.index_md_path = self.library_dir / "assets-index.md"
        self.state_json_path = self.library_dir / "catalog-state.json"

        # Project cache for metadata extraction
        self._project_contexts: Dict[Path, Dict[str, Any]] = {}

    def ensure_directories(self) -> None:
        """Create library directories if they do not exist."""
        self.originals_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
        self.contact_sheets_dir.mkdir(parents=True, exist_ok=True)

    def load_state(self) -> Dict[str, Any]:
        """Load prior catalog state for incremental updates."""
        if self.state_json_path.is_file():
            try:
                with open(self.state_json_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"files": {}, "last_updated": ""}

    def save_state(self, state: Dict[str, Any]) -> None:
        """Save catalog state atomically."""
        state["last_updated"] = datetime.now(timezone.utc).isoformat()
        temp_state = self.state_json_path.with_suffix(".tmp")
        with open(temp_state, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        temp_state.replace(self.state_json_path)

    def scan_asset_files(self) -> List[Path]:
        """Discover all eligible production image files in assets/."""
        image_files: List[Path] = []
        for root, dirs, files in os.walk(self.assets_dir):
            # Prune excluded directories in-place to avoid recursing
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIR_NAMES and not d.startswith(".")]

            root_path = Path(root)
            for f in sorted(files):
                ext = Path(f).suffix.lower()
                if ext in SUPPORTED_EXTENSIONS:
                    file_path = root_path / f
                    rel_path = file_path.relative_to(self.repo_root)
                    if is_production_asset(rel_path):
                        image_files.append(file_path)
        return sorted(image_files)

    def _get_project_context(self, file_path: Path) -> Dict[str, Any]:
        """Determine project context and cache it."""
        # Find project directory (direct child of assets/)
        rel = file_path.relative_to(self.assets_dir)
        proj_dir = self.assets_dir / rel.parts[0] if rel.parts else self.assets_dir
        if proj_dir not in self._project_contexts:
            self._project_contexts[proj_dir] = extract_project_context(proj_dir)
        return self._project_contexts[proj_dir]

    def build_asset_record(self, file_path: Path, sha256_hash: str) -> Dict[str, Any]:
        """Construct full metadata record for an image asset."""
        rel_path = file_path.relative_to(self.repo_root)
        proj_ctx = self._get_project_context(file_path)

        w, h, fmt, aspect = get_image_info(file_path)
        filename = file_path.name
        file_ext = file_path.suffix.lower()

        # Match scene
        scene_info = proj_ctx["scenes"].get(filename, {})
        norm_num = scene_info.get("norm_num")
        if not norm_num:
            # Try extract from filename e.g. "01.png", "scene-01.png"
            m = re.search(r"(\d+)", filename)
            if m:
                norm_num = m.group(1).zfill(2)
            else:
                norm_num = ""

        # Check manifests if scene info incomplete
        manifest_scenes = proj_ctx.get("manifest_scenes", {})
        m_desc = manifest_scenes.get("descriptions", {}).get(norm_num, "")
        m_prompt = manifest_scenes.get("visual_prompts", {}).get(norm_num, "")

        scene_id = scene_info.get("scene_id") or (f"scene-{norm_num}" if norm_num else filename)
        scene_role = scene_info.get("role", "content")
        narration = scene_info.get("narration", "")
        visual_prompt = scene_info.get("visual_prompt") or m_prompt
        description = m_desc or proj_ctx.get("description", "")
        topic = proj_ctx.get("topic") or proj_ctx.get("title", "")

        is_cover_scene = norm_num == "01" or "hook" in filename.lower()
        # Scene 01 or images with specific Thai/English titles have topic-specific text
        has_topic_specific_text = is_cover_scene or bool(topic and is_cover_scene)

        # Detect brand
        combined_text = f"{proj_ctx['project_id']} {topic} {description} {narration} {file_path}"
        brand = detect_brand(rel_path, proj_ctx["project_id"], combined_text)

        # Classify role and reuse recommendation
        role, reuse = classify_role_and_reuse(
            rel_path=rel_path,
            scene_id=scene_id,
            scene_role=scene_role,
            brand=brand,
            is_cover_scene=is_cover_scene,
            has_topic_specific_text=has_topic_specific_text,
            width=w,
            height=h,
        )

        # Library path uses sha256 to ensure zero duplicate filenames
        library_filename = f"{sha256_hash}{file_ext}"
        library_rel_path = f"assets/reusable-library/originals/{library_filename}"
        thumb_rel_path = f"assets/reusable-library/thumbnails/{sha256_hash}.jpg"

        tags = list(set(proj_ctx.get("tags", []) + [brand, role]))

        return {
            "asset_id": sha256_hash,
            "library_path": library_rel_path,
            "thumbnail_path": thumb_rel_path,
            "original_sources": [str(rel_path)],
            "source_project": proj_ctx["project_id"],
            "source_scene": scene_id,
            "scene_number": norm_num,
            "brand": brand,
            "role": role,
            "reuse": reuse,
            "topic": topic,
            "title": proj_ctx.get("title", topic),
            "description": description,
            "visual_prompt": visual_prompt,
            "narration": narration,
            "tags": sorted(tags),
            "width": w,
            "height": h,
            "format": fmt,
            "aspect_ratio": aspect,
            "file_size_bytes": file_path.stat().st_size,
        }

    def generate_contact_sheets(self, records_by_project: Dict[str, List[Dict[str, Any]]]) -> None:
        """Create visual contact sheet grids grouped by project."""
        for proj_id, records in records_by_project.items():
            if not records:
                continue

            # Sort records by scene number / id
            sorted_records = sorted(records, key=lambda r: (r.get("scene_number") or "99", r.get("source_scene", "")))

            # 3 columns layout
            cols = min(3, len(sorted_records))
            rows = math.ceil(len(sorted_records) / cols)
            thumb_w, thumb_h = 240, 426
            padding = 16
            header_h = 60
            caption_h = 40

            sheet_w = cols * thumb_w + (cols + 1) * padding
            sheet_h = header_h + rows * (thumb_h + caption_h) + (rows + 1) * padding

            sheet = Image.new("RGB", (sheet_w, sheet_h), (24, 26, 27))
            draw = ImageDraw.Draw(sheet)

            # Draw header
            header_text = f"Project: {proj_id} ({len(sorted_records)} scenes)"
            draw.text((padding, 18), header_text, fill=(240, 240, 240))

            for idx, rec in enumerate(sorted_records):
                c = idx % cols
                r = idx // cols
                x = padding + c * (thumb_w + padding)
                y = header_h + padding + r * (thumb_h + caption_h + padding)

                # Load thumbnail or original
                thumb_path = self.repo_root / rec["thumbnail_path"]
                if not thumb_path.exists():
                    thumb_path = self.repo_root / rec["library_path"]

                try:
                    if thumb_path.exists():
                        with Image.open(thumb_path) as im:
                            im_thumb = im.convert("RGB")
                            im_thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                            # center paste
                            px = x + (thumb_w - im_thumb.width) // 2
                            py = y + (thumb_h - im_thumb.height) // 2
                            sheet.paste(im_thumb, (px, py))
                except Exception:
                    pass

                # Draw border & caption
                draw.rectangle([x, y, x + thumb_w, y + thumb_h], outline=(60, 60, 60), width=1)
                caption = f"{rec.get('source_scene', '')} [{rec.get('role', '')}]"
                draw.text((x + 4, y + thumb_h + 8), caption, fill=(180, 180, 180))

            sheet_dst = self.contact_sheets_dir / f"{proj_id}.jpg"
            sheet.save(sheet_dst, "JPEG", quality=80)

    def write_markdown_catalog(self, records: List[Dict[str, Any]]) -> None:
        """Write human- and agent-readable summary markdown catalog."""
        lines: List[str] = [
            "# AutoClip Reusable Asset Catalog",
            "",
            f"Updated: `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}`  ",
            f"Total Unique Assets: **{len(records)}**",
            "",
            "This catalog indexes reusable production assets stored in `assets/reusable-library/originals/`.",
            "Always inspect and copy from `library_path` instead of referencing ephemeral clip directories.",
            "",
            "## Summary by Role",
            "",
        ]

        # Group by role
        by_role: Dict[str, List[Dict[str, Any]]] = {}
        for r in records:
            by_role.setdefault(r.get("role", "content"), []).append(r)

        for role, items in sorted(by_role.items()):
            lines.append(f"- **{role.capitalize()}**: {len(items)} assets")
        lines.append("")

        # Table by project
        lines.extend([
            "## Assets by Project",
            "",
            "| Project | Scene | Role | Reuse | Ratio | Dimensions | Topic / Prompt | Library Path |",
            "|---|---|---|---|---|---|---|---|",
        ])

        # Sort by project then scene
        sorted_records = sorted(records, key=lambda r: (r.get("source_project", ""), r.get("scene_number", "")))
        for r in sorted_records:
            desc = (r.get("visual_prompt") or r.get("narration") or r.get("topic") or r.get("description") or "").replace("|", "-")
            if len(desc) > 60:
                desc = desc[:57] + "..."
            lines.append(
                f"| `{r['source_project']}` | `{r['source_scene']}` | `{r['role']}` | `{r['reuse']}` | "
                f"`{r['aspect_ratio']}` | `{r['width']}x{r['height']}` | {desc} | [`{r['asset_id'][:8]}`]({r['library_path']}) |"
            )

        lines.append("")
        self.index_md_path.write_text("\n".join(lines), encoding="utf-8")

    def run(self, incremental: bool = True, rebuild: bool = False) -> Dict[str, Any]:
        """Execute catalog build and synchronization."""
        self.ensure_directories()
        state = {"files": {}, "last_updated": ""} if rebuild else self.load_state()

        scanned_files = self.scan_asset_files()
        print(f"Found {len(scanned_files)} candidate asset files across assets/.")

        # Deduplication map: asset_id -> record
        existing_records: Dict[str, Dict[str, Any]] = {}

        # If incremental and index exists, pre-load existing records
        if not rebuild and self.index_jsonl_path.is_file():
            try:
                with open(self.index_jsonl_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            rec = json.loads(line)
                            existing_records[rec["asset_id"]] = rec
            except Exception:
                pass

        processed_count = 0
        copied_count = 0
        skipped_count = 0

        # Group records by project for contact sheets
        records_by_project: Dict[str, List[Dict[str, Any]]] = {}

        for file_path in scanned_files:
            rel_str = str(file_path.relative_to(self.repo_root))
            file_stat = file_path.stat()
            mtime = file_stat.st_mtime
            size = file_stat.st_size

            cached = state["files"].get(rel_str)
            if cached and cached.get("mtime") == mtime and cached.get("size") == size and not rebuild:
                sha256_hash = cached["sha256"]
                skipped_count += 1
            else:
                sha256_hash = compute_sha256(file_path)
                state["files"][rel_str] = {
                    "mtime": mtime,
                    "size": size,
                    "sha256": sha256_hash,
                }
                processed_count += 1

            # Ensure file is cloned/copied to reusable library originals/
            file_ext = file_path.suffix.lower()
            orig_dest = self.originals_dir / f"{sha256_hash}{file_ext}"
            if not orig_dest.exists():
                copy_file_apfs_clone(file_path, orig_dest)
                copied_count += 1

            # Ensure thumbnail exists
            thumb_dest = self.thumbnails_dir / f"{sha256_hash}.jpg"
            if not thumb_dest.exists():
                generate_thumbnail(orig_dest, thumb_dest)

            # Build or update deduplicated record
            if sha256_hash in existing_records:
                rec = existing_records[sha256_hash]
                if rel_str not in rec["original_sources"]:
                    rec["original_sources"].append(rel_str)
            else:
                rec = self.build_asset_record(file_path, sha256_hash)
                existing_records[sha256_hash] = rec

            proj_id = rec.get("source_project", "misc")
            records_by_project.setdefault(proj_id, []).append(rec)

        # Write deduplicated JSONL
        records_list = sorted(existing_records.values(), key=lambda r: r["asset_id"])
        temp_jsonl = self.index_jsonl_path.with_suffix(".tmp")
        with open(temp_jsonl, "w", encoding="utf-8") as f:
            for rec in records_list:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        temp_jsonl.replace(self.index_jsonl_path)

        # Generate contact sheets and markdown
        self.generate_contact_sheets(records_by_project)
        self.write_markdown_catalog(records_list)

        # Save state
        self.save_state(state)

        result_summary = {
            "total_scanned": len(scanned_files),
            "unique_assets": len(records_list),
            "processed_count": processed_count,
            "copied_count": copied_count,
            "skipped_count": skipped_count,
            "library_dir": str(self.library_dir),
            "index_jsonl": str(self.index_jsonl_path),
            "index_md": str(self.index_md_path),
        }

        print(
            f"Catalog synchronization complete!\n"
            f"  Unique assets indexed: {result_summary['unique_assets']}\n"
            f"  New/Updated files processed: {result_summary['processed_count']}\n"
            f"  New copies into library: {result_summary['copied_count']}\n"
            f"  Unchanged files skipped: {result_summary['skipped_count']}\n"
            f"  JSONL index: {self.index_jsonl_path}\n"
            f"  Markdown index: {self.index_md_path}"
        )
        return result_summary


def main():
    parser = argparse.ArgumentParser(description="Build AutoClip Reusable Asset Catalog")
    parser.add_argument("--incremental", action="store_true", default=True, help="Incremental update (default)")
    parser.add_argument("--rebuild", action="store_true", help="Force complete rebuild of the catalog")
    parser.add_argument("--repo-root", type=str, default=None, help="Explicit repository root directory")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parent.parent
    builder = AssetCatalogBuilder(repo_root)
    builder.run(incremental=args.incremental, rebuild=args.rebuild)


if __name__ == "__main__":
    main()
