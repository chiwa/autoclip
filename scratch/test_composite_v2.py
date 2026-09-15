import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
from scipy.ndimage import uniform_filter, binary_dilation, median_filter

TARGET_W = 1080
TARGET_H = 1920

# -------------------------------------------------------------
# 1. Base Canvas: Deep Sapphire Navy Cosmos with Rich Nebula & Stars
# -------------------------------------------------------------
print("1. Generating pristine cosmic background...")
top_color = np.array([2, 5, 14], dtype=np.float32)      # Deep cosmic navy
mid_color = np.array([7, 18, 42], dtype=np.float32)     # Rich vibrant sapphire
bot_color = np.array([4, 8, 18], dtype=np.float32)      # Horizon deep navy

grad = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
for y in range(TARGET_H):
    norm_y = y / float(TARGET_H)
    if norm_y < 0.65:
        t = norm_y / 0.65
        grad[y, :] = top_color * (1.0 - t) + mid_color * t
    else:
        t = (norm_y - 0.65) / 0.35
        grad[y, :] = mid_color * (1.0 - t) + bot_color * t

canvas = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8)).convert("RGBA")

# Cosmic nebula dust (sapphire, violet, cyan) centered around the stars at y=850
nebula = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
n_draw = ImageDraw.Draw(nebula)

for r in range(480, 50, -12):
    alpha = int(24 * (1.0 - r / 480.0))
    n_draw.ellipse([540 - r*1.3, 850 - r*0.8, 540 + r*1.3, 850 + r*0.8], fill=(26, 15, 55, alpha))

for r in range(360, 30, -10):
    alpha = int(32 * (1.0 - r / 360.0))
    n_draw.ellipse([480 - r*1.1, 840 - r*0.7, 480 + r*1.1, 840 + r*0.7], fill=(12, 38, 85, alpha))

for r in range(240, 20, -8):
    alpha = int(35 * (1.0 - r / 240.0))
    n_draw.ellipse([600 - r*0.9, 860 - r*0.6, 600 + r*0.9, 860 + r*0.6], fill=(15, 60, 110, alpha))

nebula = nebula.filter(ImageFilter.GaussianBlur(38))
canvas = Image.alpha_composite(canvas, nebula)

# Procedural pin-point stars (crisp, zero sensor noise)
s_draw = ImageDraw.Draw(canvas)
np.random.seed(424)
for _ in range(600):
    sx = np.random.randint(0, TARGET_W)
    sy = np.random.randint(0, 1300)
    b = np.random.randint(75, 255)
    roll = np.random.rand()
    if roll < 0.45:
        tint = (b, int(b * 0.94), int(b * 0.86), 255)
    elif roll < 0.80:
        tint = (int(b * 0.88), int(b * 0.95), b, 255)
    else:
        tint = (b, b, b, 255)
    s_draw.point((sx, sy), fill=tint)
    if b > 230 and sy < 1100:
        s_draw.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        s_draw.line([(sx, sy-1), (sx, sy+1)], fill=tint)

# -------------------------------------------------------------
# 2. Hero Subject: Alpha Centauri A & B (ESO authentic binary)
# -------------------------------------------------------------
print("2. Compositing Alpha Centauri A & B...")
eso_raw = Image.open("assets/alpha_centauri_reel/raw/alpha_centauri_ab.png").convert("RGBA")
# Crop around twin stars
eso_crop = eso_raw.crop((80, 320, 1170, 920))
eso_arr = np.array(eso_crop).astype(np.float32)
lum = 0.299 * eso_arr[:, :, 0] + 0.587 * eso_arr[:, :, 1] + 0.114 * eso_arr[:, :, 2]
eso_alpha = np.clip((lum - 16.0) / (180.0 - 16.0), 0, 1) ** 1.25 * 255.0
eso_mask = Image.fromarray(eso_alpha.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))

eso_enh = ImageEnhance.Color(eso_crop.convert("RGB")).enhance(1.50)
eso_enh = ImageEnhance.Contrast(eso_enh).enhance(1.25)
eso_clean = eso_enh.convert("RGBA")
eso_clean.putalpha(eso_mask)

# Scale across the mid-sky: width 900
eso_w = 900
eso_h = int(eso_clean.height * (eso_w / eso_clean.width))
eso_scaled = eso_clean.resize((eso_w, eso_h), Image.Resampling.LANCZOS)

