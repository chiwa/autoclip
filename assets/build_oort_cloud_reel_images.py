import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

out_dir = "assets/oort_cloud_reel/images"
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

# -------------------------------------------------------------
# 1. SCENE 01: Hero Key Art
# -------------------------------------------------------------
print("Rendering Scene 01 Hero Key Art...")
bg1_raw = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/oort_s01_bg_1789203655851.jpg").convert("RGBA")
bg1 = bg1_raw.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

# Vignette for typography & presenter
vignette = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
for y in range(TARGET_HEIGHT - 650, TARGET_HEIGHT):
    alpha = int(210 * ((y - (TARGET_HEIGHT - 650)) / 650.0) ** 1.5)
    v_draw.line([(0, y), (TARGET_WIDTH, y)], fill=(2, 4, 10, alpha))
for y in range(0, 440):
    alpha = int(150 * ((440 - y) / 440.0) ** 1.5)
    v_draw.line([(0, y), (TARGET_WIDTH, y)], fill=(2, 4, 8, alpha))
bg1 = Image.alpha_composite(bg1, vignette)

# Presenter
presenter_path = "assets/characters/mamase-presenter-cutout.png"
orig_p = Image.open(presenter_path).convert("RGBA")

enhancer = ImageEnhance.Brightness(orig_p)
presenter = enhancer.enhance(0.92)
tint = Image.new("RGBA", presenter.size, (110, 140, 220, 255))
p_alpha = presenter.split()[3]
presenter_tinted = Image.blend(presenter, tint, 0.08)
presenter_tinted.putalpha(p_alpha)
presenter = presenter_tinted

p_height = int(TARGET_HEIGHT * 0.54)
p_ratio = presenter.width / presenter.height
p_width = int(p_height * p_ratio)
presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)

paste_x = TARGET_WIDTH - p_width - 15
paste_y = TARGET_HEIGHT - p_height

p_shadow = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
p_shadow.paste(Image.new("RGBA", (p_width, p_height), (0, 0, 0, 200)), (paste_x - 15, paste_y + 10), mask=presenter.split()[3])
p_shadow = p_shadow.filter(ImageFilter.GaussianBlur(25))
bg1 = Image.alpha_composite(bg1, p_shadow)
bg1.paste(presenter, (paste_x, paste_y), mask=presenter)

# Typography: Title "OORT CLOUD" and Hook "ขอบจริงของระบบสุริยะ อยู่ตรงไหน?"
font_chonburi_title = ImageFont.truetype("assets/fonts/Chonburi.ttf", 100)
font_chonburi_hook = ImageFont.truetype("assets/fonts/Chonburi.ttf", 52)

title_text = "OORT CLOUD"
hook_text = "ขอบจริงของระบบสุริยะ อยู่ตรงไหน?"

dummy_draw = ImageDraw.Draw(bg1)
t_bbox = dummy_draw.textbbox((0, 0), title_text, font=font_chonburi_title)
t_w = t_bbox[2] - t_bbox[0]
t_h = t_bbox[3] - t_bbox[1]

h_bbox = dummy_draw.textbbox((0, 0), hook_text, font=font_chonburi_hook)
h_w = h_bbox[2] - h_bbox[0]
h_h = h_bbox[3] - h_bbox[1]

pos_x_title = 85
pos_y_title = 270
pos_x_hook = 85
pos_y_hook = pos_y_title + 130

# Lens flare accent under title
flare_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
f_draw = ImageDraw.Draw(flare_layer)
f_y = pos_y_title + int(t_h * 0.95)
f_draw.line([(pos_x_title - 30, f_y), (pos_x_title + t_w + 40, f_y)], fill=(255, 175, 40, 240), width=5)
f_draw.line([(pos_x_title - 5, f_y), (pos_x_title + t_w + 15, f_y)], fill=(255, 245, 190, 255), width=2)
flare_layer = flare_layer.filter(ImageFilter.GaussianBlur(6))
bg1 = Image.alpha_composite(bg1, flare_layer)

# Radial warm glow behind title
glow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
g_draw = ImageDraw.Draw(glow_layer)
g_draw.text((pos_x_title, pos_y_title), title_text, font=font_chonburi_title, fill=(255, 140, 40, 255))
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(28))
bg1 = Image.alpha_composite(bg1, glow_layer)

# Shadow
shadow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_layer)
s_draw.text((pos_x_title + 6, pos_y_title + 8), title_text, font=font_chonburi_title, fill=(0, 0, 0, 255))
s_draw.text((pos_x_hook + 4, pos_y_hook + 5), hook_text, font=font_chonburi_hook, fill=(0, 0, 0, 255))
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(8))
bg1 = Image.alpha_composite(bg1, shadow_layer)
bg1 = Image.alpha_composite(bg1, shadow_layer)

# Dark stroke for Title
stroke_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
st_draw = ImageDraw.Draw(stroke_layer)
st_draw.text((pos_x_title, pos_y_title), title_text, font=font_chonburi_title, fill=(15, 8, 2, 255), stroke_width=6)
bg1 = Image.alpha_composite(bg1, stroke_layer)

# Gold Foil Fill for Title
mask_title = Image.new("L", (TARGET_WIDTH, TARGET_HEIGHT), 0)
m_draw = ImageDraw.Draw(mask_title)
m_draw.text((pos_x_title, pos_y_title), title_text, fill=255, font=font_chonburi_title)

gold_canvas = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
gc_draw = ImageDraw.Draw(gold_canvas)

np.random.seed(77)
noise = np.random.normal(0, 18, (TARGET_HEIGHT, TARGET_WIDTH))

