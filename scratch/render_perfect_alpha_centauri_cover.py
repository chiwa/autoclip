import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
from scipy.ndimage import uniform_filter, binary_dilation, median_filter

TARGET_W = 1080
TARGET_H = 1920

print("=== Starting Master Cover Production for Alpha Centauri ===")

# -------------------------------------------------------------
# 1. Base Canvas: Ultra-rich, noise-free celestial sapphire cosmos
# -------------------------------------------------------------
# Premium vertical gradient: Midnight abyss -> Royal Sapphire -> Deep horizon
top_color = np.array([2, 5, 16], dtype=np.float32)       # Midnight space
mid_color = np.array([8, 22, 52], dtype=np.float32)      # Vibrant celestial sapphire
bot_color = np.array([4, 10, 24], dtype=np.float32)     # Deep horizon navy

grad = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
for y in range(TARGET_H):
    norm_y = y / float(TARGET_H)
    if norm_y < 0.62:
        t = norm_y / 0.62
        grad[y, :] = top_color * (1.0 - t) + mid_color * t
    else:
        t = (norm_y - 0.62) / 0.38
        grad[y, :] = mid_color * (1.0 - t) + bot_color * t

canvas = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8)).convert("RGBA")

# Vibrant cosmic dust & nebula swirls (Sapphire, Violet, Cyan)
nebula = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
n_draw = ImageDraw.Draw(nebula)

# Cosmic violet & indigo clouds
for r in range(520, 40, -12):
    alpha = int(26 * (1.0 - r / 520.0))
    n_draw.ellipse([540 - r*1.3, 860 - r*0.8, 540 + r*1.3, 860 + r*0.8], fill=(35, 18, 68, alpha))

# Royal sapphire dust
for r in range(400, 30, -10):
    alpha = int(35 * (1.0 - r / 400.0))
    n_draw.ellipse([490 - r*1.1, 850 - r*0.7, 490 + r*1.1, 850 + r*0.7], fill=(14, 46, 105, alpha))

# Cyan/electric blue interstellar dust
for r in range(260, 20, -8):
    alpha = int(38 * (1.0 - r / 260.0))
    n_draw.ellipse([610 - r*0.9, 870 - r*0.6, 610 + r*0.9, 870 + r*0.6], fill=(16, 75, 135, alpha))

nebula = nebula.filter(ImageFilter.GaussianBlur(40))
canvas = Image.alpha_composite(canvas, nebula)

# Crystal-clear, razor-sharp pin-point stars (multi-spectral tints)
s_draw = ImageDraw.Draw(canvas)
np.random.seed(424) # 4.24 ly
for _ in range(650):
    sx = np.random.randint(0, TARGET_W)
    sy = np.random.randint(0, 1320)
    b = np.random.randint(80, 255)
    roll = np.random.rand()
    if roll < 0.40:
        tint = (b, int(b * 0.95), int(b * 0.88), 255) # warm golden star
    elif roll < 0.80:
        tint = (int(b * 0.88), int(b * 0.96), b, 255) # icy cyan-blue star
    else:
        tint = (b, b, b, 255) # pure diamond white
    s_draw.point((sx, sy), fill=tint)
    # Major bright stars with delicate cross diffraction
    if b > 232 and sy < 1150:
        s_draw.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        s_draw.line([(sx, sy-1), (sx, sy+1)], fill=tint)

print("Cosmic background generated.")

# -------------------------------------------------------------
# 2. Hero Subject: Authentic ESO Alpha Centauri A & B + Proxima
# -------------------------------------------------------------
print("Compositing authentic ESO Alpha Centauri A & B...")
eso_raw = Image.open("assets/alpha_centauri_reel/raw/alpha_centauri_ab.png").convert("RGBA")
# Crop around twin stars
eso_crop = eso_raw.crop((80, 320, 1170, 920))
eso_arr = np.array(eso_crop).astype(np.float32)

# Luminance extraction for noise-free starlight transparency
lum = 0.299 * eso_arr[:, :, 0] + 0.587 * eso_arr[:, :, 1] + 0.114 * eso_arr[:, :, 2]
eso_alpha = np.clip((lum - 15.0) / (175.0 - 15.0), 0, 1) ** 1.22 * 255.0
eso_mask = Image.fromarray(eso_alpha.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))

