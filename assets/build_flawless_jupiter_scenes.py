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
print("Extracting clean circular Jupiter disk...")
im_hub = Image.open("assets/jupiter_as_a_star_reel/raw/jupiter_hubble_portrait.png").convert("RGB")
# Bounding box: x=(214, 1759), y=(260, 1741)
# Center: (986.5, 1000.5), rx=772.5, ry=740.5
hub_arr = np.array(im_hub)
h_h, h_w = hub_arr.shape[:2]
cx, cy = 986.5, 1000.5
rx, ry = 768.0, 736.0 # slightly inside limb to avoid dark fringes

# Create smooth antialiased circular mask
Y, X = np.ogrid[:h_h, :h_w]
dist_norm = ((X - cx) / rx)**2 + ((Y - cy) / ry)**2
jup_mask_arr = np.clip((1.0 - dist_norm) * 200, 0, 1) * 255
# Soft edge feather
jup_mask = Image.fromarray(jup_mask_arr.astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.0))

jup_clean = Image.fromarray(hub_arr)
jup_clean.putalpha(jup_mask)
# Crop to bounding box
bbox_crop = jup_clean.crop((int(cx - rx - 10), int(cy - ry - 10), int(cx + rx + 10), int(cy + ry + 10)))
print(f"Extracted Jupiter clean disk: {bbox_crop.size}")

