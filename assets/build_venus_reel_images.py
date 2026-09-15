import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

out_dir = "assets/venus_bright_evening_reel/images"
os.makedirs(out_dir, exist_ok=True)

# -------------------------------------------------------------
# Logo Preparation
# -------------------------------------------------------------
logo_raw = Image.open("assets/branding/mamase/logo.png").convert("RGBA")
logo_size = 205
logo = logo_raw.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
logo_x = TARGET_WIDTH - logo_size - 36  # 839
logo_y = 36

# Logo shadow template
l_shadow = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
l_shadow.paste(Image.new("RGBA", (logo_size, logo_size), (0, 0, 0, 220)), (logo_x, logo_y + 3), mask=logo.split()[3])
l_shadow = l_shadow.filter(ImageFilter.GaussianBlur(12))

def apply_logo(im):
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    im = Image.alpha_composite(im, l_shadow)
    im.paste(logo, (logo_x, logo_y), mask=logo)
    return im.convert("RGB")

# -------------------------------------------------------------
# 1. SCENE 01: KEY ART COMPOSITE
# -------------------------------------------------------------
print("Rendering Scene 01 Key Art...")
bg_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/venus_s1_bg_1789187102232.jpg"
bg1 = Image.open(bg_path).convert("RGBA").resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

# Subtle vignette / bottom darkening
vignette = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
for y in range(TARGET_HEIGHT - 650, TARGET_HEIGHT):
    alpha = int(190 * ((y - (TARGET_HEIGHT - 650)) / 650.0) ** 1.5)
    v_draw.line([(0, y), (TARGET_WIDTH, y)], fill=(4, 6, 12, alpha))
for y in range(0, 400):
    alpha = int(140 * ((400 - y) / 400.0) ** 1.5)
    v_draw.line([(0, y), (TARGET_WIDTH, y)], fill=(3, 5, 10, alpha))
bg1 = Image.alpha_composite(bg1, vignette)

# Presenter
presenter_path = "assets/characters/mamase-presenter-cutout.png"
orig_p = Image.open(presenter_path).convert("RGBA")

enhancer = ImageEnhance.Brightness(orig_p)
presenter = enhancer.enhance(0.96)
tint = Image.new("RGBA", presenter.size, (200, 150, 90, 255))
p_alpha = presenter.split()[3]
presenter_tinted = Image.blend(presenter, tint, 0.08)
presenter_tinted.putalpha(p_alpha)
presenter = presenter_tinted

p_height = int(TARGET_HEIGHT * 0.55)
p_ratio = presenter.width / presenter.height
p_width = int(p_height * p_ratio)
presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)

paste_x = TARGET_WIDTH - p_width - 20
paste_y = TARGET_HEIGHT - p_height

p_shadow = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
p_shadow.paste(Image.new("RGBA", (p_width, p_height), (0, 0, 0, 180)), (paste_x - 15, paste_y + 10), mask=presenter.split()[3])
p_shadow = p_shadow.filter(ImageFilter.GaussianBlur(25))
bg1 = Image.alpha_composite(bg1, p_shadow)
bg1.paste(presenter, (paste_x, paste_y), mask=presenter)

# Typography: Title "VENUS" and Hook "ดาวสว่างลึกลับหัวค่ำ?"
font_chonburi_title = ImageFont.truetype("assets/fonts/Chonburi.ttf", 150)
font_chonburi_hook = ImageFont.truetype("assets/fonts/Chonburi.ttf", 62)

title_text = "VENUS"
hook_text = "ดาวสว่างลึกลับหัวค่ำ?"

dummy_draw = ImageDraw.Draw(bg1)
t_bbox = dummy_draw.textbbox((0, 0), title_text, font=font_chonburi_title)
t_w = t_bbox[2] - t_bbox[0]
t_h = t_bbox[3] - t_bbox[1]

h_bbox = dummy_draw.textbbox((0, 0), hook_text, font=font_chonburi_hook)
h_w = h_bbox[2] - h_bbox[0]
h_h = h_bbox[3] - h_bbox[1]

