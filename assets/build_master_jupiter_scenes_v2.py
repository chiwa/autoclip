import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H = 1080, 1920
out_dir = "assets/jupiter_as_a_star_reel/images"
os.makedirs(out_dir, exist_ok=True)

# Load official corner round logo
logo_raw = Image.open("assets/branding/mamase/logo.png").convert("RGBA")
logo = logo_raw.resize((205, 205), Image.Resampling.LANCZOS)
logo_pos = (W - 205 - 36, 36)

def add_mamase_corner_logo(img):
    c = img.convert("RGBA")
    c.paste(logo, logo_pos, logo)
    return c.convert("RGB")

# Extract isolated Jupiter disk from Hubble portrait
im_hub = Image.open("assets/jupiter_as_a_star_reel/raw/jupiter_hubble_portrait.png").convert("RGB")
hub_arr = np.array(im_hub)
h_h, h_w = hub_arr.shape[:2]
cx, cy = 986.5, 1000.5
rx, ry = 768.0, 736.0

Y, X = np.ogrid[:h_h, :h_w]
dist_norm = ((X - cx) / rx)**2 + ((Y - cy) / ry)**2
jup_mask_arr = np.clip((1.0 - dist_norm) * 200, 0, 1) * 255
jup_mask = Image.fromarray(jup_mask_arr.astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.0))

jup_clean = Image.fromarray(hub_arr)
jup_clean.putalpha(jup_mask)
bbox_crop = jup_clean.crop((int(cx - rx - 10), int(cy - ry - 10), int(cx + rx + 10), int(cy + ry + 10)))

