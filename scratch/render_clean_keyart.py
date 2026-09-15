import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont

TARGET_W = 1080
TARGET_H = 1920

print("=== Rendering Clean Cinematic Key Art for Alpha Centauri ===")

# 1. Base Gradient Canvas (Deep Royal Sapphire Cosmos)
top_color = np.array([2, 4, 12], dtype=np.float32)       # Midnight space
mid_color = np.array([7, 18, 46], dtype=np.float32)      # Deep royal sapphire
bot_color = np.array([4, 12, 30], dtype=np.float32)     # Deep space horizon

grad = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
for y in range(TARGET_H):
    norm_y = y / float(TARGET_H)
    if norm_y < 0.60:
        t = norm_y / 0.60
        grad[y, :] = top_color * (1.0 - t) + mid_color * t
    else:
        t = (norm_y - 0.60) / 0.40
        grad[y, :] = mid_color * (1.0 - t) + bot_color * t

canvas = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8)).convert("RGBA")

# Cosmic dust & Milky Way nebula swirls
nebula = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
n_draw = ImageDraw.Draw(nebula)

for r in range(540, 40, -12):
    alpha = int(24 * (1.0 - r / 540.0))
    n_draw.ellipse([540 - r*1.3, 780 - r*0.8, 540 + r*1.3, 780 + r*0.8], fill=(30, 16, 62, alpha))

for r in range(420, 30, -10):
    alpha = int(32 * (1.0 - r / 420.0))
    n_draw.ellipse([480 - r*1.1, 760 - r*0.7, 480 + r*1.1, 760 + r*0.7], fill=(14, 42, 98, alpha))

for r in range(280, 20, -8):
    alpha = int(35 * (1.0 - r / 280.0))
    n_draw.ellipse([600 - r*0.9, 790 - r*0.6, 600 + r*0.9, 790 + r*0.6], fill=(16, 70, 125, alpha))

nebula = nebula.filter(ImageFilter.GaussianBlur(38))
canvas = Image.alpha_composite(canvas, nebula)

# Multi-colored pinpoint stars
s_draw = ImageDraw.Draw(canvas)
np.random.seed(424)
for _ in range(650):
    sx = np.random.randint(0, TARGET_W)
    sy = np.random.randint(0, 1150)
    b = np.random.randint(75, 255)
    roll = np.random.rand()
    if roll < 0.40:
        tint = (b, int(b * 0.94), int(b * 0.86), 255)
    elif roll < 0.80:
        tint = (int(b * 0.88), int(b * 0.95), b, 255)
    else:
        tint = (b, b, b, 255)
    s_draw.point((sx, sy), fill=tint)
    if b > 232 and sy < 1050:
        s_draw.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        s_draw.line([(sx, sy-1), (sx, sy+1)], fill=tint)

# 2. Hero Subject: Alpha Centauri A & B (ESO Authentic Binary)
eso_raw = Image.open("assets/alpha_centauri_reel/raw/alpha_centauri_ab.png").convert("RGB")
eso_crop = eso_raw.crop((80, 320, 1170, 920))
arr = np.array(eso_crop).astype(np.float32)

h_eso, w_eso = arr.shape[:2]
Y, X = np.ogrid[:h_eso, :w_eso]
dist_left = X
dist_right = w_eso - 1 - X
dist_top = Y
dist_bottom = h_eso - 1 - Y
edge_dist = np.minimum(np.minimum(dist_left, dist_right), np.minimum(dist_top, dist_bottom)).astype(np.float32)

feather = np.clip(edge_dist / 90.0, 0, 1)
feather_mask = (1.0 - np.cos(np.pi * feather)) / 2.0
subtracted = np.clip((arr - 22.0) * (255.0 / (255.0 - 22.0)), 0, 255)

lum = 0.299 * subtracted[:, :, 0] + 0.587 * subtracted[:, :, 1] + 0.114 * subtracted[:, :, 2]
alpha = np.clip(lum / 110.0, 0, 1) ** 1.25 * feather_mask * 255.0

# Warm golden solar grading (G-type & K-type stars)
# Shift chromatic fringe towards solar gold
subtracted[:, :, 0] = np.clip(subtracted[:, :, 0] * 1.05, 0, 255) # R
subtracted[:, :, 1] = np.clip(subtracted[:, :, 1] * 0.95, 0, 255) # G
subtracted[:, :, 2] = np.clip(subtracted[:, :, 2] * 0.70, 0, 255) # Reduce blue chromatic fringing

eso_enh = ImageEnhance.Color(Image.fromarray(subtracted.astype(np.uint8))).enhance(1.40)
eso_enh = ImageEnhance.Contrast(eso_enh).enhance(1.25)
clean_stars = eso_enh.convert("RGBA")
clean_stars.putalpha(Image.fromarray(alpha.astype(np.uint8)))

eso_w = 920
eso_h = int(clean_stars.height * (eso_w / clean_stars.width))
eso_scaled = clean_stars.resize((eso_w, eso_h), Image.Resampling.LANCZOS)

star_x = (TARGET_W - eso_w) // 2
star_y = 810 - eso_h // 2

# Golden Solar Coronas
corona = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(corona)
for r in range(270, 15, -5):
    a = int(55 * (1.0 - r / 270.0))
    c_draw.ellipse([465 - r*1.2, 810 - r*1.2, 465 + r*1.2, 810 + r*1.2], fill=(255, 205, 90, a))
    c_draw.ellipse([625 - r*1.0, 810 - r*1.0, 625 + r*1.0, 810 + r*1.0], fill=(255, 175, 70, a))

corona = corona.filter(ImageFilter.GaussianBlur(25))
canvas = Image.alpha_composite(canvas, corona)
canvas.paste(eso_scaled, (star_x, star_y), eso_scaled)

