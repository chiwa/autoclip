import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random

# Output directories
out_dir = "assets/artemis_reel/images"
os.makedirs(out_dir, exist_ok=True)
brain_dir = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55"

# 1. Load Eris reference (1024x1024)
eris_src = Image.open(f"{brain_dir}/.user_uploaded/media_1789215531601.jpg").convert("RGBA")
eris_1080 = eris_src.resize((1080, 1080), Image.Resampling.LANCZOS)

# 2. Extract key components from Eris master:
# - Header bar: y: 0..130
header_bar = eris_1080.crop((0, 0, 1080, 130))
# - Footer bar: y: 960..1080
footer_bar = eris_1080.crop((0, 960, 1080, 1080))
# - Host, dog & rocky foreground: y: 550..960
# Notice host is at x: 260..800, y: 550..960
# - Moon on the right: x: 500..1080, y: 120..750

# Let's create a clean canvas of 1080x1080 starting from eris_1080
canvas = eris_1080.copy()

# 3. Clean the text area on the left (x: 20..540, y: 130..820)
# We want to keep the starry cosmos and the left atmospheric rim of the Moon.
# Let's synthesize the cosmic starfield for the text box area with soft blending into the Moon's glow.
text_bg = Image.new("RGBA", (530, 690), (4, 7, 14, 255))
t_draw = ImageDraw.Draw(text_bg)

# Add deep space stars and milky way dust
random.seed(1969)
for _ in range(250):
    sx = random.randint(0, 529)
    sy = random.randint(0, 689)
    bright = random.randint(60, 240)
    tint = random.choice([
        (bright, bright, bright, 240),
        (int(bright*0.8), int(bright*0.9), bright, 240),
        (bright, int(bright*0.95), int(bright*0.85), 240)
    ])
    t_draw.point((sx, sy), fill=tint)
    if bright > 210 and random.random() < 0.2:
        t_draw.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        t_draw.line([(sx, sy-1), (sx, sy+1)], fill=tint)

# Soft gradient on the right of the text_bg to blend into Moon's glow (x around 450..530)
alpha_mask = Image.new("L", (530, 690), 255)
am_draw = ImageDraw.Draw(alpha_mask)
for x in range(430, 530):
    val = int(255 * (1.0 - (x - 430) / 100.0))
    am_draw.line([(x, 0), (x, 690)], fill=val)

# Soft gradient on the bottom to blend into snowy/rocky terrain (y around 600..690)
for y in range(600, 690):
    val_y = 1.0 - (y - 600) / 90.0
    for x in range(430):
        current_val = alpha_mask.getpixel((x, y))
        alpha_mask.putpixel((x, y), int(min(current_val, 255 * val_y)))

# Paste cleaned text area
canvas.paste(text_bg, (20, 130), alpha_mask)

# 4. Remove Dysnomia (x: 880..1050, y: 190..330) and replace with Orion Spacecraft!
# Clean Dysnomia area first with cosmic stars
dys_bg = Image.new("RGBA", (220, 200), (3, 4, 8, 255))
d_draw = ImageDraw.Draw(dys_bg)
for _ in range(80):
    sx = random.randint(0, 219)
    sy = random.randint(0, 199)
    b = random.randint(80, 250)
    d_draw.point((sx, sy), fill=(b, b, b, 240))
dys_mask = Image.new("L", (220, 200), 0)
dm_draw = ImageDraw.Draw(dys_mask)
for r in range(100, 0, -1):
    val = int(255 * (1.0 - (r / 100.0) ** 1.5))
    dm_draw.ellipse([(110 - r, 100 - r), (110 + r, 100 + r)], fill=val)
canvas.paste(dys_bg, (870, 180), dys_mask)

# Load Orion spacecraft
orion_img = Image.open("assets/crop_orion.png").convert("RGBA")
# Resize Orion to fit beautifully in the upper right lunar orbit (~220px width)
orion_w = 230
orion_h = int(orion_img.height * (orion_w / orion_img.width))
orion_resized = orion_img.resize((orion_w, orion_h), Image.Resampling.LANCZOS)

