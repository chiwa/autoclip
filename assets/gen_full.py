import urllib.parse
import urllib.request
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 1. Generate full integrated image via Pollinations
prompt = "Premium cinematic historical documentary key art. Right side: A handsome Asian adult male presenter with short tousled black hair, wearing thin rectangular glasses and a dark navy field jacket over a black shirt, pointing to the left. He is illuminated by a warm gold and cyan rim light. Left side: Extremely massive glowing 3D cosmic web map of the universe, galaxies connected by dark energy filaments. Deep space navy blue. Volumetric lighting, epic scale."
encoded = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed=888"

bg_path = "/Users/zengcode/projects/autoclip/assets/scene-01-full-ai.png"

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

urllib.request.urlretrieve(url, bg_path)

# 2. Add Typography (Thai text since AI can't generate Thai well)
bg = Image.open(bg_path).convert("RGBA")
width, height = bg.size

try:
    font_title = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 130)
    font_hook = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 110)
except:
    font_title = ImageFont.load_default()
    font_hook = ImageFont.load_default()

text1 = "แผนที่จักรวาล"
text2 = "ใหญ่สุดในประวัติศาสตร์"
pos1 = (60, 150)
pos2 = (60, 320)

# Drop Shadow
shadow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_layer)
s_draw.text((pos1[0]+10, pos1[1]+10), text1, fill=(0, 0, 0, 200), font=font_title)
s_draw.text((pos2[0]+10, pos2[1]+10), text2, fill=(0, 0, 0, 200), font=font_hook)
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(10))
bg.paste(shadow_layer, (0,0), mask=shadow_layer)

# Title Gradient (Gold)
mask1 = Image.new("L", (width, height), 0)
m1_draw = ImageDraw.Draw(mask1)
m1_draw.text(pos1, text1, fill=255, font=font_title)
gradient = Image.new("RGBA", (width, height))
g_draw = ImageDraw.Draw(gradient)
for y in range(height):
    r = int(255 - (y / height) * 50)
    g = int(214 - (y / height) * 80)
    b = int(102 - (y / height) * 80)
    g_draw.line([(0, y), (width, y)], fill=(r, max(g,0), max(b,0), 255))
grad_text = Image.new("RGBA", (width, height))
grad_text.paste(gradient, (0,0), mask=mask1)

# Hook (White)
mask2 = Image.new("L", (width, height), 0)
m2_draw = ImageDraw.Draw(mask2)
m2_draw.text(pos2, text2, fill=255, font=font_hook)
white_text = Image.new("RGBA", (width, height), (255, 255, 255, 255))
white_text.paste(white_text, (0,0), mask=mask2)

# Stroke
stroke_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
stroke_draw = ImageDraw.Draw(stroke_layer)
stroke_draw.text(pos1, text1, font=font_title, fill=(0,0,0,255), stroke_width=6)
stroke_draw.text(pos2, text2, font=font_hook, fill=(0,0,0,255), stroke_width=6)

bg.paste(stroke_layer, (0,0), mask=stroke_layer)
bg.paste(grad_text, (0,0), mask=mask1)
bg.paste(white_text, (0,0), mask=mask2)

out_path = "/Users/zengcode/projects/autoclip/assets/scene-01-full-ai-final.png"
bg.save(out_path, "PNG")
os.system(f"cp {out_path} /Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scene-01-full-ai-final.png")
print("SUCCESS")
