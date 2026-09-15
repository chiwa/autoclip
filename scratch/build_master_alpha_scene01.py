import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
from scipy.ndimage import uniform_filter, binary_dilation, median_filter

TARGET_W = 1080
TARGET_H = 1920

# -------------------------------------------------------------
# 1. Base Canvas: Deep Sapphire Navy Cosmos with Rich Nebula & Stars
# -------------------------------------------------------------
print("Generating pristine cosmic background...")
# Vertical gradient from deep midnight navy to rich celestial sapphire
y_coords = np.linspace(0, 1, TARGET_H)[:, None]
top_color = np.array([2, 5, 14], dtype=np.float32)      # Deep cosmic navy
mid_color = np.array([6, 16, 36], dtype=np.float32)     # Rich sapphire
bot_color = np.array([3, 7, 16], dtype=np.float32)      # Horizon deep navy

# Create smooth gradient
grad = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
for y in range(TARGET_H):
    norm_y = y / float(TARGET_H)
    if norm_y < 0.6:
        t = norm_y / 0.6
        grad[y, :] = top_color * (1.0 - t) + mid_color * t
    else:
        t = (norm_y - 0.6) / 0.4
        grad[y, :] = mid_color * (1.0 - t) + bot_color * t

canvas = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8)).convert("RGBA")

# Add soft, vibrant cosmic nebula clouds (deep violet, sapphire, cyan dust)
nebula = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
n_draw = ImageDraw.Draw(nebula)

# Violet & ultramarine dust swirls around the star region
for r in range(450, 50, -10):
    alpha = int(22 * (1.0 - r / 450.0))
    n_draw.ellipse([540 - r*1.3, 620 - r*0.9, 540 + r*1.3, 620 + r*0.9], fill=(28, 16, 56, alpha))

for r in range(350, 30, -8):
    alpha = int(28 * (1.0 - r / 350.0))
    n_draw.ellipse([500 - r*1.1, 600 - r*0.8, 500 + r*1.1, 600 + r*0.8], fill=(12, 35, 75, alpha))

for r in range(250, 20, -6):
    alpha = int(32 * (1.0 - r / 250.0))
    n_draw.ellipse([580 - r*0.9, 640 - r*0.7, 580 + r*0.9, 640 + r*0.7], fill=(15, 55, 95, alpha))

nebula = nebula.filter(ImageFilter.GaussianBlur(35))
canvas = Image.alpha_composite(canvas, nebula)

# Add razor-sharp, multi-colored pin-point stars and micro-clusters
s_draw = ImageDraw.Draw(canvas)
np.random.seed(424) # 4.24 light-years
for _ in range(550):
    sx = np.random.randint(0, TARGET_W)
    sy = np.random.randint(0, 1250)
    b = np.random.randint(80, 255)
    roll = np.random.rand()
    if roll < 0.45:
        tint = (b, int(b * 0.94), int(b * 0.86), 255) # warm stellar
    elif roll < 0.80:
        tint = (int(b * 0.88), int(b * 0.95), b, 255) # icy sapphire/cyan
    else:
        tint = (b, b, b, 255) # pure white
    s_draw.point((sx, sy), fill=tint)
    # Give a few brighter stars clean 4-point diffraction
    if b > 230 and sy < 1100:
        s_draw.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        s_draw.line([(sx, sy-1), (sx, sy+1)], fill=tint)

print("Cosmic background generated.")

# -------------------------------------------------------------
# 2. Hero Subject: Authentic ESO Alpha Centauri A & B (Twin Suns)
# -------------------------------------------------------------
print("Processing authentic Alpha Centauri A & B...")
eso_raw = Image.open("assets/alpha_centauri_reel/raw/alpha_centauri_ab.png").convert("RGBA")
# ESO image size is 1248x1216. The twin stars are roughly centered horizontally, y=528..719
# Let's extract the bright stars and their gorgeous authentic diffraction spikes:
# Alpha Centauri A is the brighter left/center one, B is to its right
# Crop around the star pair: x: 100..1150, y: 380..860
eso_crop = eso_raw.crop((80, 320, 1170, 920))
# Let's check its size
print("ESO crop size:", eso_crop.size)

# The background of ESO image is dark navy with astronomical noise.
# We blend ESO stars seamlessly onto our pristine canvas using Screen / Lighten mode
# or an alpha mask based on luminance so dark noise is completely removed!
eso_arr = np.array(eso_crop).astype(np.float32)
# Calculate luminance
lum = 0.299 * eso_arr[:, :, 0] + 0.587 * eso_arr[:, :, 1] + 0.114 * eso_arr[:, :, 2]
# Threshold dark noise below 22, smooth curve above
eso_alpha = np.clip((lum - 18.0) / (200.0 - 18.0), 0, 1) ** 1.3 * 255.0
# Add soft feathering
eso_mask = Image.fromarray(eso_alpha.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))

# Boost color vibrance of the twin suns: glorious golden warm & solar amber
eso_enh = ImageEnhance.Color(eso_crop.convert("RGB")).enhance(1.45)
eso_enh = ImageEnhance.Contrast(eso_enh).enhance(1.20)
eso_clean = eso_enh.convert("RGBA")
eso_clean.putalpha(eso_mask)