# Create a smooth alpha mask for Orion so its space background blends seamlessly
orion_arr = np.array(orion_resized)
# Orion space background is dark (< 30 intensity)
lum = np.mean(orion_arr[:, :, :3], axis=2)
orion_alpha = np.clip((lum - 12) * 9, 0, 255).astype(np.uint8)
orion_mask = Image.fromarray(orion_alpha).filter(ImageFilter.GaussianBlur(1.2))
canvas.paste(orion_resized, (840, 200), orion_mask)

# 5. Technical callouts:
# A. Orion Spacecraft Callout
callout_draw = ImageDraw.Draw(canvas)
font_callout_title = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 18)
font_callout_sub = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 13)

# Line to Orion
callout_draw.line([(890, 220), (840, 175), (710, 175)], fill=(180, 220, 255, 220), width=2)
callout_draw.ellipse([(888, 218), (894, 224)], fill=(255, 255, 255, 255))
callout_draw.text((710, 135), "Orion Spacecraft", font=font_callout_title, fill=(255, 255, 255, 255))
callout_draw.text((710, 155), "CREW & DEEP SPACE OPERATIONS", font=font_callout_sub, fill=(160, 210, 255, 240))

# B. Lunar South Pole Callout
callout_draw.line([(860, 620), (910, 660), (1050, 660)], fill=(180, 220, 255, 220), width=2)
callout_draw.ellipse([(858, 618), (864, 624)], fill=(255, 255, 255, 255))
callout_draw.text((910, 638), "LUNAR SOUTH POLE", font=font_callout_title, fill=(255, 255, 255, 255))
callout_draw.text((910, 665), "TARGET FOR ARTEMIS IV", font=font_callout_sub, fill=(160, 210, 255, 240))

# 6. Render Premium Typography on the Left
font_artemis = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 86)
font_roman = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 46)
font_thai_head = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 44)
font_sub_en = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 18)
font_hook_th = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 22)
font_hook_en = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 15)

# A. Title: "ARTEMIS"
# Let's create metallic textured / glowing letters for ARTEMIS
title_txt = "ARTEMIS"
# Outer cyan glow
for dx in [-3, 0, 3]:
    for dy in [-3, 0, 3]:
        callout_draw.text((45 + dx, 135 + dy), title_txt, font=font_artemis, fill=(40, 120, 220, 90))
# Inner bright white
callout_draw.text((45, 135), title_txt, font=font_artemis, fill=(255, 255, 255, 255))

# Roman numeral badge "I–V"
callout_draw.rounded_rectangle([(420, 148), (510, 212)], radius=10, fill=(30, 70, 140, 200), outline=(120, 180, 255, 255), width=2)
callout_draw.text((433, 150), "I–V", font=font_roman, fill=(255, 255, 255, 255))

# B. Thai Headline
# "แผนกลับดวงจันทร์"
# "ของมนุษย์"
# "ทีละขั้น!"
callout_draw.text((45, 235), "แผนกลับดวงจันทร์", font=font_thai_head, fill=(255, 255, 255, 255))
callout_draw.text((45, 290), "ของมนุษย์", font=font_thai_head, fill=(255, 255, 255, 255))
callout_draw.text((45, 345), "ทีละขั้น!", font=font_thai_head, fill=(120, 215, 255, 255)) # Cyan highlight

# C. Subtitle EN
callout_draw.text((45, 415), "Artemis Missions — Step-by-Step Return to the Moon", font=font_sub_en, fill=(190, 215, 240, 240))

# D. Thin separator rule
callout_draw.line([(45, 455), (320, 455)], fill=(120, 160, 200, 180), width=2)

# E. Hook Box (Why it matters / Wow Moment)
hook_lines = [
    ("Apollo ถามว่าไปได้ไหม", (255, 255, 255, 240)),
    ("แต่ Artemis จะกลับไปเพื่ออยู่ถาวร", (255, 255, 255, 255)),
    ("และเตรียมก้าวสู่ดาวอังคาร", (140, 220, 255, 255)),
    ("ทำไมคนเหยียบดวงจันทร์ถึงเป็น Artemis IV?", (255, 215, 120, 255)), # Warm golden highlight!
]

