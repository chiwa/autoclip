import os, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
out_dir = "assets/voyager1_reel/images"
os.makedirs(out_dir, exist_ok=True)

# -------------------------------------------------------------
# Logo Setup
# -------------------------------------------------------------
logo_raw = Image.open("assets/branding/mamase/logo.png").convert("RGBA")
logo_size = 205
logo = logo_raw.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
logo_x = TARGET_WIDTH - logo_size - 36  # 839
logo_y = 36

l_shadow = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
l_shadow.paste(Image.new("RGBA", (logo_size, logo_size), (0, 0, 0, 220)), (logo_x, logo_y + 3), mask=logo.split()[3])
l_shadow = l_shadow.filter(ImageFilter.GaussianBlur(12))

def apply_logo(im):
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    im = Image.alpha_composite(im, l_shadow)
    im.paste(logo, (logo_x, logo_y), mask=logo)
    return im.convert("RGB")

print("Logo ready.")

# -------------------------------------------------------------
# 1. SCENE 02: Interstellar Distance
# -------------------------------------------------------------
# Topic: Voyager 1 in deep space, looking back at Sun/Solar System as a distant star
print("Building Scene 02: Interstellar Distance...")
# Base: High-res deep space starry cosmos (scene-05-voyager-journey.png)
base2 = Image.open("assets/oort_cloud_reel/images/scene-05-voyager-journey.png").convert("RGB")
# We already have voyager in scene-05! It shows Voyager 1 silhouetted against the colossal Milky Way!
# Let us enhance it: adjust contrast, add slight cool cyan/navy grading to match Master DNA
enhancer = ImageEnhance.Color(base2)
s2 = enhancer.enhance(1.1)
s2 = apply_logo(s2)
s2.save(os.path.join(out_dir, "scene-02-interstellar-distance.png"), quality=98)
print("Saved scene-02-interstellar-distance.png")

# -------------------------------------------------------------
# 2. SCENE 03: Light-Speed Delay (Radio beam through interstellar space)
# -------------------------------------------------------------
# Topic: Radio signal traveling 24 billion km across the cosmos between Voyager and Earth
print("Building Scene 03: Light-Speed Delay...")
# Base: Heliopause boundary / interstellar plasma wave (scene-02-heliopause.png)
base3 = Image.open("assets/interstellar_space_reel/images/scene-02-heliopause.png").convert("RGBA")

# Let us add subtle focused radio signal wave / data beam connecting the antenna toward distant Earth
beam_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
draw_b = ImageDraw.Draw(beam_layer)

# Antenna feed center is around (430, 990)
# Earth is towards bottom right (900, 1800)
# Draw focused laser/radio communication carrier line with soft glow pulses
draw_b.line([(435, 990), (950, 1850)], fill=(255, 230, 150, 90), width=3)
draw_b.line([(435, 990), (950, 1850)], fill=(255, 255, 255, 180), width=1)
# Pulsing concentric wavefronts
for dist in [120, 260, 420, 600, 800]:
    x_c = int(435 + (950 - 435) * (dist / 1100.0))
    y_c = int(990 + (1850 - 990) * (dist / 1100.0))
    draw_b.ellipse([x_c - 15, y_c - 15, x_c + 15, y_c + 15], outline=(200, 230, 255, 120), width=2)

beam_glow = beam_layer.filter(ImageFilter.GaussianBlur(4))
s3 = Image.alpha_composite(base3, beam_glow)
s3 = Image.alpha_composite(s3, beam_layer)
s3 = apply_logo(s3)
s3.save(os.path.join(out_dir, "scene-03-light-speed-delay.png"), quality=98)
print("Saved scene-03-light-speed-delay.png")

# -------------------------------------------------------------
# 3. SCENE 04: 22-Watt Transmitter & High-Gain Antenna
# -------------------------------------------------------------
# Topic: Close-up of Voyager's 3.7m dish antenna & low-power radio transmitter
print("Building Scene 04: 22-Watt Transmitter...")
# Base: High-res clean 3D scientific model of Voyager 1 (pale_blue_dot_universe_reel/scene-03-voyager-at-edge.png)
base4 = Image.open("assets/pale_blue_dot_universe_reel/scene-03-voyager-at-edge.png").convert("RGBA")

