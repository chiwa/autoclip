from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

fonts_dir = Path("assets/fonts")
W, H = 1080, 1920
TEXT_MAX_W = 968

def _wrap(draw, text, font):
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

def _fit_text(draw, text, font_path, max_size, min_size, max_lines):
    for size in range(max_size, min_size - 1, -2):
        font = ImageFont.truetype(str(font_path), size)
        lines = _wrap(draw, text, font)
        if len(lines) <= max_lines and all(
            draw.textbbox((0, 0), line, font=font)[2] <= TEXT_MAX_W for line in lines
        ):
            return font, lines
    raise ValueError(f"Text too long: {text}")

im = Image.new("RGBA", (W, H))
draw = ImageDraw.Draw(im)
title = "ALPHA CENTAURI"
hook = "ดาวที่ใกล้เราที่สุด แต่ต้องใช้เวลาเดินทางนานถึง 73,000 ปี!"

t_font, t_lines = _fit_text(draw, title, fonts_dir / "Kanit-Black.ttf", 150, 72, 2)
h_font, h_lines = _fit_text(draw, hook, fonts_dir / "Kanit-Bold.ttf", 72, 42, 3)

t_step = int(t_font.size * 1.06)
h_step = int(h_font.size * 1.18)
block_height = len(t_lines) * t_step + 24 + len(h_lines) * h_step

print(f"Title size: {t_font.size}, lines: {t_lines}")
print(f"Hook size: {h_font.size}, lines: {h_lines}")
print(f"Block height: {block_height}")

for y in (190, 520, 880, 1180):
    print(f"Candidate y={y}: span y={y}..{y+block_height}")