cur_y = 475
for line, col in hook_lines:
    callout_draw.text((45, cur_y), line, font=font_hook_th, fill=col)
    cur_y += 34

cur_y += 10
callout_draw.text((45, cur_y), "Apollo proved we could reach the Moon.", font=font_hook_en, fill=(160, 185, 210, 220))
cur_y += 22
callout_draw.text((45, cur_y), "Artemis proves we can stay.", font=font_hook_en, fill=(160, 185, 210, 220))

# 7. Save 1:1 Square Master
sq_master = canvas.convert("RGB")
sq_master_path = os.path.join(out_dir, "artemis-cover-square-1x1.png")
sq_master.save(sq_master_path, quality=98)
sq_master.save(f"{brain_dir}/artemis_cover_square_1x1.png", quality=98)
print("Saved 1:1 Square Master Cover successfully.")

# 8. Build 1080x1920 Vertical Reels Cover (9:16)
# Exactly centered for 1:1 Instagram grid preview (y = 420..1500)
v_canvas = Image.new("RGB", (1080, 1920), (3, 4, 8))

# Top cosmic extension (420px height)
top_sample = sq_master.crop((0, 0, 1080, 40))
top_arr = np.array(top_sample)
base_col = np.mean(top_arr[:10, :, :], axis=0) # shape (1080, 3)

top_bg_arr = np.zeros((430, 1080, 3), dtype=np.float32)
void_color = np.array([3.0, 5.0, 10.0])

for y in range(430):
    t = y / 429.0
    weight = t ** 1.3
    top_bg_arr[y, :, :] = (1.0 - weight) * void_color + weight * base_col

top_bg = Image.fromarray(np.clip(top_bg_arr, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))
draw_vtop = ImageDraw.Draw(top_bg)
random.seed(2028)
for _ in range(180):
    sx = random.randint(0, 1079)
    sy = random.randint(0, 400)
    b = random.randint(80, 255)
    draw_vtop.point((sx, sy), fill=(b, b, min(255, b+20)))

v_canvas.paste(top_bg, (0, 0))

# Bottom rocky extension (1500 to 1920: 420px height)
bot_sample = sq_master.crop((0, 1070, 1080, 1080))
bot_arr = np.array(bot_sample)
bot_col = np.mean(bot_arr, axis=0)

bot_bg_arr = np.zeros((430, 1080, 3), dtype=np.float32)
for y in range(430):
    t = y / 429.0
    fade = (1.0 - t ** 0.8)
    for c in range(3):
        bot_bg_arr[y, :, c] = bot_col[:, c] * fade

bot_bg = Image.fromarray(np.clip(bot_bg_arr, 0, 255).astype(np.uint8))
v_canvas.paste(bot_bg, (0, 1495))

# Paste 1:1 square master with soft feathered edges
mask_sq = Image.new("L", (1080, 1080), 255)
m_draw = ImageDraw.Draw(mask_sq)
for y in range(15):
    m_draw.line([(0, y), (1080, y)], fill=int(255 * (y / 15.0)))
for y in range(1065, 1080):
    m_draw.line([(0, y), (1080, y)], fill=int(255 * ((1079 - y) / 14.0)))

v_canvas.paste(sq_master, (0, 420), mask_sq)

# Also paste Mamase official round logo at top right of vertical Reels view
logo_orig = Image.open("assets/branding/mamase/logo.png").convert("RGBA")
logo_scaled = logo_orig.resize((190, 190), Image.Resampling.LANCZOS)
v_canvas.paste(logo_scaled, (1080 - 190 - 40, 45), logo_scaled)

v_path = os.path.join(out_dir, "artemis-reels-cover-9x16.png")
v_canvas.save(v_path, quality=98)
v_canvas.save(os.path.join(out_dir, "scene-01-hook.png"), quality=98)
v_canvas.save(f"{brain_dir}/artemis_reels_cover_9x16.png", quality=98)

print("Saved 9:16 Vertical Reels Master Cover successfully.")
