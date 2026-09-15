#!/usr/bin/env python3
"""Protected-zone-aware compositor for Mamase Reel Scene 01."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
TEXT_X, TEXT_MAX_W, SUBTITLE_SAFE_TOP = 56, 968, 1680


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _intersects(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def _parse_zone(value: str) -> tuple[int, int, int, int]:
    try:
        x, y, width, height = (int(part.strip()) for part in value.split(","))
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("protected zone must be x,y,width,height") from None
    if min(x, y, width, height) < 0 or width == 0 or height == 0:
        raise argparse.ArgumentTypeError("protected zone values must be positive")
    if x + width > W or y + height > H:
        raise argparse.ArgumentTypeError("protected zone must stay inside 1080x1920")
    return x, y, x + width, y + height


def _fit_inside(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    scale = min(max_width / image.width, max_height / image.height)
    return image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS
    )


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> list[str]:
    words = text.strip().split()
    if not words:
        return []
    lines, current = [], words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if draw.textbbox((0, 0), trial, font=font)[2] <= TEXT_MAX_W:
            current = trial
        else:
            lines.append(current)
            current = word
    return [*lines, current]


def _fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: Path,
    max_size: int,
    min_size: int,
    max_lines: int,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(max_size, min_size - 1, -2):
        font = ImageFont.truetype(str(font_path), size)
        lines = _wrap(draw, text, font)
        if len(lines) <= max_lines and all(
            draw.textbbox((0, 0), line, font=font)[2] <= TEXT_MAX_W for line in lines
        ):
            return font, lines
    raise ValueError(f"Text is too long for a mobile-safe cover: {text!r}")


def _draw_shadow_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
) -> None:
    x, y = xy
    draw.text(
        (x + 3, y + 5), text, font=font, fill=(0, 0, 0, 210),
        stroke_width=5, stroke_fill=(0, 0, 0, 150),
    )
    draw.text((x, y), text, font=font, fill=fill, stroke_width=1, stroke_fill=(0, 0, 0, 100))


def create_reels_cover(
    base_image_path: str,
    output_9x16_path: str,
    title: str,
    headline_th: str,
    headline_sub_th: str = "",
    *,
    protected_subjects: dict[str, Sequence[tuple[int, int, int, int]]] | None = None,
    protected_zones: Sequence[tuple[int, int, int, int]] | None = None,
    report_path: str | None = None,
    **legacy_options: object,
) -> dict[str, object]:
    """Add one authentic logo, topic, and Thai hook without covering subjects."""
    forbidden = {key: value for key, value in legacy_options.items() if value}
    if forbidden:
        raise ValueError(
            "Legacy cover clutter is disabled; remove: " + ", ".join(sorted(forbidden))
        )
    if protected_zones and not protected_subjects:
        raise ValueError(
            "Unlabelled protected zones are no longer accepted; provide hero, celestial, and characters"
        )
    protected_subjects = protected_subjects or {}
    missing = [name for name in ("hero", "celestial", "characters") if not protected_subjects.get(name)]
    if missing:
        raise ValueError("Missing protected subject categories: " + ", ".join(missing))
    if len(protected_subjects["characters"]) < 2:
        raise ValueError("Characters protection must include separate explorer and dog zones")
    all_zones = [zone for zones in protected_subjects.values() for zone in zones]

    base_path = Path(base_image_path)
    if not base_path.is_file():
        raise FileNotFoundError(f"Base artwork not found: {base_path}")

    root = _project_root()
    header_path = root / "assets/branding/mamase/mamase_podcast_header.png"
    fonts_dir = root / "assets/fonts"
    for required in (header_path, fonts_dir / "Kanit-Black.ttf", fonts_dir / "Kanit-Bold.ttf"):
        if not required.is_file():
            raise FileNotFoundError(f"Required brand asset not found: {required}")

    canvas = Image.open(base_path).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(canvas)
    hook = " ".join(part.strip() for part in (headline_th, headline_sub_th) if part.strip())
    title_font, title_lines = _fit_text(draw, title.strip(), fonts_dir / "Kanit-Black.ttf", 150, 72, 2)
    hook_font, hook_lines = _fit_text(draw, hook, fonts_dir / "Kanit-Bold.ttf", 72, 42, 3)
    title_step, hook_step = int(title_font.size * 1.06), int(hook_font.size * 1.18)
    block_height = len(title_lines) * title_step + 24 + len(hook_lines) * hook_step

    brand = _fit_inside(Image.open(header_path).convert("RGBA"), 430, 114)
    brand_rect = (52, 42, 52 + brand.width, 42 + brand.height)
    if any(_intersects(brand_rect, zone) for zone in all_zones):
        raise ValueError("Brand overlaps a protected subject; reframe the raw artwork")

    chosen_y = None
    text_rect = (0, 0, 0, 0)
    for y in (190, 520, 880, 1180):
        candidate = (TEXT_X, y, TEXT_X + TEXT_MAX_W, y + block_height)
        if candidate[3] <= SUBTITLE_SAFE_TOP and not any(
            _intersects(candidate, zone) for zone in all_zones
        ):
            chosen_y, text_rect = y, candidate
            break
    if chosen_y is None:
        raise ValueError("No safe text region remains; recompose raw artwork instead of covering the hero")

    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shade).rounded_rectangle(
        (text_rect[0] - 20, text_rect[1] - 18, text_rect[2], text_rect[3] + 16),
        radius=24, fill=(1, 7, 17, 112),
    )
    canvas = Image.alpha_composite(canvas, shade)
    canvas.alpha_composite(brand, (52, 42))
    draw = ImageDraw.Draw(canvas)

    y = chosen_y
    for line in title_lines:
        _draw_shadow_text(draw, (TEXT_X, y), line, title_font, "#F6F7F4")
        y += title_step
    y += 24
    for index, line in enumerate(hook_lines):
        color = "#78D7FF" if index == len(hook_lines) - 1 else "#F6F7F4"
        _draw_shadow_text(draw, (TEXT_X, y), line, hook_font, color)
        y += hook_step

    output = Path(output_9x16_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, format="PNG", optimize=True)
    report: dict[str, object] = {
        "output": str(output), "dimensions": [W, H], "brand_asset_count": 1,
        "text_layers": ["topic_title", "thai_hook"], "text_rect": list(text_rect),
        "protected_subjects": {
            name: [list(zone) for zone in zones] for name, zones in protected_subjects.items()
        },
        "forbidden_layers": [],
    }
    if report_path:
        report_file = Path(report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--hook", required=True)
    parser.add_argument("--protect-hero", action="append", type=_parse_zone, required=True)
    parser.add_argument("--protect-celestial", action="append", type=_parse_zone, required=True)
    parser.add_argument(
        "--protect-character", action="append", type=_parse_zone, required=True,
        help="x,y,width,height; pass once for explorer and once for dog",
    )
    parser.add_argument("--report")
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = create_reels_cover(
        args.base, args.output, args.title, args.hook,
        protected_subjects={
            "hero": args.protect_hero,
            "celestial": args.protect_celestial,
            "characters": args.protect_character,
        },
        report_path=args.report,
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
