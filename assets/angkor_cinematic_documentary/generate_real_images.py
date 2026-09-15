import os
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageFont

img_dir = "/Users/zengcode/projects/autoclip/assets/angkor_cinematic_documentary/images"

prompts = {
    1: "Cinematic shot of ancient Angkor Wat at its height on the left. Dark monsoon clouds on the right. Warm sandstone, golden sunrise, deep jungle green.",
    2: "Cinematic shot of ancient Southeast Asia. Lush tropical river, diverse ancient merchants in wooden boats. Volumetric sunlight.",
    3: "Cinematic view from top of Kulen Mountain looking down at a vast plain. Epic golden sunlight, morning mist, warm sandstone.",
    4: "Epic aerial drone shot of ancient Angkor city at its peak. Monumental sandstone temples, vast barays, intricate canals. Golden sunlight.",
    5: "Cinematic wide shot of an immense ancient reservoir reflecting the sun. Intricate canal systems, lush rice fields, deep teal shadows.",
    6: "Low-angle shot of ancient artisans constructing a massive sandstone temple. Moving huge stone blocks. Sunlight flaring through pillars.",
    7: "Majestic wide shot of the completed Angkor Wat. Golden sunrise illuminating the massive stone causeway. Cinematic lighting.",
    8: "Cinematic close-up tracking shot along a highly detailed sandstone bas-relief of ancient Khmer soldiers marching. Warm lighting.",
    9: "Intense cinematic shot of ancient naval warfare on Tonle Sap lake. Ancient wooden war boats clashing. Fire and smoke reflecting on water.",
    10: "Cinematic shot of massive stone faces of the Bayon temple being constructed. Golden morning light. People traveling on a Naga bridge.",
    11: "Bustling ancient Khmer marketplace. Diverse traders, artisans exchanging goods. Warm sunlight, colorful historical clothing.",
    12: "Cinematic shot of ancient merchant ships departing down a wide river towards the sea. Troops marching along a dirt road.",
    13: "Cinematic wide shot of a harsh, dry massive reservoir bed. Cracked earth, dry canals. Dusty warm sandstone, oppressive bright sunlight.",
    14: "Violent monsoon rain pouring down. Flash floods violently eroding massive earthen dikes and ancient sandstone water channels.",
    15: "Peaceful cinematic shot of Angkor Wat gradually being embraced by lush jungle vegetation. Sunlight piercing through morning mist. Warm sandstone.",
    16: "Clean modern cinematic studio background. Deep teal and warm gold ambient lighting. Professional documentary style."
}

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')]
urllib.request.install_opener(opener)

def download_pollination(prompt, filepath):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1920&height=1080&nologo=true&seed=888"
    print(f"Downloading {os.path.basename(filepath)}...")
    try:
        urllib.request.urlretrieve(url, filepath)
        return True
    except Exception as e:
        print(f"Failed to download: {e}")
        return False

scene1_bg = os.path.join(img_dir, "scene-01_bg.png")
scene1_out = os.path.join(img_dir, "scene-01.png")
if download_pollination(prompts[1], scene1_bg):
    try:
        bg = Image.open(scene1_bg).convert("RGB")
        width, height = bg.size
        ref_path = "/Users/zengcode/projects/autoclip/assets/characters/mamase-presenter-v1.png"
        if os.path.exists(ref_path):
            presenter = Image.open(ref_path).convert("RGBA")
            p_ratio = presenter.width / presenter.height
            p_height = int(height * 0.95)
            p_width = int(p_height * p_ratio)
            presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)
            bg.paste(presenter, (width - p_width - 50, height - p_height), presenter)
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
        bg.save(scene1_out, quality=95)
        os.remove(scene1_bg)
    except Exception as e:
        pass

import concurrent.futures
def run_dl(i):
    out_path = os.path.join(img_dir, f"scene-{i:02d}.png")
    download_pollination(prompts[i], out_path)

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(run_dl, range(2, 17))

print("Done generating images!")