# -------------------------------------------------------------
# SCENE 02: Chemical Composition - Atmospheric Bands & Great Red Spot
# -------------------------------------------------------------
print("Compositing Scene 02...")
# Starfield background from comets_reel
bg_s2 = Image.open("assets/comets_reel/images/scene-01-hook.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
# Darken background slightly to emphasize Jupiter
bg_s2 = ImageEnhance.Brightness(bg_s2).enhance(0.4)

# Colossal Jupiter disk: 1040px width
s2_jup = bbox_crop.resize((1040, int(bbox_crop.height * (1040 / bbox_crop.width))), Image.Resampling.LANCZOS)
# Add warm golden-amber atmospheric limb glow
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
# SCENE 03: Mass Reality Check - Sun vs Jupiter Scale
# -------------------------------------------------------------
print("Compositing Scene 03...")
# Base: Solar storm Sun disk (1920x1080)
sun_src = Image.open("assets/solar_storm_documentary/scene_02_serene_sun.png").convert("RGB")
# Scale Sun to be gigantic in upper frame
# Crop Sun circle to dominate upper 60%
sun_w, sun_h = sun_src.size
# Let Sun occupy top portion
sun_crop = sun_src.resize((W, int(sun_h * (W / sun_w))), Image.Resampling.LANCZOS)
s3_bg = Image.new("RGB", (W, H), (2, 4, 10))
s3_canvas = s3_bg.convert("RGBA")
# Paste Sun at top
s3_canvas.paste(sun_crop.convert("RGBA"), (0, 0))
# Add dark gradient fade at the bottom of the Sun
grad = Image.new("L", (W, H), 0)
for y in range(H):
    if y < 800:
        val = 255
    elif y < 1200:
        val = int(255 * (1.0 - (y - 800) / 400.0))
    else:
        val = 0
    grad.paste(val, (0, y, W, y+1))
# Combine Sun with dark starfield below
star_tile = Image.open("assets/planet_nine_reel/images/scene-08-cosmic-frontier.png").convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
s3_final_bg = Image.composite(s3_canvas, star_tile, grad)

# Now place Jupiter as a small dot/circle (0.1% mass / 10x smaller radius) with cyan target reticle
jup_scale = bbox_crop.resize((210, int(bbox_crop.height * (210 / bbox_crop.width))), Image.Resampling.LANCZOS)
# Paste Jupiter in mid-lower region (y=1180)
s3_final_bg.paste(jup_scale, ((W - 210)//2, 1160), jup_scale)

# Draw subtle scientific scale bracket / leader line
draw_s3 = ImageDraw.Draw(s3_final_bg)
# Sun label area
draw_s3.line([(180, 520), (280, 520), (340, 600)], fill=(255, 220, 120, 180), width=2)
draw_s3.ellipse([(336, 596), (344, 604)], fill=(255, 220, 120, 255))
# Jupiter label area
draw_s3.ellipse([((W - 230)//2, 1150), ((W + 230)//2, 1150 + int(bbox_crop.height * (210 / bbox_crop.width)) + 20)], outline=(115, 220, 255, 200), width=2)

s3_out = add_mamase_corner_logo(s3_final_bg)
s3_out.save(os.path.join(out_dir, "scene-03-mass-reality-check.png"), quality=98)
print("Scene 03 saved.")

# -------------------------------------------------------------
# SCENE 05: True Star Limit (75-80x) - Blazing Red Dwarf with Solar Flares
# -------------------------------------------------------------
print("Compositing Scene 05...")
# Source: scene_04_solar_flare.png (1920x1080)
flare_src = Image.open("assets/solar_storm_documentary/scene_04_solar_flare.png").convert("RGB")
# Scale flare to fill 9:16 vertical dramatically
fw, fh = flare_src.size
# Crop to focus on the energetic stellar flare arc and limb
target_h = int(fw * (16 / 9))
# Pad vertically with starry darkness or resize
flare_scaled = flare_src.resize((W, int(fh * (W / fw))), Image.Resampling.LANCZOS)
# Create vertical 9:16 canvas with starfield
s5_canvas = Image.open("assets/planet_nine_reel/images/scene-08-cosmic-frontier.png").convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
# Place solar flare in upper-mid frame
s5_canvas.paste(flare_scaled.convert("RGBA"), (0, 320))
# Blend bottom edge of flare
flare_fade = Image.new("L", (W, flare_scaled.height), 255)
for y in range(flare_scaled.height):
    if y > flare_scaled.height - 250:
        val = int(255 * (1.0 - (y - (flare_scaled.height - 250)) / 250.0))
        flare_fade.paste(val, (0, y, W, y+1))
flare_scaled.putalpha(flare_fade)
s5_canvas.paste(flare_scaled, (0, 320), flare_scaled)

s5_final = add_mamase_corner_logo(s5_canvas)
s5_final.save(os.path.join(out_dir, "scene-05-true-star-limit.png"), quality=98)
print("Scene 05 saved.")

# -------------------------------------------------------------
# SCENE 06: Earth Orbit Chaos - Gravitational Perturbation with Earth & Star
# -------------------------------------------------------------
print("Compositing Scene 06...")
# Base: chaotic orbit lines
s6_src = Image.open("assets/planet_nine_reel/images/scene-02-strange-orbits.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
# Overlay Earth in foreground lower-left being pulled out of orbit
earth_src = Image.open("assets/voyager1_reel/images/scene-05-attowatt-signal-earth.png").convert("RGB")
# Earth disk crop from scene-05
ew, eh = earth_src.size
earth_crop = earth_src.crop((ew//2 - 250, eh//2 - 250, ew//2 + 250, eh//2 + 250)).resize((340, 340), Image.Resampling.LANCZOS)
e_mask = Image.new("L", (340, 340), 0)
ImageDraw.Draw(e_mask).ellipse((5, 5, 335, 335), fill=255)
e_mask = e_mask.filter(ImageFilter.GaussianBlur(1.5))
earth_crop.putalpha(e_mask)

s6_canvas = s6_src.convert("RGBA")
# Place Earth in lower third
s6_canvas.paste(earth_crop, (120, 1120), earth_crop)
s6_final = add_mamase_corner_logo(s6_canvas)
s6_final.save(os.path.join(out_dir, "scene-06-earth-orbit-chaos.png"), quality=98)
print("Scene 06 saved.")

# -------------------------------------------------------------
# SCENE 07: Guardian Shield Payoff - Jupiter Gravitational Shield Deflecting Comets
# -------------------------------------------------------------
print("Compositing Scene 07...")
# Base: comets scene with space dust and comet
s7_base = Image.open("assets/comets_reel/images/scene-02-solar-wind-direction.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
s7_canvas = s7_base.convert("RGBA")
# Place clean Jupiter disk (880px) in upper-mid frame with zero black box
s7_jup = bbox_crop.resize((880, int(bbox_crop.height * (880 / bbox_crop.width))), Image.Resampling.LANCZOS)
# Subtle gravitational lens rim
s7_glow = Image.new("RGBA", (960, 960), (0, 0, 0, 0))
draw_s7 = ImageDraw.Draw(s7_glow)
draw_s7.ellipse((20, 20, 940, 940), fill=(100, 180, 255, 90))
s7_glow = s7_glow.filter(ImageFilter.GaussianBlur(30))

s7_canvas.paste(s7_glow, ((W - 960)//2, 280), s7_glow)
s7_canvas.paste(s7_jup, ((W - 880)//2, 320), s7_jup)

s7_final = add_mamase_corner_logo(s7_canvas)
s7_final.save(os.path.join(out_dir, "scene-07-guardian-shield-payoff.png"), quality=98)
print("Scene 07 saved.")

print("All scenes rebuilt with flawless cinematic quality!")