for y in range(pos_y_title - 10, pos_y_title + 120):
    rel = (y - pos_y_title) / 95.0
    rel = max(0.0, min(1.0, rel))
    if rel < 0.25:
        r, g, b = 255, int(250 - (rel / 0.25) * 35), int(220 - (rel / 0.25) * 150)
    elif rel < 0.70:
        sub = (rel - 0.25) / 0.45
        r, g, b = int(255 - sub * 10), int(215 - sub * 65), int(70 - sub * 50)
    else:
        sub = (rel - 0.70) / 0.30
        r, g, b = int(245 - sub * 60), int(150 - sub * 75), int(20 - sub * 15)
    gc_draw.line([(pos_x_title - 30, y), (pos_x_title + t_w + 30, y)], fill=(r, g, b, 255))

gold_arr = np.array(gold_canvas).astype(np.int16)
for c in range(3):
    gold_arr[:, :, c] = np.clip(gold_arr[:, :, c] + noise * 0.5, 0, 255)
gold_canvas = Image.fromarray(gold_arr.astype(np.uint8))

top_hl = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
th_draw = ImageDraw.Draw(top_hl)
th_draw.text((pos_x_title, pos_y_title - 2), title_text, font=font_chonburi_title, fill=(255, 255, 230, 180), stroke_width=2)
gold_canvas.paste(top_hl, (0, 0), mask=top_hl)
bg1.paste(gold_canvas, (0, 0), mask=mask_title)

# Hook Text (Creamy white with dark outline)
hook_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
h_draw = ImageDraw.Draw(hook_layer)
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_chonburi_hook, fill=(8, 5, 2, 255), stroke_width=4)
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_chonburi_hook, fill=(255, 250, 240, 255))
bg1.paste(hook_layer, (0, 0), mask=hook_layer)

s01_final = apply_logo(bg1)
s01_final.save(os.path.join(out_dir, "scene-01-hook.png"), "PNG")
print("Scene 01 saved.")

# -------------------------------------------------------------
# 2. SCENE 02: Heliosphere vs True Boundary
# -------------------------------------------------------------
print("Processing Scene 02...")
im2 = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/oort_s02_heliosphere_bubble_1789203687709.jpg")
im2_fit = im2.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s02_final = apply_logo(im2_fit)
s02_final.save(os.path.join(out_dir, "scene-02-heliosphere-bubble.png"), "PNG")
print("Scene 02 saved.")

# -------------------------------------------------------------
# 3. SCENE 03: Revealing the Oort Cloud (Spherical Shell)
# -------------------------------------------------------------
print("Processing Scene 03...")
im3 = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/oort_s03_spherical_swarm_1789203719939.jpg")
im3_fit = im3.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s03_final = apply_logo(im3_fit)
s03_final.save(os.path.join(out_dir, "scene-03-spherical-swarm.png"), "PNG")
print("Scene 03 saved.")

# -------------------------------------------------------------
# 4. SCENE 04: The Incomprehensible Scale
# -------------------------------------------------------------
print("Processing Scene 04...")
im4 = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/oort_s04_distance_scale_1789203757672.jpg")
im4_fit = im4.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s04_final = apply_logo(im4_fit)
s04_final.save(os.path.join(out_dir, "scene-04-distance-scale.png"), "PNG")
print("Scene 04 saved.")

# -------------------------------------------------------------
# 5. SCENE 05: Voyager Reality Check (Time Scale)
# -------------------------------------------------------------
print("Processing Scene 05...")
im5 = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/oort_s05_voyager_journey_1789203791208.jpg")
im5_fit = im5.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s05_final = apply_logo(im5_fit)
s05_final.save(os.path.join(out_dir, "scene-05-voyager-journey.png"), "PNG")
print("Scene 05 saved.")

# -------------------------------------------------------------
# 6. SCENE 06: Primordial Cosmic Freezer (Cometary Nucleus & Tail)
# -------------------------------------------------------------
print("Processing Scene 06...")
im6 = Image.open("assets/3i_atlas_message_reel/images/scene-09-farewell.png")
im6_fit = im6.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s06_final = apply_logo(im6_fit)
s06_final.save(os.path.join(out_dir, "scene-06-cosmic-freezer.png"), "PNG")
print("Scene 06 saved.")

# -------------------------------------------------------------
# 7. SCENE 07: True Edge of Sun's Gravity (Spacetime Boundary)
# -------------------------------------------------------------
print("Processing Scene 07...")
im7 = Image.open("assets/edge_of_universe_reel/images/scene-07-expanding-spacetime.png")
im7_fit = im7.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s07_final = apply_logo(im7_fit)
s07_final.save(os.path.join(out_dir, "scene-07-gravity-boundary.png"), "PNG")
print("Scene 07 saved.")

# -------------------------------------------------------------
# 8. SCENE 08: Cosmic Horizon Payoff (Home in the Cosmos)
# -------------------------------------------------------------
print("Processing Scene 08...")
im8 = Image.open("assets/edge_of_universe_reel/images/scene-02-cosmic-horizon.png")
im8_fit = im8.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s08_final = apply_logo(im8_fit)
s08_final.save(os.path.join(out_dir, "scene-08-cosmic-home.png"), "PNG")
print("Scene 08 saved.")

# -------------------------------------------------------------
# 9. SCENE 09: Canonical Mamase Outro
# -------------------------------------------------------------
print("Processing Scene 09 (Canonical Outro)...")
outro_raw = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGB")
outro_final = outro_raw.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
outro_final.save(os.path.join(out_dir, "scene-09-mamase-outro.png"), "PNG")
print("Scene 09 saved.")

print("All 9 scenes rendered successfully!")
