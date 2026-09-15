from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets/iss_why_not_fall_reel/images/scene-01-hook-base.png"
OUTPUT = ROOT / "assets/iss_why_not_fall_reel/images/scene-01-hook.png"
HEADER = ROOT / "assets/branding/mamase/mamase_podcast_header.png"
LOGO = ROOT / "assets/branding/mamase/logo.png"
FONT_BLACK = ROOT / "assets/fonts/Kanit-Black.ttf"
FONT_BOLD = ROOT / "assets/fonts/Kanit-Bold.ttf"
FONT_PROMPT = ROOT / "assets/fonts/Prompt-Bold.ttf"


def fit_inside(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    scale = min(max_width / image.width, max_height / image.height)
    return image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)


def shadow_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.FreeTypeFont, fill: str) -> None:
    x, y = xy
    draw.text((x + 4, y + 6), text, font=font, fill=(0, 0, 0, 190), stroke_width=5, stroke_fill=(0, 0, 0, 130))
    draw.text((x, y), text, font=font, fill=fill, stroke_width=1, stroke_fill=(255, 255, 255, 50))


def main() -> None:
    canvas = Image.open(BASE).convert("RGBA")
    shade = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rectangle((0, 0, 1080, 760), fill=(2, 9, 22, 95))
    canvas = Image.alpha_composite(canvas, shade)

    header = fit_inside(Image.open(HEADER).convert("RGBA"), 400, 106)
    canvas.alpha_composite(header, (58, 46))
    logo = fit_inside(Image.open(LOGO).convert("RGBA"), 138, 138)
    canvas.alpha_composite(logo, (888, 38))

    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype(FONT_BLACK, 190)
    headline_font = ImageFont.truetype(FONT_BOLD, 83)
    detail_font = ImageFont.truetype(FONT_PROMPT, 30)
    kicker_font = ImageFont.truetype(FONT_PROMPT, 22)

    draw.text((744, 190), "STORIES FROM\nTHE UNIVERSE", font=kicker_font, fill="#F4F7FB", spacing=4, align="right")
    draw.line((886, 270, 1018, 270), fill="#F4F7FB", width=3)
    shadow_text(draw, (54, 176), "ISS", title_font, "#F6F7F4")
    shadow_text(draw, (58, 382), "กำลังตก", headline_font, "#F6F7F4")
    shadow_text(draw, (58, 474), "แต่ทำไมไม่ถึงพื้น?", headline_font, "#78D7FF")

    draw.line((60, 602, 186, 602), fill="#78D7FF", width=5)
    draw.text((58, 625), "A GIANT LABORATORY\nIN CONTINUOUS FREE FALL", font=detail_font, fill="#F4F7FB", spacing=9)
    draw.text((55, 1840), "SCIENCE  |  SPACE  |  DISCOVERY  |  A BRIGHTER TOMORROW", font=kicker_font, fill="#F4F7FB")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUTPUT, quality=96)


if __name__ == "__main__":
    main()
