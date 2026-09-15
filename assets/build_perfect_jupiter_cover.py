import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import os, sys

TARGET_W = 1080
TARGET_H = 1920

# 1. Base canvas: Deep rich space
canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (4, 5, 10, 255))
s_draw = ImageDraw.Draw(canvas)
np.random.seed(2026)
for _ in range(500):
    sx = np.random.randint(0, TARGET_W)
    sy = np.random.randint(0, 1300)
    b = np.random.randint(70, 255)
    tint = (b, int(b * 0.94), int(b * 0.88), 255) if np.random.rand() > 0.4 else (int(b * 0.88), int(b * 0.95), b, 255)
    s_draw.point((sx, sy), fill=tint)
    if b > 230 and sy < 1000:
        s_draw.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        s_draw.line([(sx, sy-1), (sx, sy+1)], fill=tint)

# 2. Prepare Colossal Jupiter Star (Brown Dwarf / Proto-star Ignition)
jup_raw = Image.open("assets/jupiter_as_a_star_reel/raw/jupiter_hubble_portrait.png").convert("RGBA")
# Colossal diameter: 960px! Dominates 89% of width!
JUP_D = 960
jup_disk = jup_raw.resize((JUP_D, JUP_D), Image.Resampling.LANCZOS)

# Position Jupiter in upper-middle: center at (540, 560)
j_cx, j_cy = 540, 560

# Create vibrant stellar corona glow behind Jupiter
# Corona size: 1400x1400
CORONA_SZ = 1400
corona = Image.new("RGBA", (CORONA_SZ, CORONA_SZ), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(corona)
c_center = CORONA_SZ // 2

# Layered incandescent fiery glow radiating outwards from the core
for r in range(CORONA_SZ // 2, JUP_D // 2 - 40, -4):
    norm = (r - (JUP_D // 2 - 40)) / (CORONA_SZ // 2 - (JUP_D // 2 - 40))
    # Exponential dropoff
    alpha = int(170 * ((1.0 - norm) ** 1.6))
    # Golden amber / reddish star temperature (255, 120, 30)
    c_draw.ellipse((c_center - r, c_center - r, c_center + r, c_center + r),
                   fill=(255, 135, 35, alpha))

# Radial stellar flare rays
for angle in np.linspace(0, 2*np.pi, 36, endpoint=False):
    ray_len = np.random.randint(JUP_D//2 + 30, CORONA_SZ//2 - 20)
    ex = int(c_center + ray_len * np.cos(angle))
    ey = int(c_center + ray_len * np.sin(angle))
    c_draw.line([(c_center, c_center), (ex, ey)], fill=(255, 180, 80, 45), width=np.random.randint(4, 12))

corona = corona.filter(ImageFilter.GaussianBlur(24))
canvas.paste(corona, (j_cx - c_center, j_cy - c_center), corona)

# Circular mask for Jupiter disk
j_mask = Image.new("L", (JUP_D, JUP_D), 0)
jm_draw = ImageDraw.Draw(j_mask)
jm_draw.ellipse((0, 0, JUP_D, JUP_D), fill=255)

# Paste Jupiter disk
canvas.paste(jup_disk, (j_cx - JUP_D//2, j_cy - JUP_D//2), j_mask)

# Add incandescent atmosphere rim glow (light wrap) over Jupiter limb
limb_glow = Image.new("RGBA", (JUP_D, JUP_D), (0, 0, 0, 0))
lg_draw = ImageDraw.Draw(limb_glow)
for i in range(16):
    a = int(160 * (1.0 - i / 16.0))
    lg_draw.ellipse((i, i, JUP_D - i, JUP_D - i), outline=(255, 205, 110, a), width=2)
limb_glow = limb_glow.filter(ImageFilter.GaussianBlur(6))
canvas.paste(limb_glow, (j_cx - JUP_D//2, j_cy - JUP_D//2), limb_glow)

# 3. Load mountain scene with Person & Dog ("นั่งบนเขา")
# From assets/branding/mamase/reels-end-scene.png
end_img = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGBA")
# Target width is 1080. Scale end_img proportionally:
scale = TARGET_W / end_img.width # 1080 / 941 = 1.1477
new_h = int(end_img.height * scale)
end_scaled = end_img.resize((TARGET_W, new_h), Image.Resampling.LANCZOS)

# Crop the lower 920px (mountain ridge, clouds, person and dog)
# The person & dog are in the lower half
mount_crop = end_scaled.crop((0, new_h - 960, TARGET_W, new_h))
mc_w, mc_h = mount_crop.size

# Clean the text on the right of mount_crop: "เพราะในจักรวาลนี้..."
# In mount_crop, this text is around x: 670..980, y: 150..380
# We can paint over it with the actual starry background + golden horizon light
mc_draw = ImageDraw.Draw(mount_crop)
# Create a smooth alpha gradient mask for mount_crop top:
# Fade in from y = 0 to y = 280
m_mask = Image.new("L", (mc_w, mc_h), 255)
mm_draw = ImageDraw.Draw(m_mask)
for y in range(260):
    val = int(255 * (y / 260.0)**1.5)
    mm_draw.line([(0, y), (mc_w, y)], fill=val)

# For the text on the right (x > 620, y < 380), mask it out more aggressively:
for y in range(380):
    val = int(255 * (max(0, y - 100) / 280.0)**2.0)
    for x in range(600, mc_w):
        m_mask.putpixel((x, y), min(m_mask.getpixel((x, y)), val))

# Clean the faint cursive text on hoodie:
# In mount_crop, boy's back is at x: 20..180, y: 280..480
hoodie_sample = mount_crop.crop((40, 420, 160, 480)).resize((160, 180), Image.Resampling.BICUBIC)
hoodie_sample = hoodie_sample.filter(ImageFilter.GaussianBlur(4))
mount_crop.paste(hoodie_sample, (20, 280), mask=Image.new("L", (160, 180), 200))

# Composite mountain foreground onto canvas at the bottom: y from 960 to 1920
canvas.paste(mount_crop, (0, TARGET_H - mc_h), m_mask)

# Save the pristine base artwork
base_save_path = "/Users/zengcode/projects/autoclip/assets/jupiter_as_a_star_reel/raw/jupiter_mountain_star_base.png"
canvas.save(base_save_path)
print("Saved jupiter_mountain_star_base.png successfully!")
