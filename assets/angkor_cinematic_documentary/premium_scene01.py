import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import rembg
import numpy as np

img_dir = "/Users/zengcode/projects/autoclip/assets/angkor_cinematic_documentary/images"

# Load Background
bg_path = os.path.join(img_dir, "scene-04.png")
bg = Image.open(bg_path).convert("RGB")
width, height = bg.size

# Darken and add a slight blue/teal tint to make it more cinematic
enhancer = ImageEnhance.Brightness(bg)
bg = enhancer.enhance(0.75)
enhancer_color = ImageEnhance.Color(bg)
bg = enhancer_color.enhance(1.2)

# Create a dark vignette on the left/top to make text pop
vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
v_draw.rectangle([0, 0, width//2, height], fill=(0, 0, 0, 100)) # Darken left
v_draw.rectangle([0, 0, width, height//3], fill=(0, 0, 0, 100)) # Darken top
bg.paste(vignette, (0,0), vignette)

# Process Presenter
ref_path = "/Users/zengcode/projects/autoclip/assets/characters/mamase-presenter-v1.png"
orig_p = Image.open(ref_path)
p_arr = rembg.remove(np.array(orig_p))
presenter = Image.fromarray(p_arr).convert("RGBA")

# Resize Presenter (make him prominent on the right)
p_ratio = presenter.width / presenter.height
p_height = int(height * 0.95)
p_width = int(p_height * p_ratio)
presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)

# Paste Presenter
paste_x = width - p_width - 20
paste_y = height - p_height
bg.paste(presenter, (paste_x, paste_y), mask=presenter)

# --- PREMIUM TYPOGRAPHY ---
# Fonts
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 180)
    font_hook = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 130)
except:
    font_title = ImageFont.load_default()
    font_hook = ImageFont.load_default()

text1 = "จักรวรรดิขอม"
text2 = "หายไปไหน?"
pos1 = (80, 80)
pos2 = (80, 320)

txt_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
txt_draw = ImageDraw.Draw(txt_layer)

# 1. Drop Shadow (Heavy blur)
shadow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_layer)
shadow_offset = 15
s_draw.text((pos1[0]+shadow_offset, pos1[1]+shadow_offset), text1, fill=(0, 0, 0, 200), font=font_title)
s_draw.text((pos2[0]+shadow_offset, pos2[1]+shadow_offset), text2, fill=(0, 0, 0, 200), font=font_hook)
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(15))
bg.paste(shadow_layer, (0,0), mask=shadow_layer)

# 2. Text with Stroke (Outline)
# To create a gradient, we draw the text in white, use it as a mask over a gradient image
mask1 = Image.new("L", (width, height), 0)
m1_draw = ImageDraw.Draw(mask1)
m1_draw.text(pos1, text1, fill=255, font=font_title)
m1_draw.text(pos2, text2, fill=255, font=font_hook)

# Create gold gradient background
gradient = Image.new("RGBA", (width, height))
g_draw = ImageDraw.Draw(gradient)
for y in range(height):
    # Gold gradient mapping (top light yellow, bottom deep orange/gold)
    r = int(255 - (y / height) * 50)
    g = int(230 - (y / height) * 100)
    b = int(100 - (y / height) * 100)
    g_draw.line([(0, y), (width, y)], fill=(r, max(g,0), max(b,0), 255))

# The actual text filled with gradient
grad_text = Image.new("RGBA", (width, height))
grad_text.paste(gradient, (0,0), mask=mask1)

# Stroke (Black Outline)
stroke_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
stroke_draw = ImageDraw.Draw(stroke_layer)
stroke_width = 8
stroke_draw.text(pos1, text1, font=font_title, fill=(0,0,0,255), stroke_width=stroke_width, stroke_fill=(0,0,0,255))
stroke_draw.text(pos2, text2, font=font_hook, fill=(0,0,0,255), stroke_width=stroke_width, stroke_fill=(0,0,0,255))

# Paste stroke, then gradient text on top
bg.paste(stroke_layer, (0,0), mask=stroke_layer)
bg.paste(grad_text, (0,0), mask=mask1)

out_path = os.path.join(img_dir, "scene-01_premium.png")
bg.save(out_path, "PNG")
print(f"Premium Scene 01 saved: {out_path}")
