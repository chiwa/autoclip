import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

out_dir = "assets/planet_nine_reel/images"
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
# 1. SCENE 01: Key Art (Caltech Planet Nine + Presenter + Typography)
# -------------------------------------------------------------
print("Rendering Scene 01 Key Art...")
# Caltech plain is 1920x1280.
# Let's crop vertical: Planet Nine on left/center, distant sun at top right.
p9_raw = Image.open("/tmp/p9_caltech_plain.png").convert("RGBA")
# For 1080x1920, target_w = int(p9_raw.height * 9.0 / 16.0) = 1280 * 9 / 16 = 720
# Let's crop from x=200 to x=920, or let's place Planet Nine prominently in upper center
target_w = int(p9_raw.height * 9.0 / 16.0) # 720
crop_x = 220
bg1 = p9_raw.crop((crop_x, 0, crop_x + target_w, p9_raw.height)).resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

# Subtle vignette / bottom & top darkening
vignette = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
for y in range(TARGET_HEIGHT - 650, TARGET_HEIGHT):
    alpha = int(200 * ((y - (TARGET_HEIGHT - 650)) / 650.0) ** 1.5)
    v_draw.line([(0, y), (TARGET_WIDTH, y)], fill=(2, 4, 10, alpha))
for y in range(0, 420):
    alpha = int(140 * ((420 - y) / 420.0) ** 1.5)
    v_draw.line([(0, y), (TARGET_WIDTH, y)], fill=(2, 4, 8, alpha))
bg1 = Image.alpha_composite(bg1, vignette)

# Presenter
presenter_path = "assets/characters/mamase-presenter-cutout.png"
orig_p = Image.open(presenter_path).convert("RGBA")

enhancer = ImageEnhance.Brightness(orig_p)
presenter = enhancer.enhance(0.92)
tint = Image.new("RGBA", presenter.size, (100, 140, 200, 255))
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
p_shadow.paste(Image.new("RGBA", (p_width, p_height), (0, 0, 0, 190)), (paste_x - 15, paste_y + 10), mask=presenter.split()[3])
p_shadow = p_shadow.filter(ImageFilter.GaussianBlur(25))
bg1 = Image.alpha_composite(bg1, p_shadow)
bg1.paste(presenter, (paste_x, paste_y), mask=presenter)

# Typography: Title "PLANET NINE" and Hook "มีดาวเคราะห์ซ่อนอยู่จริงไหม?"
font_chonburi_title = ImageFont.truetype("assets/fonts/Chonburi.ttf", 110)
font_chonburi_hook = ImageFont.truetype("assets/fonts/Chonburi.ttf", 56)

title_text = "PLANET NINE"
hook_text = "มีดาวเคราะห์ซ่อนอยู่จริงไหม?"

dummy_draw = ImageDraw.Draw(bg1)
t_bbox = dummy_draw.textbbox((0, 0), title_text, font=font_chonburi_title)
t_w = t_bbox[2] - t_bbox[0]
t_h = t_bbox[3] - t_bbox[1]

h_bbox = dummy_draw.textbbox((0, 0), hook_text, font=font_chonburi_hook)
h_w = h_bbox[2] - h_bbox[0]
h_h = h_bbox[3] - h_bbox[1]

pos_x_title = 100
pos_y_title = 270
pos_x_hook = 100
pos_y_hook = pos_y_title + 140

# Lens flare accent under title
flare_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
f_draw = ImageDraw.Draw(flare_layer)
f_y = pos_y_title + int(t_h * 0.95)
f_draw.line([(pos_x_title - 30, f_y), (pos_x_title + t_w + 50, f_y)], fill=(255, 170, 30, 240), width=6)
f_draw.line([(pos_x_title - 5, f_y), (pos_x_title + t_w + 20, f_y)], fill=(255, 245, 180, 255), width=2)
flare_layer = flare_layer.filter(ImageFilter.GaussianBlur(6))
bg1 = Image.alpha_composite(bg1, flare_layer)

# Radial warm glow behind title
glow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
g_draw = ImageDraw.Draw(glow_layer)
g_draw.text((pos_x_title, pos_y_title), title_text, font=font_chonburi_title, fill=(255, 130, 30, 255))
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
st_draw.text((pos_x_title, pos_y_title), title_text, font=font_chonburi_title, fill=(15, 8, 2, 255), stroke_width=8)
bg1 = Image.alpha_composite(bg1, stroke_layer)

# Gold Foil Fill for Title
mask_title = Image.new("L", (TARGET_WIDTH, TARGET_HEIGHT), 0)
m_draw = ImageDraw.Draw(mask_title)
m_draw.text((pos_x_title, pos_y_title), title_text, fill=255, font=font_chonburi_title)

gold_canvas = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
gc_draw = ImageDraw.Draw(gold_canvas)

np.random.seed(99)
noise = np.random.normal(0, 20, (TARGET_HEIGHT, TARGET_WIDTH))

for y in range(pos_y_title - 15, pos_y_title + 140):
    rel = (y - pos_y_title) / 110.0
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

# Hook Text
hook_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
h_draw = ImageDraw.Draw(hook_layer)
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_chonburi_hook, fill=(10, 5, 2, 255), stroke_width=5)
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_chonburi_hook, fill=(255, 250, 240, 255))
bg1.paste(hook_layer, (0, 0), mask=hook_layer)

s01_final = apply_logo(bg1)
s01_final.save(os.path.join(out_dir, "scene-01-hook.png"), "PNG")
print("Scene 01 saved.")

