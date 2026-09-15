import os
import urllib.parse
import urllib.request
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import rembg

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

bg_path = "/Users/zengcode/projects/autoclip/assets/tno-time-capsule-reel/images/scene-01-bg-tno.png"

# 1. Generate detailed Primordial Asteroid / Kuiper belt background
prompt = (
    "Cinematic science documentary key art, 8k resolution. "
    "A massive detailed icy primordial asteroid in the Kuiper belt past Neptune, "
    "showing realistic surface craters, reddish organic tholin deposits, and glittering water-ice crust. "
    "In the dark cosmic background, the James Webb Space Telescope with glowing gold hexagonal mirrors and distant planet Neptune. "
    "Volumetric starlight, deep space contrast, clean lower right, clean lower center, ZERO text, ZERO watermarks, ZERO labels."
)

encoded = urllib.parse.quote(prompt)
seed = 44882
url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed}"

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')]
urllib.request.install_opener(opener)

print("Downloading better background...")
for attempt in range(3):
    try:
        urllib.request.urlretrieve(url, bg_path)
        img = Image.open(bg_path)
        if img.size != (TARGET_WIDTH, TARGET_HEIGHT):
            img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            img.save(bg_path, "PNG")
        print("Background ready.")
        break
    except Exception as e:
        print(f"Retry {attempt+1}: {e}")
        time.sleep(2)

bg = Image.open(bg_path).convert("RGBA")

# 2. Presenter Die-cut & Lighting Match
presenter_path = "/Users/zengcode/projects/autoclip/assets/characters/mamase-presenter-v1.png"
orig_p = Image.open(presenter_path)
p_arr = rembg.remove(np.array(orig_p))
presenter = Image.fromarray(p_arr).convert("RGBA")

# Ambient color grade
enhancer = ImageEnhance.Brightness(presenter)
presenter = enhancer.enhance(0.92)
tint = Image.new("RGBA", presenter.size, (0, 70, 130, 255))
presenter_tinted = Image.blend(presenter, tint, 0.08)
presenter_tinted.putalpha(Image.fromarray(p_arr[:, :, 3]))
presenter = presenter_tinted

# Size and ground bottom-right
p_height = int(TARGET_HEIGHT * 0.56)
p_ratio = presenter.width / presenter.height
p_width = int(p_height * p_ratio)
presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)

paste_x = TARGET_WIDTH - p_width - 25
paste_y = TARGET_HEIGHT - p_height
bg.paste(presenter, (paste_x, paste_y), mask=presenter)

# 3. Motion-Safe Typography (Compact 2-line layout that NEVER overflows)
# Title Line 1: ไทม์แคปซูล (Gold Foil Chonburi)
# Title Line 2: 4.5 พันล้านปี (Gold Foil Chonburi)
# Hook Line: จำยุคกำเนิดระบบสุริยะ? (Warm Creamy White Chonburi)

font_chonburi_title = ImageFont.truetype("/Users/zengcode/projects/autoclip/assets/fonts/Chonburi.ttf", 130)
font_chonburi_sub = ImageFont.truetype("/Users/zengcode/projects/autoclip/assets/fonts/Chonburi.ttf", 85)
font_chonburi_hook = ImageFont.truetype("/Users/zengcode/projects/autoclip/assets/fonts/Chonburi.ttf", 58)

text_t1 = "ไทม์แคปซูล"
text_t2 = "4.5 พันล้านปี"
text_hook = "จำยุคกำเนิดระบบสุริยะได้?"

dummy_draw = ImageDraw.Draw(bg)
b1 = dummy_draw.textbbox((0, 0), text_t1, font=font_chonburi_title)
w1 = b1[2] - b1[0]
h1 = b1[3] - b1[1]

b2 = dummy_draw.textbbox((0, 0), text_t2, font=font_chonburi_sub)
w2 = b2[2] - b2[0]
h2 = b2[3] - b2[1]

bh = dummy_draw.textbbox((0, 0), text_hook, font=font_chonburi_hook)
wh = bh[2] - bh[0]

# Motion-safe positioning
pos_x1 = (TARGET_WIDTH - w1) // 2
pos_y1 = 200

pos_x2 = (TARGET_WIDTH - w2) // 2
pos_y2 = pos_y1 + 135

pos_xh = (TARGET_WIDTH - wh) // 2
pos_yh = pos_y2 + 105

# A. Flare line beneath the title
flare_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
f_draw = ImageDraw.Draw(flare_layer)
f_y = pos_y2 + int(h2 * 0.95)
f_draw.line([(pos_x2 - 80, f_y), (pos_x2 + w2 + 80, f_y)], fill=(255, 140, 20, 240), width=8)
f_draw.line([(pos_x2 - 20, f_y), (pos_x2 + w2 + 20, f_y)], fill=(255, 240, 160, 255), width=3)
flare_layer = flare_layer.filter(ImageFilter.GaussianBlur(8))
bg.paste(flare_layer, (0, 0), mask=flare_layer)

