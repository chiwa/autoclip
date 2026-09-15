import os
import time
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import rembg
import numpy as np

img_dir = "/Users/zengcode/projects/autoclip/assets/angkor_cinematic_documentary/images"
prompts = {
    1: "Premium cinematic historical documentary key art. Wide landscape of ancient Angkor Wat at its height on the left. Dark monsoon clouds encroaching on the right. Warm sandstone, golden sunrise, deep jungle green, teal shadows.",
    6: "Low-angle shot of ancient artisans constructing a sandstone temple. Moving stone blocks. Sunlight flaring through pillars.",
    7: "Majestic wide shot of the completed Angkor Wat. Golden sunrise illuminating massive stone causeway. Cinematic lighting.",
    8: "Cinematic close-up tracking shot along highly detailed sandstone bas-relief of Khmer soldiers marching. Warm lighting.",
    11: "Bustling ancient Khmer marketplace. Diverse traders, artisans exchanging goods. Warm sunlight, colorful historical clothing.",
    12: "Cinematic shot of ancient merchant ships departing down a wide river towards the sea. Troops marching along a dirt road."
}

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')]
urllib.request.install_opener(opener)

def dl_image(prompt, filepath):
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1920&height=1080&nologo=true&seed=999"
    while True:
        try:
            urllib.request.urlretrieve(url, filepath)
            if os.path.getsize(filepath) > 45000:
                return True
        except Exception as e:
            pass
        print(f"Retrying {os.path.basename(filepath)}...")
        time.sleep(5)

# Scene 1
bg_path = os.path.join(img_dir, "scene-01_temp.png")
if dl_image(prompts[1], bg_path):
    print("Downloaded Scene 1 background.")
    try:
        bg = Image.open(bg_path).convert("RGB")
        width, height = bg.size
        
        # rembg
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
        os.remove(bg_path)
        print("Scene 1 composited and fixed.")
    except Exception as e:
        print(f"Error scene 1: {e}")

for i in [6, 7, 8, 11, 12]:
    path = os.path.join(img_dir, f"scene-{i:02d}.png")
    tmp = os.path.join(img_dir, f"temp_{i}.png")
    if dl_image(prompts[i], tmp):
        try:
            img = Image.open(tmp).convert("RGB")
            img.save(path, "PNG")
            os.remove(tmp)
            print(f"Fixed Scene {i}")
        except: pass

print("All remaining done!")