star_x = (TARGET_W - eso_w) // 2
star_y = 860 - eso_h // 2

# Golden/amber incandescent corona behind twin suns
corona = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(corona)
# Center of Star A (approx x=460, y=860) and Star B (approx x=620, y=860)
for r in range(260, 20, -5):
    alpha = int(48 * (1.0 - r / 260.0))
    c_draw.ellipse([460 - r*1.2, 860 - r*1.2, 460 + r*1.2, 860 + r*1.2], fill=(255, 195, 80, alpha))
    c_draw.ellipse([620 - r*1.0, 860 - r*1.0, 620 + r*1.0, 860 + r*1.0], fill=(255, 165, 60, alpha))

corona = corona.filter(ImageFilter.GaussianBlur(25))
canvas = Image.alpha_composite(canvas, corona)
canvas.paste(eso_scaled, (star_x, star_y), eso_scaled)

# Proxima Centauri (Red dwarf) at (890, 750)
proxima_layer = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
p_draw = ImageDraw.Draw(proxima_layer)
px, py = 890, 750
for r in range(55, 3, -3):
    alpha = int(85 * (1.0 - r / 55.0))
    p_draw.ellipse([px - r, py - r, px + r, py + r], fill=(255, 65, 35, alpha))
p_draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 230, 210, 255))
p_draw.line([(px - 14, py), (px + 14, py)], fill=(255, 120, 80, 210), width=2)
p_draw.line([(px, py - 14), (px, py + 14)], fill=(255, 120, 80, 210), width=2)

proxima_layer = proxima_layer.filter(ImageFilter.GaussianBlur(2))
canvas = Image.alpha_composite(canvas, proxima_layer)

# -------------------------------------------------------------
# 3. Mountain Summit with Explorer Duo Foreground
# -------------------------------------------------------------
print("3. Compositing Mamase explorer duo...")
end_img = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGB")
arr = np.array(end_img).astype(np.float32)

sub = arr[790:1170, 550:938].copy()
local_mean = uniform_filter(sub, size=(15, 15, 1))
diff = sub - local_mean
mask = (diff[:, :, 0] > 7) & (diff[:, :, 1] > 7) & (diff[:, :, 2] > 7) & (sub[:, :, 0] > 60)
mask_dil = binary_dilation(mask, iterations=5)
sub_med = median_filter(sub, size=(21, 21, 1))
sub[mask_dil] = sub_med[mask_dil]

sub_mask = Image.new("L", (sub.shape[1], sub.shape[0]), 255).filter(ImageFilter.GaussianBlur(12))
sm_arr = np.array(sub_mask)[:, :, np.newaxis] / 255.0
arr[790:1170, 550:938] = arr[790:1170, 550:938] * (1.0 - sm_arr) + sub * sm_arr

clean_end = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
scale = TARGET_W / clean_end.width
new_h = int(clean_end.height * scale)
scaled_clean = clean_end.resize((TARGET_W, new_h), Image.Resampling.LANCZOS)

FG_H = 880
fg_crop = scaled_clean.crop((0, new_h - FG_H, TARGET_W, new_h))
fg_enh = ImageEnhance.Color(fg_crop.convert("RGB")).enhance(1.20)
fg_enh = ImageEnhance.Contrast(fg_enh).enhance(1.10)
fg_crop = fg_enh.convert("RGBA")

fg_w, fg_h = fg_crop.size
fg_mask = Image.new("L", (fg_w, fg_h), 255)
fm_draw = ImageDraw.Draw(fg_mask)
for y in range(210):
    val = int(255 * (y / 210.0)**1.6)
    fm_draw.line([(0, y), (fg_w, y)], fill=val)

canvas.paste(fg_crop, (0, TARGET_H - FG_H), fg_mask)

# -------------------------------------------------------------
# 4. Deterministic Branding & Typography Composite
# -------------------------------------------------------------
print("4. Compositing deterministic typography & branding...")
# Top shade overlay for typography legibility
shade = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shade)
sd.rectangle((0, 0, TARGET_W, 760), fill=(2, 9, 22, 95))
canvas = Image.alpha_composite(canvas, shade)

# Authentic Branding Assets
header_path = "assets/branding/mamase/mamase_podcast_header.png"
logo_path = "assets/branding/mamase/logo.png"

