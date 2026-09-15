import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import rembg
import numpy as np

# 1. Load Background
bg_path = "/Users/zengcode/projects/autoclip/assets/scene-01-bg-only.png"
bg = Image.open(bg_path).convert("RGBA")
width, height = bg.size

# 2. Load and Die-cut Official Presenter
presenter_path = "/Users/zengcode/projects/autoclip/assets/characters/mamase-presenter-v1.png"
if not os.path.exists(presenter_path):
    # Fallback to local test path if needed, but the path should be correct based on previous logs
    print(f"Error: Could not find presenter at {presenter_path}")

orig_p = Image.open(presenter_path)
p_arr = rembg.remove(np.array(orig_p))
presenter = Image.fromarray(p_arr).convert("RGBA")

# 3. Color Grade Presenter (Match lighting to dark space background)
# Reduce brightness slightly
enhancer = ImageEnhance.Brightness(presenter)
presenter = enhancer.enhance(0.85)

# Add a subtle cyan tint to match the cosmic web
# Create a solid color image
tint = Image.new("RGBA", presenter.size, (0, 100, 150, 255))
# Blend it (keep alpha)
presenter_tinted = Image.blend(presenter, tint, 0.15)
# Restore exact alpha channel from rembg
presenter_tinted.putalpha(Image.fromarray(p_arr[:,:,3]))
presenter = presenter_tinted

# 4. Resize and Position
target_height = int(height * 0.6) # Take up 60% of the height
p_ratio = presenter.width / presenter.height
target_width = int(target_height * p_ratio)
presenter = presenter.resize((target_width, target_height), Image.Resampling.LANCZOS)

# Position on the bottom right
paste_x = width - target_width - 10
paste_y = height - target_height
bg.paste(presenter, (paste_x, paste_y), mask=presenter)

# 5. Premium Typography
# Use Sukhumvit Set if available, else Thonburi
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/SukhumvitSet.ttc", 130, index=5) # Bold
    font_hook = ImageFont.truetype("/System/Library/Fonts/SukhumvitSet.ttc", 100, index=5)
except:
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 130)
        font_hook = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 100)
    except:
        font_title = ImageFont.load_default()
        font_hook = ImageFont.load_default()

text1 = "Google Maps จักรวาล"
text2 = "ใหญ่ที่สุดเท่าที่เคยมีมา"
pos1 = (60, 200)
pos2 = (60, 380)

# Drop Shadow (Blurred)
shadow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_layer)
shadow_offset = 15
s_draw.text((pos1[0]+shadow_offset, pos1[1]+shadow_offset), text1, fill=(0, 0, 0, 255), font=font_title)
s_draw.text((pos2[0]+shadow_offset, pos2[1]+shadow_offset), text2, fill=(0, 0, 0, 255), font=font_hook)
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(15))
bg.paste(shadow_layer, (0,0), mask=shadow_layer)
bg.paste(shadow_layer, (0,0), mask=shadow_layer) # Double paste for darker shadow

# Title Gradient (Gold)
mask1 = Image.new("L", (width, height), 0)
m1_draw = ImageDraw.Draw(mask1)
m1_draw.text(pos1, text1, fill=255, font=font_title)

gradient = Image.new("RGBA", (width, height))
g_draw = ImageDraw.Draw(gradient)
for y in range(height):
    # Gold gradient (top light, bottom dark orange/gold)
    r = int(255)
    g = int(230 - (y / height) * 100)
    b = int(100 - (y / height) * 100)
    g_draw.line([(0, y), (width, y)], fill=(r, max(g,0), max(b,0), 255))
    
grad_text = Image.new("RGBA", (width, height))
grad_text.paste(gradient, (0,0), mask=mask1)

# Hook (White)
mask2 = Image.new("L", (width, height), 0)
m2_draw = ImageDraw.Draw(mask2)
m2_draw.text(pos2, text2, fill=255, font=font_hook)
white_text = Image.new("RGBA", (width, height), (255, 255, 255, 255))
white_text.paste(white_text, (0,0), mask=mask2)

# Black Stroke (Outline)
stroke_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
stroke_draw = ImageDraw.Draw(stroke_layer)
stroke_width = 8
stroke_draw.text(pos1, text1, font=font_title, fill=(0,0,0,255), stroke_width=stroke_width)
stroke_draw.text(pos2, text2, font=font_hook, fill=(0,0,0,255), stroke_width=stroke_width)

# Combine text layers
bg.paste(stroke_layer, (0,0), mask=stroke_layer)
bg.paste(grad_text, (0,0), mask=mask1)
bg.paste(white_text, (0,0), mask=mask2)

out_path = "/Users/zengcode/projects/autoclip/assets/scene-01-google-maps.png"
bg.convert("RGB").save(out_path, "PNG")
os.system(f"cp {out_path} /Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scene-01-google-maps.png")
print("SUCCESS")
