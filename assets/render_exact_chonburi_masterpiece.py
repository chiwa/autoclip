import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

# 1. Background (1080x1920)
bg_path = "/Users/zengcode/projects/autoclip/assets/scene-01-bg-1080x1920.png"
bg = Image.open(bg_path).convert("RGBA").resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

# 2. Presenter
presenter_path = "/Users/zengcode/projects/autoclip/assets/characters/mamase-presenter-v1.png"
import rembg
orig_p = Image.open(presenter_path)
p_arr = rembg.remove(np.array(orig_p))
presenter = Image.fromarray(p_arr).convert("RGBA")

# Color grade presenter to space environment
enhancer = ImageEnhance.Brightness(presenter)
presenter = enhancer.enhance(0.92)
tint = Image.new("RGBA", presenter.size, (0, 80, 140, 255))
presenter_tinted = Image.blend(presenter, tint, 0.08)
presenter_tinted.putalpha(Image.fromarray(p_arr[:, :, 3]))
presenter = presenter_tinted

p_height = int(TARGET_HEIGHT * 0.58)
p_ratio = presenter.width / presenter.height
p_width = int(p_height * p_ratio)
presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)

paste_x = TARGET_WIDTH - p_width - 15
paste_y = TARGET_HEIGHT - p_height
bg.paste(presenter, (paste_x, paste_y), mask=presenter)

# 3. Typography - EXACT FONT MATCH:
# Title: Chonburi (Serif High-Contrast Display) - Identical to 'ดาวศุกร์'
# Hook: Chonburi (Serif High-Contrast Display) - Identical to '1 วัน ยาวกว่า 1 ปี?'
font_chonburi_title = ImageFont.truetype("/Users/zengcode/projects/autoclip/assets/fonts/Chonburi.ttf", 155)
font_chonburi_hook = ImageFont.truetype("/Users/zengcode/projects/autoclip/assets/fonts/Chonburi.ttf", 74)

title_text = "แผนที่จักรวาล"
hook_text = "ใหญ่ที่สุดเท่าที่เคยมีมา?"

dummy_draw = ImageDraw.Draw(bg)
t_bbox = dummy_draw.textbbox((0, 0), title_text, font=font_chonburi_title)
t_w = t_bbox[2] - t_bbox[0]
t_h = t_bbox[3] - t_bbox[1]

h_bbox = dummy_draw.textbbox((0, 0), hook_text, font=font_chonburi_hook)
h_w = h_bbox[2] - h_bbox[0]

pos_x_title = (TARGET_WIDTH - t_w) // 2
pos_y_title = 120

pos_x_hook = (TARGET_WIDTH - h_w) // 2
pos_y_hook = pos_y_title + 180

# -------------------------------------------------------------
# A. Lens flare horizontal glow bar beneath title
flare_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
f_draw = ImageDraw.Draw(flare_layer)
f_y = pos_y_title + int(t_h * 0.92)
# Orange hot center line
f_draw.line([(pos_x_title - 120, f_y), (pos_x_title + t_w + 120, f_y)], fill=(255, 140, 20, 240), width=10)
f_draw.line([(pos_x_title - 40, f_y), (pos_x_title + t_w + 40, f_y)], fill=(255, 240, 160, 255), width=4)
flare_layer = flare_layer.filter(ImageFilter.GaussianBlur(10))
bg.paste(flare_layer, (0, 0), mask=flare_layer)

# B. Deep Radial Warm Glow behind title
glow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
g_draw = ImageDraw.Draw(glow_layer)
g_draw.text((pos_x_title, pos_y_title), title_text, font=font_chonburi_title, fill=(255, 100, 10, 255))
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(35))
bg.paste(glow_layer, (0, 0), mask=glow_layer)

