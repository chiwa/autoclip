import os
import urllib.parse
import urllib.request
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import rembg

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

os.makedirs("/Users/zengcode/projects/autoclip/assets/tno-time-capsule-reel/images", exist_ok=True)
bg_path = "/Users/zengcode/projects/autoclip/assets/tno-time-capsule-reel/images/scene-01-bg.png"

# 1. Generate Cinematic Outer Solar System / TNO & Space Telescopes Background
prompt = (
    "High-budget cinematic science documentary visual, 8k resolution. "
    "A colossal frozen primordial asteroid (Trans-Neptunian Object) floating in the dark outer solar system past Neptune. "
    "Gleaming ice crystals, reddish organic tholin crust, illuminated by distant golden sun glare and soft cyan starlight. "
    "In the upper background, the golden hexagonal mirrors of the James Webb Space Telescope and Hubble space telescope gleam in deep space. "
    "Volumetric cosmic lighting, majestic astronomical depth, clean bottom right, ZERO text, ZERO labels, ZERO watermarks."
)

encoded = urllib.parse.quote(prompt)
seed = 77451
url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed}"

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')]
urllib.request.install_opener(opener)

print("Downloading background...")
for attempt in range(3):
    try:
        urllib.request.urlretrieve(url, bg_path)
        img = Image.open(bg_path)
        if img.size != (TARGET_WIDTH, TARGET_HEIGHT):
            img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            img.save(bg_path, "PNG")
        print("Background downloaded successfully.")
        break
    except Exception as e:
        print(f"Retry {attempt+1}: {e}")
        time.sleep(2)

bg = Image.open(bg_path).convert("RGBA")

# 2. Die-cut Presenter & Apply Cold Space Rim + Gold Glare Lighting
presenter_path = "/Users/zengcode/projects/autoclip/assets/characters/mamase-presenter-v1.png"
orig_p = Image.open(presenter_path)
p_arr = rembg.remove(np.array(orig_p))
presenter = Image.fromarray(p_arr).convert("RGBA")

# Ambient color grade (cool deep navy with subtle warm rim)
enhancer = ImageEnhance.Brightness(presenter)
presenter = enhancer.enhance(0.92)
tint = Image.new("RGBA", presenter.size, (0, 70, 130, 255))
presenter_tinted = Image.blend(presenter, tint, 0.08)
presenter_tinted.putalpha(Image.fromarray(p_arr[:, :, 3]))
presenter = presenter_tinted

# Size and ground bottom-right
p_height = int(TARGET_HEIGHT * 0.57) # ~1094px
p_ratio = presenter.width / presenter.height
p_width = int(p_height * p_ratio)
presenter = presenter.resize((p_width, p_height), Image.Resampling.LANCZOS)

paste_x = TARGET_WIDTH - p_width - 20
paste_y = TARGET_HEIGHT - p_height
bg.paste(presenter, (paste_x, paste_y), mask=presenter)

# 3. Motion-Safe Chonburi Gold Foil Typography
font_chonburi_title = ImageFont.truetype("/Users/zengcode/projects/autoclip/assets/fonts/Chonburi.ttf", 118)
font_chonburi_hook = ImageFont.truetype("/Users/zengcode/projects/autoclip/assets/fonts/Chonburi.ttf", 62)

title_text = "ไทม์แคปซูล 4.5 พันล้านปี"
hook_text = "ความลับยุคกำเนิดระบบสุริยะ?"

dummy_draw = ImageDraw.Draw(bg)
t_bbox = dummy_draw.textbbox((0, 0), title_text, font=font_chonburi_title)
t_w = t_bbox[2] - t_bbox[0]
t_h = t_bbox[3] - t_bbox[1]

h_bbox = dummy_draw.textbbox((0, 0), hook_text, font=font_chonburi_hook)
h_w = h_bbox[2] - h_bbox[0]

# Motion safe positioning (Y: 225px, X: centered with ample margins)
pos_x_title = (TARGET_WIDTH - t_w) // 2
pos_y_title = 225

pos_x_hook = (TARGET_WIDTH - h_w) // 2
pos_y_hook = pos_y_title + 140

