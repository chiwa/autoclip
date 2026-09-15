import os
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import rembg
import numpy as np

img_dir = "/Users/zengcode/projects/autoclip/assets/angkor_cinematic_documentary/images"
prompt1 = "Premium cinematic historical documentary key art. Wide landscape of ancient Angkor Wat at its height on the left. Dark monsoon clouds encroaching on the right. Warm sandstone, golden sunrise, deep jungle green, teal shadows. Epic depth, volumetric lighting. No people, empty space on the right side."
encoded_prompt = urllib.parse.quote(prompt1)
url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1920&height=1080&nologo=true&seed=123"

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')]
urllib.request.install_opener(opener)

scene1_bg = os.path.join(img_dir, "scene-01_bg.jpg")
scene1_out = os.path.join(img_dir, "scene-01.png")

print("Downloading Scene 1 Background...")
urllib.request.urlretrieve(url, scene1_bg)
bg = Image.open(scene1_bg).convert("RGB")
width, height = bg.size

print("Removing Background from Presenter...")
ref_path = "/Users/zengcode/projects/autoclip/assets/characters/mamase-presenter-v1.png"
orig_presenter = Image.open(ref_path)
input_array = np.array(orig_presenter)
output_array = rembg.remove(input_array)
presenter = Image.fromarray(output_array).convert("RGBA")

# Resize Presenter
p_ratio = presenter.width / presenter.height
p_height = int(height * 0.95)
p_width = int(p_height * p_ratio)
presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)

# Paste Presenter (with alpha mask)
paste_x = width - p_width - 50
paste_y = height - p_height
bg.paste(presenter, (paste_x, paste_y), mask=presenter)

# Draw Text
draw = ImageDraw.Draw(bg)
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 160)
    font_hook = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 120)
except:
    font_title, font_hook = ImageFont.load_default(), ImageFont.load_default()

# Shadow/Rim text
draw.text((105, 105), "จักรวรรดิขอม", fill=(50, 40, 20), font=font_title)
draw.text((100, 100), "จักรวรรดิขอม", fill=(255, 240, 200), font=font_title)
draw.text((105, 305), "หายไปไหน?", fill=(50, 40, 20), font=font_hook)
draw.text((100, 300), "หายไปไหน?", fill=(255, 240, 200), font=font_hook)

bg.save(scene1_out, "PNG")
print("Saved Scene 01!")
os.remove(scene1_bg)