# -------------------------------------------------------------
# SCENE 02: Chemical Composition - Pure Starfield Background
# -------------------------------------------------------------
print("Building Scene 02 (Pure Starfield + Majestic Jupiter)...")
# Base: Starfield from cosmic frontier (no human presenter, no text)
bg_s2 = Image.open("assets/planet_nine_reel/images/scene-08-cosmic-frontier.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
bg_s2 = ImageEnhance.Brightness(bg_s2).enhance(0.45)

s2_jup = bbox_crop.resize((1040, int(bbox_crop.height * (1040 / bbox_crop.width))), Image.Resampling.LANCZOS)
glow_w, glow_h = s2_jup.width + 120, s2_jup.height + 120
s2_glow = Image.new("RGBA", (glow_w, glow_h), (0, 0, 0, 0))
draw_s2 = ImageDraw.Draw(s2_glow)
draw_s2.ellipse((30, 30, glow_w - 30, glow_h - 30), fill=(255, 180, 80, 160))
s2_glow = s2_glow.filter(ImageFilter.GaussianBlur(40))

s2_canvas = bg_s2.convert("RGBA")
j_x = (W - s2_jup.width) // 2
j_y = 360
s2_canvas.paste(s2_glow, (j_x - 60, j_y - 60), s2_glow)
s2_canvas.paste(s2_jup, (j_x, j_y), s2_jup)

s2_final = add_mamase_corner_logo(s2_canvas)
s2_final.save(os.path.join(out_dir, "scene-02-chemical-composition.png"), quality=98)
print("Scene 02 saved.")

# -------------------------------------------------------------
# SCENE 03: Mass Reality Check - Seamless Heliosphere Scale
# -------------------------------------------------------------
print("Building Scene 03 (Seamless Heliosphere Sun vs Planets)...")
# Use the gorgeous full vertical heliosphere bubble: scene-02-heliosphere-bubble.png
s3_src = Image.open("assets/oort_cloud_reel/images/scene-02-heliosphere-bubble.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
s3_final = add_mamase_corner_logo(s3_src)
s3_final.save(os.path.join(out_dir, "scene-03-mass-reality-check.png"), quality=98)
print("Scene 03 saved.")

# -------------------------------------------------------------
# SCENE 05: True Star Limit (75-80x) - Full Vertical Solar Flares
# -------------------------------------------------------------
print("Building Scene 05 (Full Vertical Solar Flares)...")
# Source: scene_04_solar_flare.png (1920x1080)
flare_raw = Image.open("assets/solar_storm_documentary/scene_04_solar_flare.png").convert("RGB")
# Crop center 1080 width to avoid black horizontal bars
fw, fh = flare_raw.size
crop_x = (fw - 1080) // 2 + 100
flare_mid = flare_raw.crop((crop_x, 0, crop_x + 1080, fh)) # 1080x1080
# Scale to fill vertical canvas smoothly
# Take top space and bottom space from dark starfield
bg_s5 = Image.open("assets/planet_nine_reel/images/scene-08-cosmic-frontier.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
bg_s5 = ImageEnhance.Brightness(bg_s5).enhance(0.5)
s5_canvas = bg_s5.convert("RGBA")

# Resize flare_mid to 1080x1200
flare_scaled = flare_mid.resize((W, 1200), Image.Resampling.LANCZOS)
# Create vertical gradient mask for smooth seamless top and bottom blend
mask_arr = np.ones((1200, W), dtype=np.float32) * 255
for y in range(1200):
    if y < 200:
        mask_arr[y, :] = (y / 200.0) * 255
    elif y > 950:
        mask_arr[y, :] = ((1200 - y) / 250.0) * 255
mask_img = Image.fromarray(mask_arr.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3.0))

flare_scaled.putalpha(mask_img)
s5_canvas.paste(flare_scaled, (0, 360), flare_scaled)
s5_final = add_mamase_corner_logo(s5_canvas)
s5_final.save(os.path.join(out_dir, "scene-05-true-star-limit.png"), quality=98)
print("Scene 05 saved.")

# -------------------------------------------------------------
# SCENE 06: Earth Orbit Chaos - Gravity Boundary Spacetime Distortion
# -------------------------------------------------------------
print("Building Scene 06 (Spacetime Gravitational Distortions)...")
# Base: scene-07-gravity-boundary.png (1080x1920) - Spacetime grid distortion with gravitational laser/well
s6_src = Image.open("assets/oort_cloud_reel/images/scene-07-gravity-boundary.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
s6_final = add_mamase_corner_logo(s6_src)
s6_final.save(os.path.join(out_dir, "scene-06-earth-orbit-chaos.png"), quality=98)
print("Scene 06 saved.")

# -------------------------------------------------------------
# SCENE 07: Guardian Shield Payoff - Cosmic Shield Inbound Asteroids
# -------------------------------------------------------------
print("Building Scene 07 (Cosmic Shield & Inbound Asteroids)...")
# Base: scene-05-domino-effect-comets.png (1080x1920) - Solar system in center with countless inbound comets/asteroids
s7_src = Image.open("assets/stellar_flyby_reel/images/scene-05-domino-effect-comets.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
# Place clean Jupiter disk near the center-upper orbit to demonstrate Jupiter's massive gravitational shield
jup_guard = bbox_crop.resize((420, int(bbox_crop.height * (420 / bbox_crop.width))), Image.Resampling.LANCZOS)
# Glow around Jupiter shield
g_w, g_h = jup_guard.width + 60, jup_guard.height + 60
g_mask = Image.new("RGBA", (g_w, g_h), (0, 0, 0, 0))
ImageDraw.Draw(g_mask).ellipse((10, 10, g_w - 10, g_h - 10), fill=(120, 200, 255, 120))
g_mask = g_mask.filter(ImageFilter.GaussianBlur(15))

s7_canvas = s7_src.convert("RGBA")
s7_canvas.paste(g_mask, (W//2 - g_w//2, 480 - 30), g_mask)
s7_canvas.paste(jup_guard, (W//2 - jup_guard.width//2, 480), jup_guard)

s7_final = add_mamase_corner_logo(s7_canvas)
s7_final.save(os.path.join(out_dir, "scene-07-guardian-shield-payoff.png"), quality=98)
print("Scene 07 saved.")

print("Master visual upgrade v2 complete!")