# Position centered in top-left safe area
pos_x_title = 120
pos_y_title = 260
pos_x_hook = 120
pos_y_hook = pos_y_title + 165

# Lens flare accent under title
flare_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
f_draw = ImageDraw.Draw(flare_layer)
f_y = pos_y_title + int(t_h * 0.95)
f_draw.line([(pos_x_title - 40, f_y), (pos_x_title + t_w + 60, f_y)], fill=(255, 170, 30, 240), width=6)
f_draw.line([(pos_x_title - 10, f_y), (pos_x_title + t_w + 20, f_y)], fill=(255, 245, 180, 255), width=2)
flare_layer = flare_layer.filter(ImageFilter.GaussianBlur(6))
bg1 = Image.alpha_composite(bg1, flare_layer)

# Radial warm glow behind title
glow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
g_draw = ImageDraw.Draw(glow_layer)
g_draw.text((pos_x_title, pos_y_title), title_text, font=font_chonburi_title, fill=(255, 120, 20, 255))
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(30))
bg1 = Image.alpha_composite(bg1, glow_layer)

# Shadow
shadow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_layer)
s_draw.text((pos_x_title + 8, pos_y_title + 10), title_text, font=font_chonburi_title, fill=(0, 0, 0, 255))
s_draw.text((pos_x_hook + 5, pos_y_hook + 6), hook_text, font=font_chonburi_hook, fill=(0, 0, 0, 255))
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(10))
bg1 = Image.alpha_composite(bg1, shadow_layer)
bg1 = Image.alpha_composite(bg1, shadow_layer)

# Dark stroke for Title
stroke_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
st_draw = ImageDraw.Draw(stroke_layer)
st_draw.text((pos_x_title, pos_y_title), title_text, font=font_chonburi_title, fill=(15, 8, 2, 255), stroke_width=9)
bg1 = Image.alpha_composite(bg1, stroke_layer)

# Gold Foil Fill for Title
mask_title = Image.new("L", (TARGET_WIDTH, TARGET_HEIGHT), 0)
m_draw = ImageDraw.Draw(mask_title)
m_draw.text((pos_x_title, pos_y_title), title_text, fill=255, font=font_chonburi_title)

gold_canvas = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
gc_draw = ImageDraw.Draw(gold_canvas)

np.random.seed(42)
noise = np.random.normal(0, 20, (TARGET_HEIGHT, TARGET_WIDTH))

for y in range(pos_y_title - 15, pos_y_title + 175):
    rel = (y - pos_y_title) / 140.0
    rel = max(0.0, min(1.0, rel))
    if rel < 0.25:
        r, g, b = 255, int(250 - (rel / 0.25) * 35), int(220 - (rel / 0.25) * 150)
    elif rel < 0.70:
        sub = (rel - 0.25) / 0.45
        r, g, b = int(255 - sub * 10), int(215 - sub * 65), int(70 - sub * 50)
    else:
        sub = (rel - 0.70) / 0.30
        r, g, b = int(245 - sub * 60), int(150 - sub * 75), int(20 - sub * 15)
    gc_draw.line([(pos_x_title - 40, y), (pos_x_title + t_w + 40, y)], fill=(r, g, b, 255))

gold_arr = np.array(gold_canvas).astype(np.int16)
for c in range(3):
    gold_arr[:, :, c] = np.clip(gold_arr[:, :, c] + noise * 0.5, 0, 255)
gold_canvas = Image.fromarray(gold_arr.astype(np.uint8))

top_hl = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
th_draw = ImageDraw.Draw(top_hl)
th_draw.text((pos_x_title, pos_y_title - 2), title_text, font=font_chonburi_title, fill=(255, 255, 230, 180), stroke_width=2)
gold_canvas.paste(top_hl, (0, 0), mask=top_hl)
bg1.paste(gold_canvas, (0, 0), mask=mask_title)

# Hook Text
hook_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
h_draw = ImageDraw.Draw(hook_layer)
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_chonburi_hook, fill=(10, 5, 2, 255), stroke_width=5)
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_chonburi_hook, fill=(255, 250, 240, 255))
bg1.paste(hook_layer, (0, 0), mask=hook_layer)

