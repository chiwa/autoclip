import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

# Load Eris master
src = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/media_1789215531601.jpg").convert("RGBA")
canvas = src.resize((1080, 1080), Image.Resampling.LANCZOS)

# 1. CLEAN LEFT TEXT AREA COMPLETELY (x: 0..540, y: 120..950)
# We sample dark cosmos from the top (x: 400..600, y: 30..100) and starry void
# Notice behind the text:
# y: 120..600 is deep space / starry cosmos
# y: 600..950 is snowy/rocky ridge terrain
# Let's cleanly paint deep space for y: 120..620:
draw = ImageDraw.Draw(canvas)

# Create a clean cosmos patch for the whole left upper area (x: 0..530, y: 125..620)
space_patch = Image.new("RGBA", (540, 500), (3, 5, 10, 255))
sp_draw = ImageDraw.Draw(space_patch)

random.seed(42)
for _ in range(300):
    sx = random.randint(0, 539)
    sy = random.randint(0, 499)
    b = random.randint(50, 240)
    tint = (b, b, min(255, b + 15), 235)
    sp_draw.point((sx, sy), fill=tint)
    if b > 215 and random.random() < 0.25:
        sp_draw.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        sp_draw.line([(sx, sy-1), (sx, sy+1)], fill=tint)

# Mask for space patch: feather seamlessly on the right into Moon glow
sp_mask = Image.new("L", (540, 500), 255)
m_draw = ImageDraw.Draw(sp_mask)
for x in range(420, 540):
    val = int(255 * (1.0 - (x - 420) / 120.0))
    m_draw.line([(x, 0), (x, 500)], fill=val)

canvas.paste(space_patch, (0, 125), sp_mask)

# For y: 620..940, x: 0..380 (where "ถูกลดชั้น" was), sample the snowy rocky mountains from x: 0..380, y: 580..680
# Notice that at y: 620..940 on the left, it's snowy peaks and dark rocks in the foreground.
# Let's clone clean snowy mountains and dark rocks over the text area!
# In Eris, clean snowy mountain ridge without text is at x: 500..650, y: 570..640
clean_mountains = canvas.crop((500, 565, 660, 635)).resize((380, 70), Image.Resampling.LANCZOS)
clean_rocks = canvas.crop((0, 850, 260, 950)).filter(ImageFilter.GaussianBlur(1))

# Paint over "ถูกลดชั้น" and English text (x: 20..320, y: 640..850)
rock_patch = Image.new("RGBA", (340, 220), (5, 6, 9, 255))
rp_draw = ImageDraw.Draw(rock_patch)
# Add rock texture grain
for _ in range(1200):
    rx = random.randint(0, 339)
    ry = random.randint(0, 219)
    rb = random.randint(8, 35)
    rp_draw.point((rx, ry), fill=(rb, rb+1, rb+3, 255))

# Feather rock patch
rp_mask = Image.new("L", (340, 220), 0)
rpm_draw = ImageDraw.Draw(rp_mask)
for y in range(220):
    for x in range(340):
        # distance from center
        dist_x = min(x, 339 - x)
        dist_y = min(y, 219 - y)
        d = min(dist_x / 30.0, dist_y / 30.0, 1.0)
        rpm_draw.point((x, y), fill=int(255 * d))

canvas.paste(rock_patch, (10, 650), rp_mask)

# 2. CLEAN DYSNOMIA & KUIPER BELT LABELS
# Dysnomia label & line at x: 840..1060, y: 150..220
clean_sky = Image.new("RGBA", (240, 100), (4, 6, 12, 255))
cs_draw = ImageDraw.Draw(clean_sky)
for _ in range(90):
    cs_draw.point((random.randint(0, 239), random.randint(0, 99)), fill=(200, 200, 220, 230))
canvas.paste(clean_sky, (840, 140))