# Proxima Centauri (Red dwarf star at 4.24 LY) in upper-right sky at (910, 690)
proxima_layer = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
p_draw = ImageDraw.Draw(proxima_layer)
px, py = 910, 690
for r in range(55, 3, -3):
    a = int(90 * (1.0 - r / 55.0))
    p_draw.ellipse([px - r, py - r, px + r, py + r], fill=(255, 70, 35, a))
p_draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 235, 215, 255))
p_draw.line([(px - 15, py), (px + 15, py)], fill=(255, 125, 85, 220), width=2)
p_draw.line([(px, py - 15), (px, py + 15)], fill=(255, 125, 85, 220), width=2)

proxima_layer = proxima_layer.filter(ImageFilter.GaussianBlur(1.8))
canvas = Image.alpha_composite(canvas, proxima_layer)

# 3. Benchmark Lower Foreground: Explorer + Dog on Summit + Earth Limb
fg_source = Image.open("scratch/clean_iss_fg_1070.png").convert("RGBA")
fg_w, fg_h = fg_source.size

fg_mask = Image.new("L", (fg_w, fg_h), 255)
m_draw = ImageDraw.Draw(fg_mask)
for y in range(130):
    val = int(255 * ((1.0 - np.cos(np.pi * (y / 130.0))) / 2.0))
    m_draw.line([(0, y), (fg_w, y)], fill=val)

canvas.paste(fg_source, (0, 1070), fg_mask)

# Save the pristine raw base artwork (textless, logoless)
raw_base_path = "assets/alpha_centauri_reel/raw/scene-01-hook-raw.png"
os.makedirs("assets/alpha_centauri_reel/raw", exist_ok=True)
canvas.convert("RGB").save(raw_base_path, quality=98)
print(f"Saved pristine raw base: {raw_base_path}")

# 4. Deterministic Branding & Editorial Typography Composite
shade = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shade)
sd.rectangle((0, 0, TARGET_W, 760), fill=(2, 9, 22, 95))
canvas = Image.alpha_composite(canvas, shade)

# Authentic Mamase Header (Transparent, NO black box!)
header_raw = Image.open("assets/branding/mamase/mamase_podcast_header.png").convert("RGB")
h_arr = np.array(header_raw).astype(np.float32)
lum_h = np.max(h_arr, axis=2)
alpha_h = np.clip(lum_h * 1.6, 0, 255).astype(np.uint8)
clean_header = Image.fromarray(h_arr.astype(np.uint8)).convert("RGBA")
clean_header.putalpha(Image.fromarray(alpha_h))

def fit_inside(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    sc = min(max_width / image.width, max_height / image.height)
    return image.resize((round(image.width * sc), round(image.height * sc)), Image.Resampling.LANCZOS)

header_final = fit_inside(clean_header, 400, 106)
canvas.alpha_composite(header_final, (58, 46))

# Authentic Round Logo at (888, 38)
logo_path = "assets/branding/mamase/logo.png"
if os.path.exists(logo_path):
    logo_img = fit_inside(Image.open(logo_path).convert("RGBA"), 138, 138)
    canvas.alpha_composite(logo_img, (888, 38))

# Fonts
font_black = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 185)
font_bold = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 80)
font_prompt_sub = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 26)
font_kicker = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 22)
font_footer = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 20)

draw = ImageDraw.Draw(canvas)

# Kicker: STORIES FROM THE UNIVERSE
draw.text((744, 190), "STORIES FROM\nTHE UNIVERSE", font=font_kicker, fill="#F4F7FB", spacing=4, align="right")
draw.line((886, 270, 1018, 270), fill="#F4F7FB", width=3)

def shadow_text(draw_obj, xy, text, font, fill):
    x, y = xy
    draw_obj.text((x + 4, y + 6), text, font=font, fill=(0, 0, 0, 210), stroke_width=5, stroke_fill=(0, 0, 0, 150))
    draw_obj.text((x, y), text, font=font, fill=fill, stroke_width=1, stroke_fill=(255, 255, 255, 40))

# Topic Title: ALPHA / CENTAURI (stacked, massive, iconic)
shadow_text(draw, (54, 176), "ALPHA", font_black, "#F6F7F4")
shadow_text(draw, (54, 340), "CENTAURI", font_black, "#F6F7F4")

# Thai Hook Lines
shadow_text(draw, (58, 515), "ดาวที่ใกล้โลกที่สุด...", font_bold, "#F6F7F4")
shadow_text(draw, (58, 605), "ต้องเดินทางกี่หมื่นปี?", font_bold, "#78D7FF")

# Accent rule & Subline
draw.line((60, 715, 186, 715), fill="#78D7FF", width=5)
draw.text((58, 736), "4.24 LIGHT-YEARS & THE 73,000-YEAR VOYAGE", font=font_prompt_sub, fill="#F4F7FB")

# Documentary Footer Bar
draw.text((55, 1840), "SCIENCE  |  SPACE  |  DISCOVERY  |  A BRIGHTER TOMORROW", font=font_footer, fill="#F4F7FB")

# Save final 9:16 vertical cover
final_path = "assets/alpha_centauri_reel/images/scene-01-hook.png"
os.makedirs("assets/alpha_centauri_reel/images", exist_ok=True)
canvas.convert("RGB").save(final_path, quality=98)
print(f"Successfully saved Master Cover: {final_path}")

# Copy to brain artifacts directory for direct user inspection
brain_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/alpha_centauri_scene_01_hook.png"
canvas.convert("RGB").save(brain_path, quality=98)
print(f"Saved artifact to: {brain_path}")

print("=== Clean Key Art Rendered Successfully ===")