# A. Horizontal Lens Flare Line beneath title
flare_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
f_draw = ImageDraw.Draw(flare_layer)
f_y = pos_y_title + int(t_h * 0.90)
f_draw.line([(pos_x_title - 70, f_y), (pos_x_title + t_w + 70, f_y)], fill=(255, 140, 20, 230), width=8)
f_draw.line([(pos_x_title - 20, f_y), (pos_x_title + t_w + 20, f_y)], fill=(255, 240, 160, 255), width=3)
flare_layer = flare_layer.filter(ImageFilter.GaussianBlur(8))
bg.paste(flare_layer, (0, 0), mask=flare_layer)

# B. Warm Radial Glow behind title
glow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
g_draw = ImageDraw.Draw(glow_layer)
g_draw.text((pos_x_title, pos_y_title), title_text, font=font_chonburi_title, fill=(255, 110, 10, 255))
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(28))
bg.paste(glow_layer, (0, 0), mask=glow_layer)

# C. Deep Blurred Drop Shadows
shadow_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_layer)
s_draw.text((pos_x_title + 8, pos_y_title + 12), title_text, font=font_chonburi_title, fill=(0, 0, 0, 255))
s_draw.text((pos_x_hook + 5, pos_y_hook + 8), hook_text, font=font_chonburi_hook, fill=(0, 0, 0, 255))
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(12))
bg.paste(shadow_layer, (0, 0), mask=shadow_layer)
bg.paste(shadow_layer, (0, 0), mask=shadow_layer)

# D. Outer Dark Stroke for Title
stroke_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
st_draw = ImageDraw.Draw(stroke_layer)
st_draw.text((pos_x_title, pos_y_title), title_text, font=font_chonburi_title, fill=(25, 8, 2, 255), stroke_width=9)
bg.paste(stroke_layer, (0, 0), mask=stroke_layer)

# E. Gold Foil Texture Fill
mask_title = Image.new("L", (TARGET_WIDTH, TARGET_HEIGHT), 0)
m_draw = ImageDraw.Draw(mask_title)
m_draw.text((pos_x_title, pos_y_title), title_text, fill=255, font=font_chonburi_title)

gold_canvas = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
gc_draw = ImageDraw.Draw(gold_canvas)

np.random.seed(9999)
noise = np.random.normal(0, 22, (TARGET_HEIGHT, TARGET_WIDTH))

for y in range(pos_y_title - 20, pos_y_title + 160):
    rel = (y - pos_y_title) / 120.0
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

    gc_draw.line([(pos_x_title - 50, y), (pos_x_title + t_w + 50, y)], fill=(r, g, b, 255))

gold_arr = np.array(gold_canvas).astype(np.int16)
for c in range(3):
    gold_arr[:, :, c] = np.clip(gold_arr[:, :, c] + noise * 0.5, 0, 255)
gold_canvas = Image.fromarray(gold_arr.astype(np.uint8))

top_hl = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
th_draw = ImageDraw.Draw(top_hl)
th_draw.text((pos_x_title, pos_y_title - 2), title_text, font=font_chonburi_title, fill=(255, 255, 230, 180), stroke_width=2)
gold_canvas.paste(top_hl, (0, 0), mask=top_hl)

bg.paste(gold_canvas, (0, 0), mask=mask_title)

# F. Hook Text (Chonburi Warm Creamy White)
hook_layer = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
h_draw = ImageDraw.Draw(hook_layer)
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_chonburi_hook, fill=(10, 5, 2, 255), stroke_width=5)
h_draw.text((pos_x_hook, pos_y_hook), hook_text, font=font_chonburi_hook, fill=(255, 250, 240, 255))
bg.paste(hook_layer, (0, 0), mask=hook_layer)

out_file = "/Users/zengcode/projects/autoclip/assets/tno-time-capsule-reel/images/scene-01-hook.png"
bg.convert("RGB").save(out_file, "PNG")
os.system(f"cp {out_file} /Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scene-01-tno-time-capsule.png")
print("SUCCESS_TNO_SCENE01")
