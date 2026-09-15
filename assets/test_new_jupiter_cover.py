import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import os

# 1. Load mountain crop
crop_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/test_mountain_crop.png"
crop = Image.open(crop_path).convert("RGBA")
cw, ch = crop.size # 1080 x 1058

# Clean the faint cursive text on the hoodie
# The text is around x: 15..170, y: 370..560
hoodie_patch = crop.crop((20, 360, 180, 560)).filter(ImageFilter.MedianFilter(size=11))
# Smooth blend over the text area
crop.paste(hoodie_patch, (20, 360))

# 2. Prepare 1080x1920 canvas
TARGET_W = 1080
TARGET_H = 1920
canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (5, 6, 12, 255))

# Create deep starry sky background
sky_bg = Image.new("RGBA", (TARGET_W, TARGET_H), (4, 5, 10, 255))
s_draw = ImageDraw.Draw(sky_bg)
np.random.seed(42)
for _ in range(450):
    sx = np.random.randint(0, TARGET_W)
    sy = np.random.randint(0, 1400)
    b = np.random.randint(60, 255)
    tint = (b, int(b * 0.92), int(b * 0.85), 255) if np.random.rand() > 0.5 else (int(b * 0.85), int(b * 0.95), b, 255)
    s_draw.point((sx, sy), fill=tint)
    if b > 230 and sy < 1100:
        s_draw.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        s_draw.line([(sx, sy-1), (sx, sy+1)], fill=tint)

canvas = sky_bg

# 3. Load Hubble Jupiter and resize to COLOSSAL scale
jup_raw = Image.open("assets/jupiter_as_a_star_reel/raw/jupiter_hubble_portrait.png").convert("RGBA")
# Jupiter hero size: 920x920
JUP_SIZE = 920
jup_hero = jup_raw.resize((JUP_SIZE, JUP_SIZE), Image.Resampling.LANCZOS)

# Create circular mask for Jupiter disk
j_mask = Image.new("L", (JUP_SIZE, JUP_SIZE), 0)
j_draw = ImageDraw.Draw(j_mask)
j_draw.ellipse((0, 0, JUP_SIZE, JUP_SIZE), fill=255)

# Add stellar corona / proto-star ignited glow
corona_size = JUP_SIZE + 320
corona = Image.new("RGBA", (corona_size, corona_size), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(corona)
c_center = corona_size // 2

# Layered golden/amber stellar glow
for r in range(c_center, JUP_SIZE // 2 - 20, -4):
    ratio = (r - (JUP_SIZE // 2)) / (c_center - JUP_SIZE // 2)
    alpha = int(140 * (1.0 - ratio)**1.8)
    # Warm stellar orange-gold
    c_draw.ellipse((c_center - r, c_center - r, c_center + r, c_center + r),
                   fill=(255, 140, 40, alpha))

# Smooth corona blur
corona = corona.filter(ImageFilter.GaussianBlur(16))

# Position Jupiter in the upper-mid sky: center_x = 540, center_y = 650
jup_cx = 540
jup_cy = 620

# Paste corona
canvas.paste(corona, (jup_cx - corona_size//2, jup_cy - corona_size//2), corona)

# Paste Jupiter disk
canvas.paste(jup_hero, (jup_cx - JUP_SIZE//2, jup_cy - JUP_SIZE//2), j_mask)

# Add intense solar rim lighting / flare highlights around Jupiter limb
rim_flare = Image.new("RGBA", (JUP_SIZE, JUP_SIZE), (0, 0, 0, 0))
rf_draw = ImageDraw.Draw(rim_flare)
for offset in range(12):
    alpha = int(180 * (1.0 - offset/12.0))
    rf_draw.ellipse((offset, offset, JUP_SIZE - offset, JUP_SIZE - offset),
                    outline=(255, 200, 100, alpha), width=2)
rim_flare = rim_flare.filter(ImageFilter.GaussianBlur(4))
canvas.paste(rim_flare, (jup_cx - JUP_SIZE//2, jup_cy - JUP_SIZE//2), rim_flare)

# 4. Composite foreground mountain with explorer and dog
# The mountain crop will sit in the lower portion: y from 980 to 1920 (height ~940)
# We want the mountain summit & characters to sit in front of Jupiter
# Let us resize the mountain crop slightly to span nicely:
fg_h = 940
fg_w = TARGET_W
fg_scaled = crop.crop((0, ch - fg_h, cw, ch))

# Create smooth gradient mask for sky/horizon blend of the mountain crop
fg_mask = Image.new("L", (fg_w, fg_h), 255)
fm_draw = ImageDraw.Draw(fg_mask)
# Top of mountain crop has horizon clouds and sky: blend from y=0 to y=180
for y in range(180):
    val = int(255 * (y / 180.0)**1.2)
    fm_draw.line([(0, y), (fg_w, y)], fill=val)

# Apply mask and paste foreground
canvas.paste(fg_scaled, (0, TARGET_H - fg_h), fg_mask)

# Save test base
out_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/test_new_jupiter_base.png"
canvas.save(out_path)
print("Saved test new jupiter base to", out_path)