# B. Warm Radial Glow behind titles
glow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
g_draw = ImageDraw.Draw(glow_layer)
g_draw.text((pos_x1, pos_y1), text_t1, font=font_chonburi_title, fill=(255, 110, 10, 255))
g_draw.text((pos_x2, pos_y2), text_t2, font=font_chonburi_sub, fill=(255, 110, 10, 255))
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(30))
bg.paste(glow_layer, (0, 0), mask=glow_layer)

# C. Deep Drop Shadows
shadow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_layer)
s_draw.text((pos_x1 + 8, pos_y1 + 12), text_t1, font=font_chonburi_title, fill=(0, 0, 0, 255))
s_draw.text((pos_x2 + 6, pos_y2 + 10), text_t2, font=font_chonburi_sub, fill=(0, 0, 0, 255))
s_draw.text((pos_xh + 5, pos_yh + 8), text_hook, font=font_chonburi_hook, fill=(0, 0, 0, 255))
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(12))
bg.paste(shadow_layer, (0, 0), mask=shadow_layer)
bg.paste(shadow_layer, (0, 0), mask=shadow_layer)

# D. Outer Dark Stroke for Gold Titles
stroke_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
st_draw = ImageDraw.Draw(stroke_layer)
st_draw.text((pos_x1, pos_y1), text_t1, font=font_chonburi_title, fill=(25, 8, 2, 255), stroke_width=9)
st_draw.text((pos_x2, pos_y2), text_t2, font=font_chonburi_sub, fill=(25, 8, 2, 255), stroke_width=7)
bg.paste(stroke_layer, (0, 0), mask=stroke_layer)

# E. Gold Foil Texture Fill
mask_title = Image.new("L", (TARGET_WIDTH, TARGET_HEIGHT), 0)
m_draw = ImageDraw.Draw(mask_title)
m_draw.text((pos_x1, pos_y1), text_t1, fill=255, font=font_chonburi_title)
m_draw.text((pos_x2, pos_y2), text_t2, fill=255, font=font_chonburi_sub)

gold_canvas = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
gc_draw = ImageDraw.Draw(gold_canvas)

np.random.seed(8888)
noise = np.random.normal(0, 22, (TARGET_HEIGHT, TARGET_WIDTH))

for y in range(pos_y1 - 20, pos_y2 + 130):
    rel = (y - pos_y1) / 230.0
    rel = max(0.0, min(1.0, rel))
    
    if rel < 0.20:
        r = 255
        g = int(250 - (rel / 0.20) * 35)
        b = int(225 - (rel / 0.20) * 160)
    elif rel < 0.65:
        sub = (rel - 0.20) / 0.45
        r = int(255 - sub * 10)
        g = int(215 - sub * 70)
        b = int(65 - sub * 55)
    else:
        sub = (rel - 0.65) / 0.35
        r = int(245 - sub * 65)
        g = int(145 - sub * 75)
        b = int(10 - sub * 10)

    gc_draw.line([(pos_x1 - 60, y), (pos_x1 + w1 + 60, y)], fill=(r, g, b, 255))

gold_arr = np.array(gold_canvas).astype(np.int16)
for c in range(3):
    gold_arr[:, :, c] = np.clip(gold_arr[:, :, c] + noise * 0.5, 0, 255)
gold_canvas = Image.fromarray(gold_arr.astype(np.uint8))

top_hl = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
th_draw = ImageDraw.Draw(top_hl)
th_draw.text((pos_x1, pos_y1 - 2), text_t1, font=font_chonburi_title, fill=(255, 255, 230, 180), stroke_width=2)
th_draw.text((pos_x2, pos_y2 - 2), text_t2, font=font_chonburi_sub, fill=(255, 255, 230, 180), stroke_width=2)
gold_canvas.paste(top_hl, (0, 0), mask=top_hl)

bg.paste(gold_canvas, (0, 0), mask=mask_title)

# F. Hook Text (Warm Creamy White Chonburi)
hook_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
h_draw = ImageDraw.Draw(hook_layer)
h_draw.text((pos_xh, pos_yh), text_hook, font=font_chonburi_hook, fill=(10, 5, 2, 255), stroke_width=5)
h_draw.text((pos_xh, pos_yh), text_hook, font=font_chonburi_hook, fill=(255, 250, 240, 255))
bg.paste(hook_layer, (0, 0), mask=hook_layer)

out_file = "/Users/zengcode/projects/autoclip/assets/tno-time-capsule-reel/images/scene-01-hook.png"
bg.convert("RGB").save(out_file, "PNG")
os.system(f"cp {out_file} /Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scene-01-tno-time-capsule.png")
print("SUCCESS_TNO_SCENE01_PERFECT")