# Dysnomia moon body itself at x: 860..1040, y: 190..340
clean_sky_dys = Image.new("RGBA", (220, 180), (3, 5, 10, 255))
csd_draw = ImageDraw.Draw(clean_sky_dys)
for _ in range(140):
    csd_draw.point((random.randint(0, 219), random.randint(0, 179)), fill=(210, 210, 230, 230))
canvas.paste(clean_sky_dys, (860, 190))

# Kuiper Belt label at x: 860..1060, y: 560..630
clean_sky_kb = Image.new("RGBA", (200, 70), (4, 7, 14, 255))
canvas.paste(clean_sky_kb, (860, 560))

# 3. ADD ORION SPACECRAFT CLEANLY
# We load crop_orion and make a tight alpha cutout
orion = Image.open("assets/crop_orion.png").convert("RGBA")
# Make background pure transparent: space background is RGB < 25
o_data = np.array(orion)
# Create alpha mask based on luminance
r, g, b, a = o_data[:,:,0], o_data[:,:,1], o_data[:,:,2], o_data[:,:,3]
lum = 0.299*r + 0.587*g + 0.114*b
# Foreground spacecraft is bright, background is black space
alpha = np.clip((lum - 16) * 12, 0, 255).astype(np.uint8)
# Clean up edges with morphology / blur
orion_cut = Image.fromarray(o_data)
orion_mask = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1.0))
orion_cut.putalpha(orion_mask)

# Resize to fit in upper-right space (width: 250)
orion_scaled = orion_cut.resize((250, int(orion_cut.height * (250 / orion_cut.width))), Image.Resampling.LANCZOS)
canvas.paste(orion_scaled, (820, 180), orion_scaled)

# 4. ADD TECHNICAL CALLOUTS
draw = ImageDraw.Draw(canvas)
font_callout_h = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 20)
font_callout_t = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 13)

# Orion Callout (Upper Right)
draw.line([(870, 220), (810, 170), (660, 170)], fill=(160, 210, 255, 230), width=2)
draw.ellipse([(867, 217), (873, 223)], fill=(255, 255, 255, 255))
draw.text((660, 128), "Orion Spacecraft", font=font_callout_h, fill=(255, 255, 255, 255))
draw.text((660, 150), "CREW & DEEP SPACE OPERATIONS", font=font_callout_t, fill=(150, 210, 255, 240))

# Lunar South Pole Callout
draw.line([(820, 590), (870, 630), (1050, 630)], fill=(160, 210, 255, 230), width=2)
draw.ellipse([(817, 587), (823, 593)], fill=(255, 255, 255, 255))
draw.text((880, 606), "LUNAR SOUTH POLE", font=font_callout_h, fill=(255, 255, 255, 255))
draw.text((880, 633), "TARGET FOR ARTEMIS IV LANDING", font=font_callout_t, fill=(150, 210, 255, 240))

# 5. RENDER MASTER TYPOGRAPHY (LEFT SIDE)
font_artemis = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 86)
font_roman = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 46)
font_thai_head = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 46)
font_sub_en = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 18)
font_hook_th = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 23)
font_hook_en = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 15)

# A. Title: "ARTEMIS I–V"
for dx in [-2, 0, 2]:
    for dy in [-2, 0, 2]:
        draw.text((45 + dx, 140 + dy), "ARTEMIS", font=font_artemis, fill=(20, 80, 180, 120))
draw.text((45, 140), "ARTEMIS", font=font_artemis, fill=(255, 255, 255, 255))

draw.rounded_rectangle([(420, 152), (515, 218)], radius=10, fill=(25, 60, 130, 220), outline=(130, 190, 255, 255), width=2)
draw.text((435, 154), "I–V", font=font_roman, fill=(255, 255, 255, 255))

# B. Thai Headline
draw.text((45, 245), "แผนกลับดวงจันทร์", font=font_thai_head, fill=(255, 255, 255, 255))
draw.text((45, 302), "ของมนุษย์", font=font_thai_head, fill=(255, 255, 255, 255))
draw.text((45, 360), "ทีละขั้น!", font=font_thai_head, fill=(110, 215, 255, 255))

