import os
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import rembg
import numpy as np
import sys

img_dir = "/Users/zengcode/projects/autoclip/assets/angkor_cinematic_documentary/images"
prompt = "Premium cinematic historical documentary key art. Wide landscape of ancient Angkor Wat at its height on the left. Dark monsoon clouds encroaching on the right. Warm sandstone, golden sunrise, deep jungle green, teal shadows."

encoded = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded}?width=1920&height=1080&nologo=true&seed=999"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = response.read()
        if len(data) > 50000:
            with open(os.path.join(img_dir, "scene-01_temp2.png"), "wb") as f:
                f.write(data)
                print("Downloaded S1", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)

try:
    bg_path = os.path.join(img_dir, "scene-01_temp2.png")
    bg = Image.open(bg_path).convert("RGB")
    width, height = bg.size
    ref_path = "/Users/zengcode/projects/autoclip/assets/characters/mamase-presenter-v1.png"
    orig_p = Image.open(ref_path)
    p_arr = rembg.remove(np.array(orig_p))
    presenter = Image.fromarray(p_arr).convert("RGBA")
    p_ratio = presenter.width / presenter.height
    p_height = int(height * 0.95)
    p_width = int(p_height * p_ratio)
    presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)
    bg.paste(presenter, (width - p_width - 50, height - p_height), mask=presenter)
    draw = ImageDraw.Draw(bg)
    font_title = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 160)
    font_hook = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 120)
    draw.text((105, 105), "จักรวรรดิขอม", fill=(50, 40, 20), font=font_title)
    draw.text((100, 100), "จักรวรรดิขอม", fill=(255, 240, 200), font=font_title)
    draw.text((105, 305), "หายไปไหน?", fill=(50, 40, 20), font=font_hook)
    draw.text((100, 300), "หายไปไหน?", fill=(255, 240, 200), font=font_hook)
    bg.save(os.path.join(img_dir, "scene-01.png"), "PNG")
    print("S1 fixed successfully!", flush=True)
except Exception as e:
    print(f"Proc Error: {e}", flush=True)
