import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import uniform_filter, binary_dilation, median_filter
import os, sys

TARGET_W = 1080
TARGET_H = 1920

# 1. Base canvas: Deep rich space with fine stars
canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (4, 5, 10, 255))
s_draw = ImageDraw.Draw(canvas)
np.random.seed(2026)
for _ in range(450):
    sx = np.random.randint(0, TARGET_W)
    sy = np.random.randint(0, 1100)
    b = np.random.randint(70, 255)
    tint = (b, int(b * 0.93), int(b * 0.86), 255) if np.random.rand() > 0.4 else (int(b * 0.86), int(b * 0.94), b, 255)
    s_draw.point((sx, sy), fill=tint)
    if b > 235 and sy < 950:
        s_draw.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        s_draw.line([(sx, sy-1), (sx, sy+1)], fill=tint)

# 2. Authentic Hubble Jupiter Disk (Crop tightly to planet boundary)
jup_raw = Image.open("assets/jupiter_as_a_star_reel/raw/jupiter_hubble_portrait.png").convert("RGBA")
# Exact planet boundary: x: 215..1759, y: 260..1741
jup_disk_raw = jup_raw.crop((215, 260, 1759, 1741))

JUP_D = 950
jup_disk = jup_disk_raw.resize((JUP_D, JUP_D), Image.Resampling.LANCZOS)
j_cx, j_cy = 540, 560

# Stellar Corona (Warm golden-orange proto-star / ignited brown dwarf glow)
CORONA_SZ = 1450
corona = Image.new("RGBA", (CORONA_SZ, CORONA_SZ), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(corona)
c_center = CORONA_SZ // 2

for r in range(CORONA_SZ // 2, JUP_D // 2 - 15, -4):
    norm = (r - (JUP_D // 2 - 15)) / (CORONA_SZ // 2 - (JUP_D // 2 - 15))
    alpha = int(185 * ((1.0 - norm) ** 1.5))
    c_draw.ellipse((c_center - r, c_center - r, c_center + r, c_center + r),
                   fill=(255, 140, 35, alpha))

for angle in np.linspace(0, 2*np.pi, 48, endpoint=False):
    ray_len = np.random.randint(JUP_D//2 + 50, CORONA_SZ//2 - 20)
    ex = int(c_center + ray_len * np.cos(angle))
    ey = int(c_center + ray_len * np.sin(angle))
    c_draw.line([(c_center, c_center), (ex, ey)], fill=(255, 195, 95, 55), width=np.random.randint(4, 10))

corona = corona.filter(ImageFilter.GaussianBlur(22))
canvas.paste(corona, (j_cx - c_center, j_cy - c_center), corona)

# Paste Jupiter disk with subtle smoothed limb mask
j_mask = Image.new("L", (JUP_D, JUP_D), 0)
jm_draw = ImageDraw.Draw(j_mask)
jm_draw.ellipse((0, 0, JUP_D, JUP_D), fill=255)
j_mask = j_mask.filter(ImageFilter.GaussianBlur(1.5))
canvas.paste(jup_disk, (j_cx - JUP_D//2, j_cy - JUP_D//2), j_mask)

# Ambient atmospheric limb flare (warm light wrap)
limb_glow = Image.new("RGBA", (JUP_D, JUP_D), (0, 0, 0, 0))
lg_draw = ImageDraw.Draw(limb_glow)
for i in range(12):
    a = int(160 * (1.0 - i / 12.0))
    lg_draw.ellipse((i, i, JUP_D - i, JUP_D - i), outline=(255, 215, 120, a), width=2)
limb_glow = limb_glow.filter(ImageFilter.GaussianBlur(4))
canvas.paste(limb_glow, (j_cx - JUP_D//2, j_cy - JUP_D//2), limb_glow)

# 3. Clean Mountain Summit Foreground ("นั่งบนเขา")
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

# Feather blend the sub region back into arr
sub_mask = Image.new("L", (sub.shape[1], sub.shape[0]), 255)
sub_mask = sub_mask.filter(ImageFilter.GaussianBlur(12))
sm_arr = np.array(sub_mask)[:, :, np.newaxis] / 255.0
arr[790:1170, 550:938] = arr[790:1170, 550:938] * (1.0 - sm_arr) + sub * sm_arr

clean_end = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")

# Scale to width 1080
scale = TARGET_W / clean_end.width
new_h = int(clean_end.height * scale)
scaled_clean = clean_end.resize((TARGET_W, new_h), Image.Resampling.LANCZOS)

# We want the mountain summit to sit in the lower 38% of the canvas:
# Crop lower 880px (summit, characters, clouds, city lights)
FG_H = 880
fg_crop = scaled_clean.crop((0, new_h - FG_H, TARGET_W, new_h))

# Soft top gradient fade: from y=0 to y=200
fg_mask = Image.new("L", (TARGET_W, FG_H), 255)
fm_draw = ImageDraw.Draw(fg_mask)
for y in range(180):
    val = int(255 * (y / 180.0)**1.6)
    fm_draw.line([(0, y), (TARGET_W, y)], fill=val)

# Composite foreground onto canvas: y from 1040 to 1920
canvas.paste(fg_crop, (0, TARGET_H - FG_H), fg_mask)

# Save pristine base artwork
pristine_base_path = "assets/jupiter_as_a_star_reel/raw/jupiter_summit_master_base.png"
canvas.save(pristine_base_path)
print("Saved pristine jupiter_summit_master_base.png successfully!")
