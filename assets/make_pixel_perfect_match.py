import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

# 1. Load background
bg_path = "/Users/zengcode/projects/autoclip/assets/scene-01-bg-1080x1920.png"
bg = Image.open(bg_path).convert("RGBA").resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

# 2. Presenter
presenter_path = "/Users/zengcode/projects/autoclip/assets/characters/mamase-presenter-v1.png"
import rembg
orig_p = Image.open(presenter_path)
p_arr = rembg.remove(np.array(orig_p))
presenter = Image.fromarray(p_arr).convert("RGBA")

# Color grade presenter to space environment (subtle cyan/gold rim)
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

# 3. Typography Exact Match:
# Font: Kanit-Black for Title, Kanit-Bold for Hook
title_font_path = "/Users/zengcode/projects/autoclip/assets/fonts/Kanit-Black.ttf"
hook_font_path = "/Users/zengcode/projects/autoclip/assets/fonts/Kanit-Bold.ttf"

title_size = 150
hook_size = 72

font_title = ImageFont.truetype(title_font_path, title_size)
font_hook = ImageFont.truetype(hook_font_path, hook_size)

title_text = "แผนที่จักรวาล"
hook_text = "ใหญ่ที่สุดเท่าที่เคยมีมา?"

dummy_draw = ImageDraw.Draw(bg)
t_bbox = dummy_draw.textbbox((0, 0), title_text, font=font_title)
t_w = t_bbox[2] - t_bbox[0]

h_bbox = dummy_draw.textbbox((0, 0), hook_text, font=font_hook)
h_w = h_bbox[2] - h_bbox[0]

pos_x_title = (TARGET_WIDTH - t_w) // 2
pos_y_title = 120

pos_x_hook = (TARGET_WIDTH - h_w) // 2
pos_y_hook = pos_y_title + 165

# A. Strong Orange Backlight / Ambient Flare behind Title (underneath the letters)
glow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
g_draw = ImageDraw.Draw(glow_layer)
g_draw.text((pos_x_title, pos_y_title), title_text, font=font_title, fill=(255, 120, 10, 255))
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(30))
bg.paste(glow_layer, (0, 0), mask=glow_layer)

# Extra horizontal lens flare strip under the title (like in the reference!)
flare_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
f_draw = ImageDraw.Draw(flare_layer)
f_y = pos_y_title + int(title_size * 0.85)
f_draw.line([(pos_x_title - 60, f_y), (pos_x_title + t_w + 60, f_y)], fill=(255, 200, 80, 200), width=6)
flare_layer = flare_layer.filter(ImageFilter.GaussianBlur(8))
bg.paste(flare_layer, (0, 0), mask=flare_layer)

# B. Deep Drop Shadow
shadow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_layer)
s_draw.text((pos_x_title + 8, pos_y_title + 14), title_text, font=font_title, fill=(0, 0, 0, 255))
s_draw.text((pos_x_hook + 6, pos_y_hook + 10), hook_text, font=font_hook, fill=(0, 0, 0, 255))
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(14))
bg.paste(shadow_layer, (0, 0), mask=shadow_layer)
bg.paste(shadow_layer, (0, 0), mask=shadow_layer) # deeper shadow

# C. Outer Dark Stroke for Title
stroke_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
st_draw = ImageDraw.Draw(stroke_layer)
st_draw.text((pos_x_title, pos_y_title), title_text, font=font_title, fill=(30, 10, 5, 255), stroke_width=10)
bg.paste(stroke_layer, (0, 0), mask=stroke_layer)

# D. Gold Foil / Sparkling Metallic Texture for Title
# Create gold textured foil: multi-frequency noise + gold gradient
mask_title = Image.new("L", (TARGET_WIDTH, TARGET_HEIGHT), 0)
m_draw = ImageDraw.Draw(mask_title)
m_draw.text((pos_x_title, pos_y_title), title_text, fill=255, font=font_title)

# Generate gold metallic gradient with micro-sparkles
gold_tex = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
gt_draw = ImageDraw.Draw(gold_tex)

np.random.seed(42)
noise = np.random.normal(0, 18, (TARGET_HEIGHT, TARGET_WIDTH))

for y in range(pos_y_title - 20, pos_y_title + title_size + 40):
    rel = (y - pos_y_title) / float(title_size)
    rel = max(0.0, min(1.0, rel))
    
    # 3-tier metallic gradient
    if rel < 0.25:
        # Top specular highlight
        base_r = 255
        base_g = int(245 - rel/0.25 * 30)
        base_b = int(220 - rel/0.25 * 140)
    elif rel < 0.70:
        # Midtone gold
        sub = (rel - 0.25) / 0.45
        base_r = int(255 - sub * 10)
        base_g = int(215 - sub * 75)
        base_b = int(80 - sub * 65)
    else:
        # Bottom rich copper/amber
        sub = (rel - 0.70) / 0.30
        base_r = int(245 - sub * 75)
        base_g = int(140 - sub * 70)
        base_b = int(15 - sub * 15)

    gt_draw.line([(pos_x_title - 60, y), (pos_x_title + t_w + 60, y)], fill=(base_r, base_g, base_b, 255))

# Add subtle metallic noise grain
gold_np = np.array(gold_tex).astype(np.int16)
for c in range(3):
    gold_np[:, :, c] = np.clip(gold_np[:, :, c] + noise * 0.4, 0, 255)
gold_tex = Image.fromarray(gold_np.astype(np.uint8))

# Add bevel 3D top edge highlight
edge_hl = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
e_draw = ImageDraw.Draw(edge_hl)
e_draw.text((pos_x_title, pos_y_title - 2), title_text, font=font_title, fill=(255, 255, 220, 180), stroke_width=2)
gold_tex.paste(edge_hl, (0, 0), mask=edge_hl)

bg.paste(gold_tex, (0, 0), mask=mask_title)

# E. Hook Text (Kanit Bold, crisp white, black outline)
hook_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
h_draw = ImageDraw.Draw(hook_layer)
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_hook, fill=(0, 0, 0, 255), stroke_width=6)
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_hook, fill=(255, 255, 255, 255))
bg.paste(hook_layer, (0, 0), mask=hook_layer)

out_file = "/Users/zengcode/projects/autoclip/assets/scene-01-google-maps-kanit-gold.png"
bg.convert("RGB").save(out_file, "PNG")
os.system(f"cp {out_file} /Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scene-01-google-maps-kanit-gold.png")
print("SUCCESS_KANIT_GOLD")