# Vibrant golden solar enhancement
eso_enh = ImageEnhance.Color(eso_crop.convert("RGB")).enhance(1.55)
eso_enh = ImageEnhance.Contrast(eso_enh).enhance(1.28)
eso_clean = eso_enh.convert("RGBA")
eso_clean.putalpha(eso_mask)

# Scale across mid-sky (width 920)
eso_w = 920
eso_h = int(eso_clean.height * (eso_w / eso_clean.width))
eso_scaled = eso_clean.resize((eso_w, eso_h), Image.Resampling.LANCZOS)

star_x = (TARGET_W - eso_w) // 2
star_y = 865 - eso_h // 2

# Incandescent Golden Corona behind the twin suns
corona = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(corona)
# Center of Star A (~465, 865) and Star B (~625, 865)
for r in range(270, 15, -5):
    alpha = int(52 * (1.0 - r / 270.0))
    c_draw.ellipse([465 - r*1.2, 865 - r*1.2, 465 + r*1.2, 865 + r*1.2], fill=(255, 200, 85, alpha))
    c_draw.ellipse([625 - r*1.0, 865 - r*1.0, 625 + r*1.0, 865 + r*1.0], fill=(255, 170, 65, alpha))

corona = corona.filter(ImageFilter.GaussianBlur(24))
canvas = Image.alpha_composite(canvas, corona)
canvas.paste(eso_scaled, (star_x, star_y), eso_scaled)

# Proxima Centauri (Red dwarf star at 4.24 LY) in upper-right sky at (910, 760)
proxima_layer = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
p_draw = ImageDraw.Draw(proxima_layer)
px, py = 910, 760
for r in range(60, 3, -3):
    alpha = int(90 * (1.0 - r / 60.0))
    p_draw.ellipse([px - r, py - r, px + r, py + r], fill=(255, 70, 35, alpha))
p_draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 235, 215, 255))
p_draw.line([(px - 16, py), (px + 16, py)], fill=(255, 125, 85, 220), width=2)
p_draw.line([(px, py - 16), (px, py + 16)], fill=(255, 125, 85, 220), width=2)

proxima_layer = proxima_layer.filter(ImageFilter.GaussianBlur(1.8))
canvas = Image.alpha_composite(canvas, proxima_layer)

print("Alpha Centauri triple star system placed.")

# -------------------------------------------------------------
# 3. Authentic Mountain Summit with Explorer Duo Foreground
# -------------------------------------------------------------
print("Compositing authentic Mamase explorer duo...")
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

# Boost color vibrance and cinematic depth
fg_enh = ImageEnhance.Color(fg_crop.convert("RGB")).enhance(1.22)
fg_enh = ImageEnhance.Contrast(fg_enh).enhance(1.12)
fg_crop = fg_enh.convert("RGBA")

# Atmospheric light wrap: subtle golden starlight illumination on the summit ridge
wrap_layer = Image.new("RGBA", (TARGET_W, FG_H), (0, 0, 0, 0))
w_draw = ImageDraw.Draw(wrap_layer)
for y in range(80, 240):
    a = int(35 * ((240 - y) / 160.0) ** 1.4)
    w_draw.line([(0, y), (TARGET_W, y)], fill=(255, 200, 110, a))
wrap_layer = wrap_layer.filter(ImageFilter.GaussianBlur(15))
fg_crop = Image.alpha_composite(fg_crop, wrap_layer)

fg_w, fg_h = fg_crop.size
fg_mask = Image.new("L", (fg_w, fg_h), 255)
fm_draw = ImageDraw.Draw(fg_mask)
for y in range(220):
    val = int(255 * (y / 220.0)**1.6)
    fm_draw.line([(0, y), (fg_w, y)], fill=val)

canvas.paste(fg_crop, (0, TARGET_H - FG_H), fg_mask)

# Save the raw base artwork (textless, logoless)
raw_base_path = "assets/alpha_centauri_reel/raw/scene-01-hook-raw.png"
canvas.convert("RGB").save(raw_base_path, quality=98)
print(f"Saved pristine raw base: {raw_base_path}")