# Apply Mamase Logo top-right
s01_final = apply_logo(bg1)
s01_final.save(os.path.join(out_dir, "scene-01-hook.png"), "PNG")
print("Scene 01 saved.")

# -------------------------------------------------------------
# 2. SCENES 02 to 05: Direct Generative Masters + Logo
# -------------------------------------------------------------
direct_scenes = {
    "scene-02-bright-star.png": "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/venus_s2_bright_star_1789187121230.jpg",
    "scene-03-albedo-clouds.png": "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/venus_s3_albedo_clouds_1789187137962.jpg",
    "scene-04-peak-brilliancy.png": "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/venus_s4_peak_brilliancy_1789187158553.jpg",
    "scene-05-lunar-occultation.png": "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/venus_s5_lunar_occultation_1789187180095.jpg",
}

for name, path in direct_scenes.items():
    print(f"Processing {name}...")
    im = Image.open(path).convert("RGBA").resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    res = apply_logo(im)
    res.save(os.path.join(out_dir, name), "PNG")
    print(f"Saved {name}.")

# -------------------------------------------------------------
# 3. SCENE 06: Swimming Moon & Venus Setting (ESO Master)
# -------------------------------------------------------------
print("Processing Scene 06 (Swimming Moon & Venus at Horizon)...")
im6 = Image.open("/tmp/venus_swimming_moon.jpg").convert("RGBA")
# Target 1080x1920 (aspect ratio 9:16 = 0.5625)
# Current size: 2481x3723 (ratio 0.666)
# Crop width slightly to get exact 9:16 framing centered
target_w = int(im6.height * 9.0 / 16.0)  # 3723 * 9 / 16 = 2094
crop_x = (im6.width - target_w) // 2
im6_cropped = im6.crop((crop_x, 0, crop_x + target_w, im6.height))
im6_resized = im6_cropped.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s06_final = apply_logo(im6_resized)
s06_final.save(os.path.join(out_dir, "scene-06-setting-horizon.png"), "PNG")
print("Saved Scene 06.")

# -------------------------------------------------------------
# 4. SCENE 07: ESO Auxiliary Telescope at Sunset
# -------------------------------------------------------------
print("Processing Scene 07 (Observatory Sunset)...")
im7 = Image.open("/tmp/eso_auxtel.jpg").convert("RGBA")
# Current: 1920x1280 (landscape 3:2)
# Crop vertical 9:16 focusing on the telescope and glowing orange horizon
target_w = int(im7.height * 9.0 / 16.0) # 1280 * 9 / 16 = 720
crop_x = 550 # capture the sleek telescope structure and sunset sky
im7_cropped = im7.crop((crop_x, 0, crop_x + target_w, im7.height))
im7_resized = im7_cropped.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s07_final = apply_logo(im7_resized)
s07_final.save(os.path.join(out_dir, "scene-07-observatory-viewpoint.png"), "PNG")
print("Saved Scene 07.")

# -------------------------------------------------------------
# 5. SCENE 08: Earth & Venus Cosmic View
# -------------------------------------------------------------
print("Processing Scene 08 (Earth & Venus Cosmic Rhythms)...")
im8 = Image.open("assets/venus-day-longer-than-year-reel/images/scene-09-cosmic-rhythms.png").convert("RGBA")
im8 = im8.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s08_final = apply_logo(im8)
s08_final.save(os.path.join(out_dir, "scene-08-earth-venus-cosmic.png"), "PNG")
print("Saved Scene 08.")

# -------------------------------------------------------------
# 6. SCENE 09: Canonical Outro (NO second logo, NO subtitles)
# -------------------------------------------------------------
print("Processing Scene 09 (Canonical Outro)...")
im9 = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGB")
im9_resized = im9.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
im9_resized.save(os.path.join(out_dir, "scene-09-mamase-outro.png"), "PNG")
print("Saved Scene 09.")

print("\nALL 9 SCENES PRODUCED SUCCESSFULLY 100%!")