# Resize to majestic scale across the upper-mid sky: width 920
eso_w = 920
eso_h = int(eso_clean.height * (eso_w / eso_clean.width))
eso_scaled = eso_clean.resize((eso_w, eso_h), Image.Resampling.LANCZOS)

# Position twin stars at cx=540, cy=610
star_x = (TARGET_W - eso_w) // 2
star_y = 610 - eso_h // 2

# Add glowing golden stellar corona behind the twin suns
corona = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(corona)
# Center of Star A (approx x=460, y=610) and Star B (approx x=620, y=610)
for r in range(260, 20, -5):
    alpha = int(45 * (1.0 - r / 260.0))
    c_draw.ellipse([460 - r*1.2, 610 - r*1.2, 460 + r*1.2, 610 + r*1.2], fill=(255, 190, 80, alpha))
    c_draw.ellipse([620 - r*1.0, 610 - r*1.0, 620 + r*1.0, 610 + r*1.0], fill=(255, 160, 60, alpha))

corona = corona.filter(ImageFilter.GaussianBlur(25))
canvas = Image.alpha_composite(canvas, corona)

# Paste authentic ESO twin stars
canvas.paste(eso_scaled, (star_x, star_y), eso_scaled)

# Add Proxima Centauri (Red dwarf star, 4.24 LY) in the upper-right
# At (880, 520) - small, intense crimson-ruby glowing red dwarf
proxima_layer = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
p_draw = ImageDraw.Draw(proxima_layer)
px, py = 880, 530
for r in range(60, 3, -3):
    alpha = int(80 * (1.0 - r / 60.0))
    p_draw.ellipse([px - r, py - r, px + r, py + r], fill=(255, 70, 40, alpha))
# Bright core
p_draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 220, 200, 255))
p_draw.line([(px - 16, py), (px + 16, py)], fill=(255, 120, 80, 210), width=2)
p_draw.line([(px, py - 16), (px, py + 16)], fill=(255, 120, 80, 210), width=2)

proxima_layer = proxima_layer.filter(ImageFilter.GaussianBlur(2))
canvas = Image.alpha_composite(canvas, proxima_layer)

print("Alpha Centauri triple star system placed.")

# -------------------------------------------------------------
# 3. Authentic Mountain Summit with Explorer Duo ("นั่งบนเขา")
# -------------------------------------------------------------
print("Processing authentic Mamase explorer duo foreground...")
end_img = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGB")
arr = np.array(end_img).astype(np.float32)

# Inpainting the text region seamlessly (rows 800..1160, cols 560..935)
sub = arr[790:1170, 550:938].copy()
local_mean = uniform_filter(sub, size=(15, 15, 1))
diff = sub - local_mean
mask = (diff[:, :, 0] > 7) & (diff[:, :, 1] > 7) & (diff[:, :, 2] > 7) & (sub[:, :, 0] > 60)
mask_dil = binary_dilation(mask, iterations=5)
sub_med = median_filter(sub, size=(21, 21, 1))
sub[mask_dil] = sub_med[mask_dil]

sub_mask = Image.new("L", (sub.shape[1], sub.shape[0]), 255)
sub_mask = sub_mask.filter(ImageFilter.GaussianBlur(12))
sm_arr = np.array(sub_mask)[:, :, np.newaxis] / 255.0
arr[790:1170, 550:938] = arr[790:1170, 550:938] * (1.0 - sm_arr) + sub * sm_arr

clean_end = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")

# Scale to width 1080
scale = TARGET_W / clean_end.width
new_h = int(clean_end.height * scale)
scaled_clean = clean_end.resize((TARGET_W, new_h), Image.Resampling.LANCZOS)

# Crop lower 880px (summit, characters, clouds, city lights)
FG_H = 880
fg_crop = scaled_clean.crop((0, new_h - FG_H, TARGET_W, new_h))

# Warm golden rim lighting on explorer and dog matching Alpha Centauri's light!
fg_enh = ImageEnhance.Color(fg_crop.convert("RGB")).enhance(1.18)
fg_enh = ImageEnhance.Contrast(fg_enh).enhance(1.08)
fg_crop = fg_enh.convert("RGBA")

# Soft top gradient fade: from y=0 to y=200 for seamless blending into deep sapphire cosmos
fg_w, fg_h = fg_crop.size
fg_mask = Image.new("L", (fg_w, fg_h), 255)
fm_draw = ImageDraw.Draw(fg_mask)
for y in range(210):
    val = int(255 * (y / 210.0)**1.6)
    fm_draw.line([(0, y), (fg_w, y)], fill=val)

# Composite mountain foreground onto canvas at y = TARGET_H - FG_H
canvas.paste(fg_crop, (0, TARGET_H - FG_H), fg_mask)

# Save the pristine raw base artwork (textless, logoless)
raw_base_path = "assets/alpha_centauri_reel/raw/scene-01-hook-raw.png"
os.makedirs("assets/alpha_centauri_reel/raw", exist_ok=True)
canvas.convert("RGB").save(raw_base_path, quality=98)
print(f"Saved raw artwork: {raw_base_path}")
