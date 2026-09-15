import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

out_dir = "assets/eris_reel/images"
os.makedirs(out_dir, exist_ok=True)

# -------------------------------------------------------------
# Logo Setup (Official Mamase circular logo at 205x205, pos: 839, 36)
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

def cover_crop(im, target_w, target_h):
    w, h = im.size
    scale = max(target_w / w, target_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return im.crop((left, top, left + target_w, top + target_h))

# -------------------------------------------------------------
# 1. SCENE 01: Hero Key Art
# -------------------------------------------------------------
print("Building Scene 01: Hero Key Art...")
bg1_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/eris_keyart_bg_1789214528021.jpg"
bg1_raw = Image.open(bg1_path).convert("RGBA")
bg1 = cover_crop(bg1_raw, TARGET_WIDTH, TARGET_HEIGHT)

# Vignette for typography & presenter
vignette = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
for y in range(TARGET_HEIGHT - 650, TARGET_HEIGHT):
    alpha = int(210 * ((y - (TARGET_HEIGHT - 650)) / 650.0) ** 1.5)
    v_draw.line([(0, y), (TARGET_WIDTH, y)], fill=(2, 4, 10, alpha))
for y in range(0, 480):
    alpha = int(140 * ((480 - y) / 480.0) ** 1.5)
    v_draw.line([(0, y), (TARGET_WIDTH, y)], fill=(2, 4, 10, alpha))
bg1 = Image.alpha_composite(bg1, vignette)

# Presenter Cutout
presenter_path = "assets/characters/mamase-presenter-cutout.png"
orig_p = Image.open(presenter_path).convert("RGBA")

# Adjust lighting: cool blue-white ambient fill light from icy Eris
enhancer = ImageEnhance.Brightness(orig_p)
presenter = enhancer.enhance(0.95)
tint = Image.new("RGBA", presenter.size, (180, 215, 255, 255))
p_alpha = presenter.split()[3]
presenter_tinted = Image.blend(presenter, tint, 0.06)
presenter_tinted.putalpha(p_alpha)
presenter = presenter_tinted

p_height = int(TARGET_HEIGHT * 0.53)
p_ratio = presenter.width / presenter.height
p_width = int(p_height * p_ratio)
presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)

paste_x = TARGET_WIDTH - p_width - 15
paste_y = TARGET_HEIGHT - p_height

p_shadow = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
p_shadow.paste(Image.new("RGBA", (p_width, p_height), (0, 0, 0, 210)), (paste_x - 15, paste_y + 10), mask=presenter.split()[3])
p_shadow = p_shadow.filter(ImageFilter.GaussianBlur(25))
bg1 = Image.alpha_composite(bg1, p_shadow)
bg1.paste(presenter, (paste_x, paste_y), mask=presenter)

# Typography
font_chonburi_title = ImageFont.truetype("assets/fonts/Chonburi.ttf", 104)
font_chonburi_hook = ImageFont.truetype("assets/fonts/Chonburi.ttf", 46)
font_badge = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 32)

title_text = "ERIS"
hook_line1 = "โลกที่บรรยากาศ"
hook_line2 = "แข็งตัวตกลงบนพื้น"
badge_text = "“ผู้เปลี่ยนนิยามดาวเคราะห์”"

pos_x = 75
pos_y_badge = 240

# Draw Badge: "“ผู้เปลี่ยนนิยามดาวเคราะห์”"
dummy_draw = ImageDraw.Draw(bg1)
b_bbox = dummy_draw.textbbox((0, 0), badge_text, font=font_badge)
b_w = b_bbox[2] - b_bbox[0]
b_h = b_bbox[3] - b_bbox[1]
b_pad_x = 24
b_pad_y = 10

badge_bg = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
bb_draw = ImageDraw.Draw(badge_bg)
bb_rect = [pos_x, pos_y_badge, pos_x + b_w + b_pad_x * 2, pos_y_badge + b_h + b_pad_y * 2]
bb_draw.rounded_rectangle(bb_rect, radius=12, fill=(30, 70, 140, 220), outline=(120, 200, 255, 255), width=2)
bg1 = Image.alpha_composite(bg1, badge_bg)

b_draw = ImageDraw.Draw(bg1)
b_draw.text((pos_x + b_pad_x, pos_y_badge + b_pad_y - 2), badge_text, font=font_badge, fill=(255, 255, 255, 255))

pos_y_title = pos_y_badge + b_h + b_pad_y * 2 + 35