# Grade and composite with rich dark space and subtle stellar illumination
enh = ImageEnhance.Contrast(base4)
s4 = enh.enhance(1.15)
# Add subtle vignette at bottom for subtitle-safe area
vig4 = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
v_draw4 = ImageDraw.Draw(vig4)
for y in range(TARGET_HEIGHT - 400, TARGET_HEIGHT):
    alpha = int(180 * ((y - (TARGET_HEIGHT - 400)) / 400.0) ** 1.5)
    v_draw4.line([(0, y), (TARGET_WIDTH, y)], fill=(2, 4, 10, alpha))
s4 = Image.alpha_composite(s4, vig4)
s4 = apply_logo(s4)
s4.save(os.path.join(out_dir, "scene-04-refrigerator-bulb-power.png"), quality=98)
print("Saved scene-04-refrigerator-bulb-power.png")

# -------------------------------------------------------------
# 4. SCENE 05: Attowatt Signal Reaching Earth
# -------------------------------------------------------------
# Topic: Signal arriving at Earth after crossing 24 billion km, faint attowatt power
print("Building Scene 05: Attowatt Signal Reaching Earth...")
# Base: Stunning Earth from orbit with satellites and starry background (solar_storm_documentary/scene_12_modern_earth_orbit.png)
base5_raw = Image.open("assets/solar_storm_documentary/scene_12_modern_earth_orbit.png").convert("RGB")
# Crop center 1080x1920
# Original is 1920x1080 horizontal! Let us compose native vertical:
# Resize base5 to height 1920
h5 = 1920
w5 = int(base5_raw.width * (h5 / base5_raw.height))
base5_scaled = base5_raw.resize((w5, h5), Image.Resampling.LANCZOS)
# Center crop width to 1080
left5 = (w5 - TARGET_WIDTH) // 2
s5_crop = base5_scaled.crop((left5, 0, left5 + TARGET_WIDTH, TARGET_HEIGHT)).convert("RGBA")

# Add incoming radio carrier wave from deep space (upper left) towards Earth limb
signal_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(signal_layer)
# Faint incoming pulses
s_draw.line([(0, 200), (450, 750)], fill=(120, 200, 255, 70), width=2)
for r in [60, 140, 220, 310, 420]:
    s_draw.ellipse([450 - r, 750 - r, 450 + r, 750 + r], outline=(100, 180, 255, 50), width=1)

s5_glow = signal_layer.filter(ImageFilter.GaussianBlur(3))
s5 = Image.alpha_composite(s5_crop, s5_glow)
s5 = Image.alpha_composite(s5, signal_layer)
s5 = apply_logo(s5)
s5.save(os.path.join(out_dir, "scene-05-attowatt-signal-earth.png"), quality=98)
print("Saved scene-05-attowatt-signal-earth.png")

# -------------------------------------------------------------
# 5. SCENE 06: Deep Space Network (DSN 70m Antenna at Night)
# -------------------------------------------------------------
# Topic: 70-meter dish antenna receiving Voyager signal under night sky
print("Building Scene 06: DSN 70m Dishes...")
# Raw photo: Goldstone 70-meter antenna at night (assets/voyager1_reel/raw/goldstone_70m.jpg)
dsn_raw = Image.open("assets/voyager1_reel/raw/goldstone_70m.jpg").convert("RGB")
# Compose vertical 1080x1920:
# The dish is on the upper-right facing up. Let's crop and frame it heroically:
# Scale dsn_raw to height 1920
h6 = 1920
w6 = int(dsn_raw.width * (h6 / dsn_raw.height))
dsn_scaled = dsn_raw.resize((w6, h6), Image.Resampling.LANCZOS)
# Crop to focus on the dish and night sky
left6 = int(w6 * 0.38)
if left6 + TARGET_WIDTH > w6:
    left6 = w6 - TARGET_WIDTH
s6 = dsn_scaled.crop((left6, 0, left6 + TARGET_WIDTH, TARGET_HEIGHT)).convert("RGBA")