def fit_inside(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    sc = min(max_width / image.width, max_height / image.height)
    return image.resize((round(image.width * sc), round(image.height * sc)), Image.Resampling.LANCZOS)

if os.path.exists(header_path):
    h_img = fit_inside(Image.open(header_path).convert("RGBA"), 400, 106)
    canvas.alpha_composite(h_img, (58, 46))

if os.path.exists(logo_path):
    l_img = fit_inside(Image.open(logo_path).convert("RGBA"), 138, 138)
    canvas.alpha_composite(l_img, (888, 38))

# Fonts
font_black = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 175)
font_bold = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 78)
font_prompt_sub = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 26)
font_kicker = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 22)
font_footer = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 20)

draw = ImageDraw.Draw(canvas)

# Kicker
draw.text((744, 190), "STORIES FROM\nTHE UNIVERSE", font=font_kicker, fill="#F4F7FB", spacing=4, align="right")
draw.line((886, 270, 1018, 270), fill="#F4F7FB", width=3)

def shadow_text(draw_obj, xy, text, font, fill):
    x, y = xy
    draw_obj.text((x + 4, y + 6), text, font=font, fill=(0, 0, 0, 200), stroke_width=5, stroke_fill=(0, 0, 0, 140))
    draw_obj.text((x, y), text, font=font, fill=fill, stroke_width=1, stroke_fill=(255, 255, 255, 40))

# Topic Title: ALPHA / CENTAURI
shadow_text(draw, (54, 172), "ALPHA", font_black, "#F6F7F4")
shadow_text(draw, (54, 332), "CENTAURI", font_black, "#F6F7F4")

# Thai Hook Lines
shadow_text(draw, (58, 508), "ดาวที่ใกล้โลกที่สุด...", font_bold, "#F6F7F4")
shadow_text(draw, (58, 595), "ต้องเดินทางกี่หมื่นปี?", font_bold, "#78D7FF")

# Accent rule & Subline
draw.line((60, 705, 186, 705), fill="#78D7FF", width=5)
draw.text((58, 725), "THE 4.24 LIGHT-YEAR VOYAGE TO OUR NEXT-DOOR NEIGHBOR", font=font_prompt_sub, fill="#F4F7FB")

# Functional Technical Callouts
# 1. Callout to Alpha Centauri A & B (Twin Suns)
font_c_title = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 20)
font_c_sub = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 14)

# Line to Star A&B: from (460, 830) -> (360, 780) -> (200, 780)
draw.line([(460, 830), (380, 785), (220, 785)], fill=(120, 215, 255, 220), width=2)
draw.ellipse([(460 - 4, 830 - 4), (460 + 4, 830 + 4)], fill=(255, 255, 255, 255))
draw.text((220, 742), "Alpha Centauri A & B", font=font_c_title, fill="#FFFFFF")
draw.text((220, 764), "TWIN BINARY SUNS (4.37 LY)", font=font_c_sub, fill="#78D7FF")

# 2. Callout to Proxima Centauri: from (890, 750) -> (930, 715) -> (1040, 715)
draw.line([(890, 750), (930, 715), (1040, 715)], fill=(255, 120, 90, 220), width=2)
draw.ellipse([(890 - 4, 750 - 4), (890 + 4, 750 + 4)], fill=(255, 255, 255, 255))
draw.text((790, 672), "Proxima Centauri", font=font_c_title, fill="#FFFFFF")
draw.text((790, 694), "CLOSEST STAR (4.24 LY)", font=font_c_sub, fill="#FF8866")

# Documentary Footer Bar
draw.text((55, 1840), "SCIENCE  |  SPACE  |  DISCOVERY  |  A BRIGHTER TOMORROW", font=font_footer, fill="#F4F7FB")

# Save final 9:16
final_output = "assets/alpha_centauri_reel/images/scene-01-hook.png"
os.makedirs("assets/alpha_centauri_reel/images", exist_ok=True)
canvas.convert("RGB").save(final_output, quality=98)
print(f"Successfully rendered master cover: {final_output}")

# Also copy to artifacts directory for user inspection
brain_artifact = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/alpha_centauri_scene_01_hook.png"
canvas.convert("RGB").save(brain_artifact, quality=98)
print(f"Saved artifact to: {brain_artifact}")
