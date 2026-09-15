import os
import shutil
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np

def create_starfield(w, h, seed=42, num_stars=350):
    np.random.seed(seed)
    star_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(star_img)
    for _ in range(num_stars):
        x = np.random.randint(0, w)
        y = np.random.randint(0, h)
        b = np.random.randint(90, 255)
        r = np.random.choice([1, 1, 1, 2])
        col = (b, int(b * 0.95), int(b * 1.1), np.random.randint(180, 255))
        draw.ellipse([x, y, x + r, y + r], fill=col)
    return star_img

def test_all():
    os.makedirs("scratch/saturn_preview", exist_ok=True)
    w, h = 1080, 1920
    
    # 1. Scene 01: Hook & Narrative Key Art
    canvas1 = Image.new("RGBA", (w, h), (4, 5, 12, 255))
    base1 = Image.open("scratch/saturn_downloads/hubble_saturn_2025.jpg").convert("RGBA")
    # scale to width 1080
    scale1 = 1080 / base1.width
    nh1 = int(base1.height * scale1)
    base1_fit = base1.resize((1080, nh1), Image.Resampling.LANCZOS)
    
    # Feather top and bottom
    arr1 = np.array(base1_fit, dtype=np.float32)
    fade1 = 120
    arr1[:fade1, :, 3] *= np.linspace(0.0, 1.0, fade1)[:, None]
    arr1[-fade1:, :, 3] *= np.linspace(1.0, 0.0, fade1)[:, None]
    faded1 = Image.fromarray(np.clip(arr1, 0, 255).astype(np.uint8))
    canvas1.paste(faded1, (0, 180), faded1)
    
    # Starfield
    canvas1.alpha_composite(create_starfield(w, h, seed=501))
    
    # Presenter Cutout on Right
    cutout = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scratch/mamase_presenter_cutout.png").convert("RGBA")
    target_h = 1320
    scale_p = target_h / cutout.height
    target_w = int(cutout.width * scale_p)
    presenter_fit = cutout.resize((target_w, target_h), Image.Resampling.LANCZOS)
    canvas1.paste(presenter_fit, (w - target_w + 60, h - target_h), presenter_fit)
    
    # Typography in Upper-Left
    font_path = "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc"
    f_topic = ImageFont.truetype(font_path, 42, index=0)
    f_hook = ImageFont.truetype(font_path, 74, index=0)
    draw1 = ImageDraw.Draw(canvas1)
    
    tx, ty = 60, 110
    draw1.text((tx + 2, ty + 2), "ความลับขั้วดาวเสาร์", font=f_topic, fill=(0, 0, 0, 220))
    draw1.text((tx, ty), "ความลับขั้วดาวเสาร์", font=f_topic, fill=(255, 209, 102, 255))
    
    hy = ty + 68
    draw1.text((tx + 3, hy + 3), "10 เหลี่ยมปริศนา\nที่ Cassini ไม่เคยเห็น!", font=f_hook, fill=(0, 0, 0, 220))
    draw1.text((tx, hy), "10 เหลี่ยมปริศนา\nที่ Cassini ไม่เคยเห็น!", font=f_hook, fill=(255, 255, 255, 255))
    
    canvas1.convert("RGB").save("scratch/saturn_preview/scene-01-hook.png")
    print("Scene 01 OK")

if __name__ == "__main__":
    test_all()
