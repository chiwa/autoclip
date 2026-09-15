import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import os, sys

TARGET_W = 1080
TARGET_H = 1920

# 1. Base canvas with deep cosmic starfield
canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (4, 5, 10, 255))
s_draw = ImageDraw.Draw(canvas)
np.random.seed(42)
for _ in range(400):
    sx = np.random.randint(0, TARGET_W)
    sy = np.random.randint(0, 1100)
    b = np.random.randint(70, 255)
    tint = (b, int(b * 0.93), int(b * 0.85), 255) if np.random.rand() > 0.5 else (int(b * 0.85), int(b * 0.95), b, 255)
    s_draw.point((sx, sy), fill=tint)
    if b > 235 and sy < 900:
        s_draw.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        s_draw.line([(sx, sy-1), (sx, sy+1)], fill=tint)

# 2. Tightly crop Jupiter from authentic Hubble portrait (NO black border)
jup_raw = Image.open("assets/jupiter_as_a_star_reel/raw/jupiter_hubble_portrait.png").convert("RGBA")
# Bounding box of planet disk: x: 215..1759, y: 260..1741
jup_cropped = jup_raw.crop((215, 260, 1759, 1741))

# Colossal diameter: 960x960!
JUP_D = 960
jup_disk = jup_cropped.resize((JUP_D, JUP_D), Image.Resampling.LANCZOS)

# Position Jupiter in upper-middle: center at (540, 560)
j_cx, j_cy = 540, 560

# 3. Create vibrant stellar corona glow radiating DIRECTLY from the disk edge
CORONA_SZ = 1400
corona = Image.new("RGBA", (CORONA_SZ, CORONA_SZ), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(corona)
c_center = CORONA_SZ // 2

# Golden/amber incandescent stellar atmosphere
for r in range(CORONA_SZ // 2, JUP_D // 2 - 20, -4):
    norm = (r - (JUP_D // 2 - 20)) / (CORONA_SZ // 2 - (JUP_D // 2 - 20))
    alpha = int(180 * ((1.0 - norm) ** 1.5))
    c_draw.ellipse((c_center - r, c_center - r, c_center + r, c_center + r),
                   fill=(255, 140, 40, alpha))

# Radial proto-star flares
for angle in np.linspace(0, 2*np.pi, 48, endpoint=False):
    ray_len = np.random.randint(JUP_D//2 + 40, CORONA_SZ//2 - 20)
    ex = int(c_center + ray_len * np.cos(angle))
    ey = int(c_center + ray_len * np.sin(angle))
    c_draw.line([(c_center, c_center), (ex, ey)], fill=(255, 190, 90, 55), width=np.random.randint(4, 10))

corona = corona.filter(ImageFilter.GaussianBlur(22))
canvas.paste(corona, (j_cx - c_center, j_cy - c_center), corona)

# Circular mask for Jupiter disk
j_mask = Image.new("L", (JUP_D, JUP_D), 0)
jm_draw = ImageDraw.Draw(j_mask)
jm_draw.ellipse((0, 0, JUP_D, JUP_D), fill=255)
# Soften the edge of mask slightly (2px blur) for photorealistic limb integration
j_mask = j_mask.filter(ImageFilter.GaussianBlur(1.5))

# Paste Jupiter disk onto canvas
canvas.paste(jup_disk, (j_cx - JUP_D//2, j_cy - JUP_D//2), j_mask)

# Add delicate incandescent rim flare (light wrap) over Jupiter limb
limb_glow = Image.new("RGBA", (JUP_D, JUP_D), (0, 0, 0, 0))
lg_draw = ImageDraw.Draw(limb_glow)
for i in range(14):
    a = int(170 * (1.0 - i / 14.0))
    lg_draw.ellipse((i, i, JUP_D - i, JUP_D - i), outline=(255, 215, 120, a), width=2)
limb_glow = limb_glow.filter(ImageFilter.GaussianBlur(5))
canvas.paste(limb_glow, (j_cx - JUP_D//2, j_cy - JUP_D//2), limb_glow)

# 4. Load mountain scene with Person & Dog ("นั่งบนเขา")
end_img = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGBA")
# Scale proportionally to width 1080
scale = TARGET_W / end_img.width
new_h = int(end_img.height * scale)
end_scaled = end_img.resize((TARGET_W, new_h), Image.Resampling.LANCZOS)

# Crop the lower portion (mountain ridge, clouds, city lights, person and dog)
# Total height from summit down: height 900
mount_crop = end_scaled.crop((0, new_h - 900, TARGET_W, new_h))
mc_w, mc_h = mount_crop.size

# Clean the faint cursive text on the hoodie (x: 20..180, y: 220..420 in mount_crop)
hoodie_patch = mount_crop.crop((20, 220, 180, 420)).filter(ImageFilter.MedianFilter(size=13))
mount_crop.paste(hoodie_patch, (20, 220))

# Clean the right-side text by sampling the glowing cloud & horizon gradient
# The text "เพราะในจักรวาลนี้... THANK YOU" is at x: 640..980, y: 100..340 in mount_crop
# Below y=340 is the golden sea of clouds and city lights
# We replace the text area with a clean twilight gradient that blends into the horizon
cloud_bg = mount_crop.crop((600, 320, 980, 480)).resize((380, 240))
cloud_bg = cloud_bg.filter(ImageFilter.GaussianBlur(16))
mount_crop.paste(cloud_bg, (600, 100), mask=Image.new("L", (380, 240), 220))

# Create smooth gradient mask for mountain foreground:
# Fade in from y = 0 to y = 260
m_mask = Image.new("L", (mc_w, mc_h), 255)
mm_draw = ImageDraw.Draw(m_mask)
for y in range(240):
    val = int(255 * (y / 240.0)**1.8)
    mm_draw.line([(0, y), (mc_w, y)], fill=val)

# Composite mountain foreground onto canvas: y from 1020 to 1920
canvas.paste(mount_crop, (0, TARGET_H - mc_h), m_mask)

# Save pristine composite base
base_output = "/Users/zengcode/projects/autoclip/assets/jupiter_as_a_star_reel/raw/jupiter_summit_master_base.png"
canvas.save(base_output)
print("Saved jupiter_summit_master_base.png successfully!")