# -------------------------------------------------------------
# 2. SCENE 02: Clustered Orbits (5850x3900 master)
# -------------------------------------------------------------
print("Processing Scene 02 (Clustered Orbits)...")
im2 = Image.open("/tmp/p9_orbits_unannotated.png").convert("RGBA")
# Crop vertical around the cluster
# 3900 * 9 / 16 = 2193
target_w2 = int(im2.height * 9.0 / 16.0)
crop_x2 = (im2.width - target_w2) // 2
im2_cropped = im2.crop((crop_x2, 0, crop_x2 + target_w2, im2.height)).resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s02_final = apply_logo(im2_cropped)
s02_final.save(os.path.join(out_dir, "scene-02-strange-orbits.png"), "PNG")
print("Scene 02 saved.")

# -------------------------------------------------------------
# 3. SCENE 03: The Massive Sculptor (Hypothetical Planet Nine 4K)
# -------------------------------------------------------------
print("Processing Scene 03 (Massive Sculptor)...")
im3 = Image.open("/tmp/p9_hypothetical_4k.png").convert("RGBA")
# 3840x2160 landscape. Crop vertical 9:16 focusing on the crescent planet and distant sun
target_w3 = int(im3.height * 9.0 / 16.0) # 2160 * 9 / 16 = 1215
crop_x3 = 1300 # frames the glowing crescent of the planet and space
im3_cropped = im3.crop((crop_x3, 0, crop_x3 + target_w3, im3.height)).resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s03_final = apply_logo(im3_cropped)
s03_final.save(os.path.join(out_dir, "scene-03-massive-sculptor.png"), "PNG")
print("Scene 03 saved.")

# -------------------------------------------------------------
# 4. SCENE 04: Scale & Distance (400-800 AU)
# -------------------------------------------------------------
print("Processing Scene 04 (Scale & Distance)...")
im4 = Image.open("/tmp/p9_oort_scale.jpg").convert("RGBA")
# 4400x4409 square. Focus on bottom right panel (Post-Kuiper belt & Planet 9) and top right
# Let's crop the right half which has Planet 9 orbit and outer solar system
# 4409 * 9 / 16 = 2479
target_w4 = int(im4.height * 9.0 / 16.0)
crop_x4 = im4.width - target_w4 # right side
im4_cropped = im4.crop((crop_x4, 0, crop_x4 + target_w4, im4.height)).resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s04_final = apply_logo(im4_cropped)
s04_final.save(os.path.join(out_dir, "scene-04-distance-scale.png"), "PNG")
print("Scene 04 saved.")

# -------------------------------------------------------------
# 5. SCENE 05: Why Unseen? (JWST Space Telescope searching)
# -------------------------------------------------------------
print("Processing Scene 05 (Space Telescope)...")
im5 = Image.open("assets/james_webb_time_machine_reel/scene-05-jwst-observatory.png").convert("RGBA")
im5 = im5.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s05_final = apply_logo(im5)
s05_final.save(os.path.join(out_dir, "scene-05-why-unseen.png"), "PNG")
print("Scene 05 saved.")

# -------------------------------------------------------------
# 6. SCENE 06: Evidence vs Hypothesis (Caltech Distant Sun & Orbits)
# -------------------------------------------------------------
print("Processing Scene 06 (Evidence vs Hypothesis)...")
im6 = Image.open("/tmp/p9_caltech_plain.png").convert("RGBA")
# Crop vertical around the distant sun with the planetary orbits
target_w6 = int(im6.height * 9.0 / 16.0) # 720
crop_x6 = 1100 # focuses on the distant glowing sun and orbital ellipses in Milky Way
im6_cropped = im6.crop((crop_x6, 0, crop_x6 + target_w6, im6.height)).resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s06_final = apply_logo(im6_cropped)
s06_final.save(os.path.join(out_dir, "scene-06-evidence-vs-hypothesis.png"), "PNG")
print("Scene 06 saved.")

# -------------------------------------------------------------
# 7. SCENE 07: Vera C. Rubin Observatory at Night
# -------------------------------------------------------------
print("Processing Scene 07 (Vera Rubin Observatory)...")
im7 = Image.open("/tmp/rubin_night_official.jpg").convert("RGBA")
# 6048x4024. Crop vertical focusing on the white observatory dome on the mountain summit under the starry sky
target_w7 = int(im7.height * 9.0 / 16.0) # 4024 * 9 / 16 = 2263
crop_x7 = 850 # captures the dome and starry sky, avoiding the tall red tower on the far right
im7_cropped = im7.crop((crop_x7, 0, crop_x7 + target_w7, im7.height)).resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s07_final = apply_logo(im7_cropped)
s07_final.save(os.path.join(out_dir, "scene-07-vera-rubin-hunt.png"), "PNG")
print("Scene 07 saved.")

# -------------------------------------------------------------
# 8. SCENE 08: Cosmic Frontier Payoff
# -------------------------------------------------------------
print("Processing Scene 08 (Cosmic Frontier)...")
im8 = Image.open("assets/james_webb_time_machine_reel/scene-08-cosmic-dawn.png").convert("RGBA")
im8 = im8.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s08_final = apply_logo(im8)
s08_final.save(os.path.join(out_dir, "scene-08-cosmic-frontier.png"), "PNG")
print("Scene 08 saved.")

# -------------------------------------------------------------
# 9. SCENE 09: Canonical Outro
# -------------------------------------------------------------
print("Processing Scene 09 (Canonical Outro)...")
im9 = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGB")
im9_resized = im9.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
im9_resized.save(os.path.join(out_dir, "scene-09-mamase-outro.png"), "PNG")
print("Scene 09 saved.")

print("\nALL 9 SCENES CREATED SUCCESSFULLY!")
