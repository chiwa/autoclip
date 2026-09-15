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

# Color grade presenter to space environment
enhancer = ImageEnhance.Brightness(presenter)
presenter = enhancer.enhance(0.9)
tint = Image.new("RGBA", presenter.size, (0, 80, 140, 255))
presenter_tinted = Image.blend(presenter, tint, 0.1)
presenter_tinted.putalpha(Image.fromarray(p_arr[:, :, 3]))
presenter = presenter_tinted

p_height = int(TARGET_HEIGHT * 0.58)
p_ratio = presenter.width / presenter.height
p_width = int(p_height * p_ratio)
presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)

paste_x = TARGET_WIDTH - p_width - 15
paste_y = TARGET_HEIGHT - p_height
bg.paste(presenter, (paste_x, paste_y), mask=presenter)

# 3. Typography Exact Replica of Reference
# Reference details:
# Title: Big, bold, centered or prominent top, Metallic Gold Texture with dark rim and glowing orange/gold backlight.
# Hook: Bold modern sans, clean white, dark drop shadow.
title_font_path = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/24bfb28c08310266db798d9d93c7e2ca87a66299.asset/AssetData/ChakraPetch.ttc"
hook_font_path = "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc"

title_size = 145
hook_size = 72

font_title = ImageFont.truetype(title_font_path, title_size, index=0) # Chakra Petch Bold
font_hook = ImageFont.truetype(hook_font_path, hook_size, index=5) # Sukhumvit Set Bold

title_text = "แผนที่จักรวาล"
hook_text = "ใหญ่ที่สุดเท่าที่เคยมีมา?"

# Measure texts
dummy_draw = ImageDraw.Draw(bg)
t_bbox = dummy_draw.textbbox((0, 0), title_text, font=font_title)
t_w = t_bbox[2] - t_bbox[0]

h_bbox = dummy_draw.textbbox((0, 0), hook_text, font=font_hook)
h_w = h_bbox[2] - h_bbox[0]

# Centered like the reference poster:
pos_x_title = (TARGET_WIDTH - t_w) // 2
pos_y_title = 130

pos_x_hook = (TARGET_WIDTH - h_w) // 2
pos_y_hook = pos_y_title + 155

# --- Title Effects: ---
# A. Warm orange glow behind title
glow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
g_draw = ImageDraw.Draw(glow_layer)
g_draw.text((pos_x_title, pos_y_title), title_text, font=font_title, fill=(255, 140, 20, 240))
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(35))
bg.paste(glow_layer, (0, 0), mask=glow_layer)

# B. Deep Drop Shadow behind Title and Hook
shadow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_layer)
s_draw.text((pos_x_title + 10, pos_y_title + 14), title_text, font=font_title, fill=(0, 0, 0, 255))
s_draw.text((pos_x_hook + 6, pos_y_hook + 8), hook_text, font=font_hook, fill=(0, 0, 0, 255))
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(12))
bg.paste(shadow_layer, (0, 0), mask=shadow_layer)

# C. Outer Dark Stroke for Title
stroke_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
st_draw = ImageDraw.Draw(stroke_layer)
st_draw.text((pos_x_title, pos_y_title), title_text, font=font_title, fill=(35, 15, 5, 255), stroke_width=10)
bg.paste(stroke_layer, (0, 0), mask=stroke_layer)

# D. Gold Metallic Gradient Fill for Title
# Create gold gradient texture (from bright light gold #FFF2A7 at top to rich amber #E68A00 and darker at bottom)
mask_title = Image.new("L", (TARGET_WIDTH, TARGET_HEIGHT), 0)
m_draw = ImageDraw.Draw(mask_title)
m_draw.text((pos_x_title, pos_y_title), title_text, fill=255, font=font_title)

# Generate gradient box
gold_tex = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
gt_draw = ImageDraw.Draw(gold_tex)
for y in range(pos_y_title - 20, pos_y_title + title_size + 40):
    rel = (y - pos_y_title) / float(title_size)
    rel = max(0.0, min(1.0, rel))
    # Rich multi-stop gold
    if rel < 0.35:
        # Highlight: Pale gold #FFF8D6 to Brilliant Gold #FFD700
        r = int(255)
        g = int(248 - rel/0.35 * (248 - 215))
        b = int(214 - rel/0.35 * (214 - 30))
    elif rel < 0.75:
        # Midtone: Brilliant Gold to Deep Amber #E68000
        sub = (rel - 0.35) / 0.40
        r = int(255 - sub * 25)
        g = int(215 - sub * 87)
        b = int(30 - sub * 30)
    else:
        # Bottom: Deep Amber to Dark Gold Bronze #8B4500
        sub = (rel - 0.75) / 0.25
        r = int(230 - sub * 91)
        g = int(128 - sub * 59)
        b = int(0)
    gt_draw.line([(pos_x_title - 50, y), (pos_x_title + t_w + 50, y)], fill=(r, g, b, 255))

# Add inner bevel highlight simulation (draw smaller white highlight along top)
inner_highlight = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
ih_draw = ImageDraw.Draw(inner_highlight)
ih_draw.text((pos_x_title, pos_y_title - 2), title_text, font=font_title, fill=(255, 255, 220, 160), stroke_width=2)
gold_tex.paste(inner_highlight, (0, 0), mask=inner_highlight)

bg.paste(gold_tex, (0, 0), mask=mask_title)

# E. Hook Text (Crisp White + Clean Subtitle Stroke like reference)
hook_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
h_draw = ImageDraw.Draw(hook_layer)
# Stroke
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_hook, fill=(0, 0, 0, 255), stroke_width=6)
# White text
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_hook, fill=(255, 255, 255, 255))
bg.paste(hook_layer, (0, 0), mask=hook_layer)

out_file = "/Users/zengcode/projects/autoclip/assets/scene-01-google-maps-reference-match.png"
bg.convert("RGB").save(out_file, "PNG")
os.system(f"cp {out_file} /Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scene-01-google-maps-reference-match.png")
print("SUCCESS_MATCH")
