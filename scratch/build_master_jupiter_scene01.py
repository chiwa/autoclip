import os, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps

W, H = 1080, 1920

# 1. Base Deep Cosmos Sky Canvas (9:16)
canvas = Image.new("RGBA", (W, H), (4, 6, 14, 255))
sky_draw = ImageDraw.Draw(canvas)

# Create subtle cosmic nebula dust
np.random.seed(42)
nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
n_draw = ImageDraw.Draw(nebula)
for _ in range(8):
    cx = np.random.randint(200, 900)
    cy = np.random.randint(100, 1000)
    rx = np.random.randint(250, 500)
    ry = np.random.randint(200, 450)
    n_draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(15, 25, 45, 35))
nebula = nebula.filter(ImageFilter.GaussianBlur(60))
canvas = Image.alpha_composite(canvas, nebula)

# Add fine stars & stellar points
s_draw = ImageDraw.Draw(canvas)
for _ in range(450):
    sx = np.random.randint(0, W)
    sy = np.random.randint(0, 1350)
    bright = np.random.randint(60, 255)
    tint = (bright, int(bright * 0.94), int(bright * 0.88), 255) if np.random.rand() > 0.4 else (int(bright * 0.88), int(bright * 0.95), bright, 255)
    s_draw.point((sx, sy), fill=tint)
    if bright > 230 and sy < 1100:
        s_draw.line([(sx - 1, sy), (sx + 1, sy)], fill=tint)
        s_draw.line([(sx, sy - 1), (sx, sy + 1)], fill=tint)

# 2. Add Colossal Jupiter as a Star
# We place Jupiter centered horizontally at x=540, y=700 (or slightly to the right at x=560, y=710)
# Leaving top-left (x: 50..550, y: 150..650) with clean space for title overlay
jup_cx, jup_cy = 560, 720
jup_diam = 860

# Load Hubble 4K Jupiter portrait
jup_path = "assets/jupiter_as_a_star_reel/raw/jupiter_hubble_portrait.png"
jup_src = Image.open(jup_path).convert("RGBA")
# Crop tightly to Jupiter planet boundary (215, 260, 1759, 1741)
jup_disk_raw = jup_src.crop((215, 260, 1759, 1741))
jup_disk = jup_disk_raw.resize((jup_diam, jup_diam), Image.Resampling.LANCZOS)

# Create organic stellar corona around Jupiter
# Outer corona radiance
corona_size = 1500
corona = Image.new("RGBA", (corona_size, corona_size), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(corona)
c_center = corona_size // 2

# Golden-orange stellar gradient falloff
for r in range(corona_size // 2, jup_diam // 2 - 20, -3):
    norm = (r - (jup_diam // 2 - 20)) / (corona_size // 2 - (jup_diam // 2 - 20))
    # Non-linear falloff
    alpha = int(185 * ((1.0 - norm) ** 1.65))
    # Transition from solar white-gold at core to fiery amber-orange
    r_val = 255
    g_val = int(180 * (1.0 - norm * 0.45))
    b_val = int(60 * (1.0 - norm))
    c_draw.ellipse((c_center - r, c_center - r, c_center + r, c_center + r), fill=(r_val, g_val, b_val, alpha))

# Add dynamic solar prominence loops and coronal flare rays
for angle in np.linspace(0, 2 * np.pi, 64, endpoint=False):
    ray_len = np.random.randint(jup_diam // 2 + 40, corona_size // 2 - 40)
    ex = int(c_center + ray_len * np.cos(angle))
    ey = int(c_center + ray_len * np.sin(angle))
    c_draw.line([(c_center, c_center), (ex, ey)], fill=(255, 200, 100, int(np.random.randint(25, 65))), width=np.random.randint(2, 6))

corona = corona.filter(ImageFilter.GaussianBlur(18))

# Paste corona onto canvas
c_x = jup_cx - corona_size // 2
c_y = jup_cy - corona_size // 2
canvas.paste(corona, (c_x, c_y), corona)

# Circular mask for Jupiter disk
j_mask = Image.new("L", (jup_diam, jup_diam), 0)
jm_draw = ImageDraw.Draw(j_mask)
jm_draw.ellipse((0, 0, jup_diam, jup_diam), fill=255)

# Slight warm grade on Jupiter to reflect nascent star heating
j_enhancer = ImageEnhance.Color(jup_disk)
jup_graded = j_enhancer.enhance(1.15)
b_enhancer = ImageEnhance.Brightness(jup_graded)
jup_graded = b_enhancer.enhance(1.08)

# Paste Jupiter disk
canvas.paste(jup_graded, (jup_cx - jup_diam // 2, jup_cy - jup_diam // 2), j_mask)

# Add brilliant solar rim lighting / limb flare
limb_flare = Image.new("RGBA", (jup_diam, jup_diam), (0, 0, 0, 0))
lf_draw = ImageDraw.Draw(limb_flare)
for offset in range(16):
    alpha = int(220 * (1.0 - offset / 16.0) ** 1.3)
    lf_draw.ellipse((offset, offset, jup_diam - offset, jup_diam - offset), outline=(255, 230, 140, alpha), width=2)
limb_flare = limb_flare.filter(ImageFilter.GaussianBlur(4))
canvas.paste(limb_flare, (jup_cx - jup_diam // 2, jup_cy - jup_diam // 2), limb_flare)

# Add subtle starlight rays descending from Jupiter toward the horizon
rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
r_draw = ImageDraw.Draw(rays)
for i in range(18):
    angle = np.pi / 2 + (i - 9) * 0.08
    r_len = np.random.randint(600, 1000)
    tx = int(jup_cx + r_len * np.cos(angle))
    ty = int(jup_cy + r_len * np.sin(angle))
    r_draw.line([(jup_cx, jup_cy), (tx, ty)], fill=(255, 210, 120, np.random.randint(12, 30)), width=np.random.randint(8, 22))
rays = rays.filter(ImageFilter.GaussianBlur(25))
canvas = Image.alpha_composite(canvas, rays)

# 3. Midground: Horizon, clouds, and distant valley city lights
# From ISS benchmark: the curved Earth with city lights and blue atmosphere limb gave that epic scale!
# Let us adapt the Earth curvature / sea of clouds & horizon from the benchmark to create a cohesive world:
iss_base = Image.open("assets/iss_why_not_fall_reel/images/scene-01-hook-base.png").convert("RGBA")
# ISS base has the magnificent Earth limb with city lights from y: 950 to 1920
earth_horizon = iss_base.crop((0, 950, W, 1920))

# Warm grade the horizon clouds to match Jupiter stellar illumination
# Blend subtle amber/golden warmth into the Earth limb lights
amber_tint = Image.new("RGBA", earth_horizon.size, (255, 160, 40, 35))
earth_horizon_warm = Image.alpha_composite(earth_horizon, amber_tint)

# Soft feather mask for the top of the horizon (y=0..120 of earth_horizon)
h_mask = Image.new("L", earth_horizon.size, 255)
hm_draw = ImageDraw.Draw(h_mask)
for y in range(130):
    val = int(255 * (y / 130.0) ** 1.4)
    hm_draw.line([(0, y), (W, y)], fill=val)

# Paste midground + foreground onto canvas
canvas.paste(earth_horizon_warm, (0, 950), h_mask)

# 4. Save Raw Base Artwork (Clean, no text, no logo)
raw_out = "assets/jupiter_as_a_star_reel/raw/scene-01-hook-raw.png"
os.makedirs("assets/jupiter_as_a_star_reel/raw", exist_ok=True)
canvas.convert("RGB").save(raw_out, quality=98)
print(f"Generated clean raw artwork: {raw_out}")