# C. Heavy Blurred Drop Shadow for Title and Hook
shadow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_layer)
s_draw.text((pos_x_title + 10, pos_y_title + 14), title_text, font=font_chonburi_title, fill=(0, 0, 0, 255))
s_draw.text((pos_x_hook + 6, pos_y_hook + 10), hook_text, font=font_chonburi_hook, fill=(0, 0, 0, 255))
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(14))
bg.paste(shadow_layer, (0, 0), mask=shadow_layer)
bg.paste(shadow_layer, (0, 0), mask=shadow_layer)

# D. Outer Dark Rim / Bevel Stroke for Title (Chocolate Dark Amber)
stroke_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
st_draw = ImageDraw.Draw(stroke_layer)
st_draw.text((pos_x_title, pos_y_title), title_text, font=font_chonburi_title, fill=(25, 8, 2, 255), stroke_width=11)
bg.paste(stroke_layer, (0, 0), mask=stroke_layer)

# E. Gold Foil Texture Fill (Identical to 'ดาวศุกร์'):
# Rich gold foil with metallic speckles, white specular rim at top, amber gradient at bottom
mask_title = Image.new("L", (TARGET_WIDTH, TARGET_HEIGHT), 0)
m_draw = ImageDraw.Draw(mask_title)
m_draw.text((pos_x_title, pos_y_title), title_text, fill=255, font=font_chonburi_title)

# Generate multi-layer gold foil
gold_canvas = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
gc_draw = ImageDraw.Draw(gold_canvas)

np.random.seed(1337)
noise = np.random.normal(0, 24, (TARGET_HEIGHT, TARGET_WIDTH))

for y in range(pos_y_title - 20, pos_y_title + 220):
    rel = (y - pos_y_title) / 160.0
    rel = max(0.0, min(1.0, rel))
    
    if rel < 0.20:
        # High specular pale gold highlight
        r = 255
        g = int(250 - (rel / 0.20) * 35)
        b = int(225 - (rel / 0.20) * 160)
    elif rel < 0.65:
        # Pure radiant 24k gold
        sub = (rel - 0.20) / 0.45
        r = int(255 - sub * 10)
        g = int(215 - sub * 70)
        b = int(65 - sub * 55)
    else:
        # Deep amber/bronze at bottom
        sub = (rel - 0.65) / 0.35
        r = int(245 - sub * 65)
        g = int(145 - sub * 75)
        b = int(10 - sub * 10)

    gc_draw.line([(pos_x_title - 80, y), (pos_x_title + t_w + 80, y)], fill=(r, g, b, 255))

# Add sparkling metallic foil texture
gold_arr = np.array(gold_canvas).astype(np.int16)
for c in range(3):
    gold_arr[:, :, c] = np.clip(gold_arr[:, :, c] + noise * 0.55, 0, 255)
gold_canvas = Image.fromarray(gold_arr.astype(np.uint8))

# Top bevel highlight line
top_hl = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
th_draw = ImageDraw.Draw(top_hl)
th_draw.text((pos_x_title, pos_y_title - 2), title_text, font=font_chonburi_title, fill=(255, 255, 230, 180), stroke_width=2)
gold_canvas.paste(top_hl, (0, 0), mask=top_hl)

bg.paste(gold_canvas, (0, 0), mask=mask_title)

# F. Hook (Chonburi Serif, Warm Creamy White with bevel/glow like '1 วัน ยาวกว่า 1 ปี?')
hook_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
h_draw = ImageDraw.Draw(hook_layer)
# Dark stroke
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_chonburi_hook, fill=(10, 5, 2, 255), stroke_width=6)
# Warm light cream fill (matching the reference hook exactly)
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_chonburi_hook, fill=(255, 250, 240, 255))
bg.paste(hook_layer, (0, 0), mask=hook_layer)

out_file = "/Users/zengcode/projects/autoclip/assets/scene-01-google-maps-chonburi-exact.png"
bg.convert("RGB").save(out_file, "PNG")
os.system(f"cp {out_file} /Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scene-01-google-maps-chonburi-exact.png")
print("SUCCESS_EXACT_CHONBURI")