# Title "ERIS" with Gold Foil and Glow
t_bbox = dummy_draw.textbbox((0, 0), title_text, font=font_chonburi_title)
t_w = t_bbox[2] - t_bbox[0]
t_h = t_bbox[3] - t_bbox[1]

# Flare accent line under title
flare_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
f_draw = ImageDraw.Draw(flare_layer)
f_y = pos_y_title + int(t_h * 0.95)
f_draw.line([(pos_x - 30, f_y), (pos_x + t_w + 40, f_y)], fill=(120, 210, 255, 240), width=4)
flare_layer = flare_layer.filter(ImageFilter.GaussianBlur(3))
bg1 = Image.alpha_composite(bg1, flare_layer)

# Title Shadow
glow_title = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
g_draw = ImageDraw.Draw(glow_title)
for ox in range(-7, 8):
    for oy in range(-7, 8):
        if ox*ox + oy*oy <= 49:
            g_draw.text((pos_x + ox, pos_y_title + oy), title_text, font=font_chonburi_title, fill=(20, 70, 160, 180))
glow_title = glow_title.filter(ImageFilter.GaussianBlur(10))
bg1 = Image.alpha_composite(bg1, glow_title)

# Draw Title in Gold / Icy Lustre
t_draw = ImageDraw.Draw(bg1)
t_draw.text((pos_x + 3, pos_y_title + 5), title_text, font=font_chonburi_title, fill=(0, 0, 0, 230))
t_draw.text((pos_x, pos_y_title), title_text, font=font_chonburi_title, fill=(255, 220, 130, 255))

# Subtitle Lines
pos_y_hook = pos_y_title + t_h + 45
glow_hook = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
gh_draw = ImageDraw.Draw(glow_hook)
for ox in range(-5, 6):
    for oy in range(-5, 6):
        gh_draw.text((pos_x + ox, pos_y_hook + oy), hook_line1, font=font_chonburi_hook, fill=(0, 0, 0, 220))
        gh_draw.text((pos_x + ox, pos_y_hook + 68 + oy), hook_line2, font=font_chonburi_hook, fill=(0, 0, 0, 220))
glow_hook = glow_hook.filter(ImageFilter.GaussianBlur(6))
bg1 = Image.alpha_composite(bg1, glow_hook)

h_draw = ImageDraw.Draw(bg1)
h_draw.text((pos_x, pos_y_hook), hook_line1, font=font_chonburi_hook, fill=(255, 248, 235, 255))
h_draw.text((pos_x, pos_y_hook + 68), hook_line2, font=font_chonburi_hook, fill=(180, 230, 255, 255))

# Apply Logo to Scene 01
s01 = apply_logo(bg1)
s01.save(os.path.join(out_dir, "scene-01-hook.png"), "PNG")
print("Scene 01 saved.")

# -------------------------------------------------------------
# 2. SCENES 02–08: Clean B-roll + Official Logo
# -------------------------------------------------------------
scenes_broll = [
    ("scene-02-planet-killer-pluto.png", "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/eris_vs_pluto_1789214562602.jpg"),
    ("scene-03-twin-sizes-dysnomia.png", "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/eris_keyart_bg_1789214528021.jpg"),
    ("scene-04-cosmic-mirror.png", "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/eris_mirror_surface_1789214601463.jpg"),
    ("scene-05-atmospheric-collapse.png", "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/atmospheric_collapse_1789214623662.jpg"),
    ("scene-06-breathing-world-orbit.png", "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/eris_sublimating_orbit_1789214660116.jpg"),
    ("scene-07-unreached-observatory.png", "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/raw_vlt_vertical.jpg"),
    ("scene-08-mamase-frontier-payoff.png", "assets/planet_nine_reel/images/scene-08-cosmic-frontier.png")
]

for filename, path in scenes_broll:
    print(f"Compositing {filename}...")
    im = Image.open(path).convert("RGBA")
    im = cover_crop(im, TARGET_WIDTH, TARGET_HEIGHT)
    im = apply_logo(im)
    im.save(os.path.join(out_dir, filename), "PNG")
    print(f"{filename} saved.")

# -------------------------------------------------------------
# 3. SCENE 09: Locked Canonical Outro (reels-end-scene.png)
# -------------------------------------------------------------
print("Compositing Scene 09: Canonical Outro...")
outro_raw = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGB")
s09 = outro_raw.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
s09.save(os.path.join(out_dir, "scene-09-mamase-outro.png"), "PNG")
print("Scene 09 saved.")

print("\n=== ALL 9 SCENES GENERATED & SAVED SUCCESSFULLY ===")