# C. Subtitle EN
draw.text((45, 432), "Artemis Missions — Step-by-Step Return to the Moon", font=font_sub_en, fill=(190, 220, 245, 240))

# D. Separator
draw.line([(45, 470), (360, 470)], fill=(120, 165, 210, 200), width=2)

# E. Hook Box (Why it matters / Wow Moment)
hook_lines = [
    ("Apollo ถามว่าไปได้ไหม", (255, 255, 255, 240)),
    ("แต่ Artemis จะกลับไปเพื่ออยู่ถาวร", (255, 255, 255, 255)),
    ("และเตรียมก้าวสู่ดาวอังคาร", (130, 220, 255, 255)),
    ("ทำไมคนเหยียบดวงจันทร์ถึงเป็น Artemis IV?", (255, 220, 120, 255)),
]

cur_y = 490
for line, col in hook_lines:
    draw.text((45, cur_y), line, font=font_hook_th, fill=col)
    cur_y += 35

cur_y += 12
draw.text((45, cur_y), "Apollo proved we could reach the Moon.", font=font_hook_en, fill=(160, 190, 220, 220))
cur_y += 22
draw.text((45, cur_y), "Artemis proves we can stay.", font=font_hook_en, fill=(160, 190, 220, 220))

# Save 1:1 square
sq_out = canvas.convert("RGB")
sq_out.save("assets/artemis_reel/images/artemis-cover-square-1x1.png", quality=98)
sq_out.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/artemis_cover_optA_1x1.png", quality=98)

# 6. EXTEND TO 1080x1920 (9:16)
v_canvas = Image.new("RGB", (1080, 1920), (3, 4, 8))

# Top cosmic extension
top_sample = sq_out.crop((0, 0, 1080, 40))
top_col = np.mean(np.array(top_sample)[:10, :, :], axis=0)
top_arr = np.zeros((430, 1080, 3), dtype=np.float32)
for y in range(430):
    t = y / 429.0
    weight = t ** 1.3
    top_arr[y, :, :] = (1.0 - weight) * np.array([3.0, 5.0, 10.0]) + weight * top_col
top_bg = Image.fromarray(np.clip(top_arr, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))
draw_vt = ImageDraw.Draw(top_bg)
for _ in range(180):
    draw_vt.point((random.randint(0, 1079), random.randint(0, 400)), fill=(random.randint(80, 255), random.randint(80, 255), 255))
v_canvas.paste(top_bg, (0, 0))

# Bottom rocky extension
bot_col = np.mean(np.array(sq_out.crop((0, 1070, 1080, 1080))), axis=0)
bot_arr = np.zeros((430, 1080, 3), dtype=np.float32)
for y in range(430):
    t = y / 429.0
    bot_arr[y, :, :] = bot_col * (1.0 - t ** 0.8)
bot_bg = Image.fromarray(np.clip(bot_arr, 0, 255).astype(np.uint8))
v_canvas.paste(bot_bg, (0, 1495))

# Paste square master with soft mask
mask_sq = Image.new("L", (1080, 1080), 255)
md = ImageDraw.Draw(mask_sq)
for y in range(15):
    md.line([(0, y), (1080, y)], fill=int(255 * (y / 15.0)))
for y in range(1065, 1080):
    md.line([(0, y), (1080, y)], fill=int(255 * ((1079 - y) / 14.0)))
v_canvas.paste(sq_out, (0, 420), mask_sq)

# Corner Logo at top right
logo = Image.open("assets/branding/mamase/logo.png").convert("RGBA").resize((190, 190), Image.Resampling.LANCZOS)
v_canvas.paste(logo, (1080 - 190 - 40, 45), logo)

v_canvas.save("assets/artemis_reel/images/artemis-reels-cover-9x16.png", quality=98)
v_canvas.save("assets/artemis_reel/images/scene-01-hook.png", quality=98)
v_canvas.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/artemis_cover_optA_9x16.png", quality=98)

print("Refined Option A built successfully!")
