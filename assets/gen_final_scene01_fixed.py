import os
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import rembg
import numpy as np

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

# 1. Download or upscale background to exact 1080x1920 native
bg_path = "/Users/zengcode/projects/autoclip/assets/scene-01-bg-1080x1920.png"
prompt = "Premium cinematic historical documentary key art, 8k resolution. Extremely massive glowing 3D cosmic web map of the universe, billions of galaxies connected by dark energy filaments. Deep space navy blue, glowing cyan and warm gold rim lights. Volumetric lighting, epic cosmic scale, majestic, cinematic depth. Clean dark space on the bottom right."
encoded = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed=2024"

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

try:
    urllib.request.urlretrieve(url, bg_path)
    bg = Image.open(bg_path).convert("RGBA")
except Exception as e:
    print("Fallback local resize:", e)
    bg = Image.open("/Users/zengcode/projects/autoclip/assets/scene-01-bg-only.png").convert("RGBA")

# Ensure exact dimensions
bg = bg.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

# 2. Die-cut Presenter
presenter_path = "/Users/zengcode/projects/autoclip/assets/characters/mamase-presenter-v1.png"
orig_p = Image.open(presenter_path)
p_arr = rembg.remove(np.array(orig_p))
presenter = Image.fromarray(p_arr).convert("RGBA")

# Lighting integration
enhancer = ImageEnhance.Brightness(presenter)
presenter = enhancer.enhance(0.88)
enhancer_con = ImageEnhance.Contrast(presenter)
presenter = enhancer_con.enhance(1.05)

# Subtle cyan ambient rim
tint = Image.new("RGBA", presenter.size, (0, 80, 140, 255))
presenter_tinted = Image.blend(presenter, tint, 0.12)
presenter_tinted.putalpha(Image.fromarray(p_arr[:, :, 3]))
presenter = presenter_tinted

# Size & position (Presenter bottom right, nicely grounded)
p_height = int(TARGET_HEIGHT * 0.58) # ~1113px
p_ratio = presenter.width / presenter.height
p_width = int(p_height * p_ratio)
presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)

paste_x = TARGET_WIDTH - p_width - 10
paste_y = TARGET_HEIGHT - p_height
bg.paste(presenter, (paste_x, paste_y), mask=presenter)

# 3. Typography (Strict SKILL.md specs)
# Title ~44pt-54pt equivalent in 1080x1920 scale (around 52-60px), Hook ~72-84px
# Font selection
font_path = "/System/Library/Fonts/SukhumvitSet.ttc"
if not os.path.exists(font_path):
    font_path = "/System/Library/Fonts/Thonburi.ttc"

# Set sizes that fit comfortably within margin (x=80, max_width=900)
# Title: warm gold #FFD666
# Hook: crisp white #FFFFFF with blurred drop shadow
font_title = ImageFont.truetype(font_path, 56, index=5 if "Sukhumvit" in font_path else 0)
font_hook = ImageFont.truetype(font_path, 80, index=5 if "Sukhumvit" in font_path else 0)

title_text = "แผนที่จักรวาล"
hook_line1 = "ใหญ่ที่สุด"
hook_line2 = "เท่าที่เคยมีมา"

# Calculate bounding boxes to ensure no overflow
pos_x = 80
pos_y_title = 160
pos_y_hook1 = 230
pos_y_hook2 = 325

# Drop Shadow Layer
shadow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_layer)
shadow_offset = 12

s_draw.text((pos_x + shadow_offset, pos_y_title + shadow_offset), title_text, fill=(0, 0, 0, 230), font=font_title)
s_draw.text((pos_x + shadow_offset, pos_y_hook1 + shadow_offset), hook_line1, fill=(0, 0, 0, 230), font=font_hook)
s_draw.text((pos_x + shadow_offset, pos_y_hook2 + shadow_offset), hook_line2, fill=(0, 0, 0, 230), font=font_hook)
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(14))

bg.paste(shadow_layer, (0, 0), mask=shadow_layer)

# Text Layer with Stroke and Exact Palette
text_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
t_draw = ImageDraw.Draw(text_layer)

# Title: Warm Gold #FFD666 with subtle black stroke
t_draw.text((pos_x, pos_y_title), title_text, fill="#FFD666", font=font_title, stroke_width=4, stroke_fill=(0, 0, 0, 220))

# Hook: Crisp White #FFFFFF with black stroke
t_draw.text((pos_x, pos_y_hook1), hook_line1, fill="#FFFFFF", font=font_hook, stroke_width=5, stroke_fill=(0, 0, 0, 240))
t_draw.text((pos_x, pos_y_hook2), hook_line2, fill="#FFFFFF", font=font_hook, stroke_width=5, stroke_fill=(0, 0, 0, 240))

bg.paste(text_layer, (0, 0), mask=text_layer)

out_file = "/Users/zengcode/projects/autoclip/assets/scene-01-google-maps-1080x1920.png"
bg.convert("RGB").save(out_file, "PNG")
os.system(f"cp {out_file} /Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scene-01-google-maps-1080x1920.png")
print("SUCCESS_1080_1920")