# -------------------------------------------------------------
# 4. Deterministic Branding & Editorial Typography Composite
# -------------------------------------------------------------
print("Compositing deterministic branding and typography...")

# Top shade for text legibility (ISS benchmark style)
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
font_c_title = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 20)
font_c_sub = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 14)

draw = ImageDraw.Draw(canvas)

# Kicker: STORIES FROM THE UNIVERSE
draw.text((744, 190), "STORIES FROM\nTHE UNIVERSE", font=font_kicker, fill="#F4F7FB", spacing=4, align="right")
draw.line((886, 270, 1018, 270), fill="#F4F7FB", width=3)

def shadow_text(draw_obj, xy, text, font, fill):
    x, y = xy
    draw_obj.text((x + 4, y + 6), text, font=font, fill=(0, 0, 0, 210), stroke_width=5, stroke_fill=(0, 0, 0, 150))
    draw_obj.text((x, y), text, font=font, fill=fill, stroke_width=1, stroke_fill=(255, 255, 255, 40))

# Topic Title: ALPHA / CENTAURI (stacked, massive, iconic)
shadow_text(draw, (54, 172), "ALPHA", font_black, "#F6F7F4")
shadow_text(draw, (54, 332), "CENTAURI", font_black, "#F6F7F4")

# Thai Hook Lines
shadow_text(draw, (58, 508), "ดาวที่ใกล้โลกที่สุด...", font_bold, "#F6F7F4")
shadow_text(draw, (58, 595), "ต้องเดินทางกี่หมื่นปี?", font_bold, "#78D7FF")

# Accent rule & Compact Subline (leaves right side clear for Proxima)
draw.line((60, 705, 186, 705), fill="#78D7FF", width=5)
draw.text((58, 725), "4.24 LIGHT-YEARS & THE 73,000-YEAR VOYAGE", font=font_prompt_sub, fill="#F4F7FB")

# Functional Technical Callouts with generous breathing room
# 1. Callout to Alpha Centauri A & B (Twin Suns)
# Line leads down-left to empty space above summit: from (440, 930) -> (330, 990) -> (150, 990)
draw.line([(440, 930), (330, 990), (150, 990)], fill=(120, 215, 255, 220), width=2)
draw.ellipse([(440 - 4, 930 - 4), (440 + 4, 930 + 4)], fill=(255, 255, 255, 255))
draw.text((150, 948), "Alpha Centauri A & B", font=font_c_title, fill="#FFFFFF")
draw.text((150, 970), "TWIN BINARY SUNS (4.37 LY)", font=font_c_sub, fill="#78D7FF")

# 2. Callout to Proxima Centauri
# Line leads to upper-right: from (910, 760) -> (960, 720) -> (1040, 720)
draw.line([(910, 760), (960, 720), (1040, 720)], fill=(255, 120, 90, 220), width=2)
draw.ellipse([(910 - 4, 760 - 4), (910 + 4, 760 + 4)], fill=(255, 255, 255, 255))
draw.text((750, 676), "Proxima Centauri", font=font_c_title, fill="#FFFFFF")
draw.text((750, 698), "CLOSEST RED DWARF (4.24 LY)", font=font_c_sub, fill="#FF8866")

# Documentary Footer Bar
draw.text((55, 1840), "SCIENCE  |  SPACE  |  DISCOVERY  |  A BRIGHTER TOMORROW", font=font_footer, fill="#F4F7FB")

# Save final 9:16 vertical cover
final_path = "assets/alpha_centauri_reel/images/scene-01-hook.png"
os.makedirs("assets/alpha_centauri_reel/images", exist_ok=True)
canvas.convert("RGB").save(final_path, quality=98)
print(f"Successfully saved Master Cover: {final_path}")

# Save to brain artifacts directory for direct user inspection
brain_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/alpha_centauri_scene_01_hook.png"
canvas.convert("RGB").save(brain_path, quality=98)
print(f"Saved artifact to: {brain_path}")

print("=== Finished Alpha Centauri Master Cover Successfully ===")