# Enhance contrast and deep navy tint to match Master DNA
enh6 = ImageEnhance.Contrast(s6)
s6 = enh6.enhance(1.1)
s6 = apply_logo(s6)
s6.save(os.path.join(out_dir, "scene-06-dsn-giant-dishes.png"), quality=98)
print("Saved scene-06-dsn-giant-dishes.png")

# -------------------------------------------------------------
# 6. SCENE 07: The Golden Record
# -------------------------------------------------------------
# Topic: The Golden Record on Voyager 1 carrying humanity's greeting
print("Building Scene 07: The Golden Record...")
# Raw photo: High-res NASA official Golden Record cover (assets/voyager1_reel/raw/golden_record_cover.jpg)
gr_raw = Image.open("assets/voyager1_reel/raw/golden_record_cover.jpg").convert("RGB")

# Place Golden Record onto deep cosmic starfield (using scene-08-cosmic-cradle.png or deep starry cosmos)
bg7 = Image.open("assets/eris_reel/images/scene-08-mamase-frontier-payoff.png").convert("RGBA")
# Dim background so Golden Record pops out
dark_bg = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (4, 6, 12, 190))
bg7 = Image.alpha_composite(bg7, dark_bg)

# Prepare Golden Record: circular cutout, diameter 820px, centered
gr_size = 840
gr_resized = gr_raw.resize((gr_size, gr_size), Image.Resampling.LANCZOS)

# Create soft circular mask with slight metallic rim glow
gr_mask = Image.new("L", (gr_size, gr_size), 0)
draw_grm = ImageDraw.Draw(gr_mask)
draw_grm.ellipse([10, 10, gr_size - 10, gr_size - 10], fill=255)

# Glow shadow
gr_x = (TARGET_WIDTH - gr_size) // 2
gr_y = 480
gr_shadow = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
draw_grs = ImageDraw.Draw(gr_shadow)
draw_grs.ellipse([gr_x - 30, gr_y - 30, gr_x + gr_size + 30, gr_y + gr_size + 30], fill=(215, 160, 40, 70))
gr_shadow = gr_shadow.filter(ImageFilter.GaussianBlur(35))

s7 = Image.alpha_composite(bg7, gr_shadow)
s7.paste(gr_resized, (gr_x, gr_y), mask=gr_mask)
s7 = apply_logo(s7)
s7.save(os.path.join(out_dir, "scene-07-golden-record-humanity.png"), quality=98)
print("Saved scene-07-golden-record-humanity.png")

# -------------------------------------------------------------
# 7. SCENE 08: Silent Voyage in the Milky Way
# -------------------------------------------------------------
# Topic: Voyager 1 drifting forever through the stars of the Milky Way galaxy
print("Building Scene 08: Silent Voyage in the Milky Way...")
# Base: Gorgeous cosmic nebula and star cradle (assets/interstellar_space_reel/images/scene-08-cosmic-cradle.png)
base8 = Image.open("assets/interstellar_space_reel/images/scene-08-cosmic-cradle.png").convert("RGBA")

# Composite Voyager 1 silhouette/craft moving toward distant stars
voyager_model_raw = Image.open("assets/voyager1_reel/raw/voyager_model.png").convert("RGBA")
# Voyager craft scale in distance (width ~420px)
v_scale_w = 420
v_scale_h = int(voyager_model_raw.height * (v_scale_w / voyager_model_raw.width))
v_scaled = voyager_model_raw.resize((v_scale_w, v_scale_h), Image.Resampling.LANCZOS)

# Darken and tint Voyager to match deep interstellar lighting
v_enh = ImageEnhance.Brightness(v_scaled)
v_scaled = v_enh.enhance(0.7)

# Paste Voyager at midground (x=160, y=720) heading into the stellar core
s8 = base8.copy()
s8.paste(v_scaled, (160, 720), mask=v_scaled.split()[3])
s8 = apply_logo(s8)
s8.save(os.path.join(out_dir, "scene-08-silent-voyage-milkyway.png"), quality=98)
print("Saved scene-08-silent-voyage-milkyway.png")

print("\n=== ALL SCENES BUILT SUCCESSFULLY! ===")
