import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import rembg
import numpy as np

img_dir = "/Users/zengcode/projects/autoclip/assets/angkor_cinematic_documentary/images"

# Use scene-04.png as the background for scene 01
bg_path = os.path.join(img_dir, "scene-04.png")
bg = Image.open(bg_path).convert("RGB")
width, height = bg.size

# Darken the background slightly so text pops out more
enhancer = ImageEnhance.Brightness(bg)
bg = enhancer.enhance(0.7)

# rembg on presenter
ref_path = "/Users/zengcode/projects/autoclip/assets/characters/mamase-presenter-v1.png"
orig_p = Image.open(ref_path)
p_arr = rembg.remove(np.array(orig_p))
presenter = Image.fromarray(p_arr).convert("RGBA")

# resize
p_ratio = presenter.width / presenter.height
p_height = int(height * 0.95)
p_width = int(p_height * p_ratio)
presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)

bg.paste(presenter, (width - p_width - 50, height - p_height), mask=presenter)

draw = ImageDraw.Draw(bg)
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 160)
    font_hook = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 120)
except:
    font_title, font_hook = ImageFont.load_default(), ImageFont.load_default()
    
draw.text((105, 105), "จักรวรรดิขอม", fill=(50, 40, 20), font=font_title)
draw.text((100, 100), "จักรวรรดิขอม", fill=(255, 240, 200), font=font_title)
draw.text((105, 305), "หายไปไหน?", fill=(50, 40, 20), font=font_hook)
draw.text((100, 300), "หายไปไหน?", fill=(255, 240, 200), font=font_hook)

bg.save(os.path.join(img_dir, "scene-01.png"), "PNG")
print("Scene 1 fixed using Scene 4 background!")

