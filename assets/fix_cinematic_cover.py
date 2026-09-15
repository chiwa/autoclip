import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

# 1. Reload raw generated masterpiece (768x1376)
src = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/artemis_cover_test_1789221334812.jpg").convert("RGB")
canvas = src.resize((1080, 1920), Image.Resampling.LANCZOS)
W, H = canvas.size

# 2. SEAMLESS CLEANUP OF BOTTOM TEXT AREA (y: 1630 to 1920)
# Instead of tiling small patches, let us do a professional cinematic treatment:
# At y: 1600, the lunar terrain is dark rocky ground.
# From y: 1620 down to 1920, we blend with a continuous dark basaltic rock surface 
# and a smooth, deep cosmic black gradient (RGBA (2, 4, 8)) with subtle lunar dust noise.
# This gives a 100% seamless, rich, deep cinematic floor.

# Create smooth dark gradient floor for y: 1600..1920
floor_h = H - 1600 # 320px
floor = Image.new("RGBA", (W, floor_h), (3, 5, 9, 255))
fl_draw = ImageDraw.Draw(floor)

# Add subtle astrophysical regolith grain/noise
random.seed(1969)
for _ in range(8000):
    gx = random.randint(0, W - 1)
    gy = random.randint(0, floor_h - 1)
    # Brightness higher near top (matching rocks), fading to pitch black at bottom
    fade = 1.0 - (gy / float(floor_h)) ** 0.8
    val = int(random.randint(10, 32) * fade)
    fl_draw.point((gx, gy), fill=(val, val + 1, val + 3, 255))

# Feather top 60px of floor so it blends seamlessly into the lunar ground
floor_mask = Image.new("L", (W, floor_h), 255)
fm_draw = ImageDraw.Draw(floor_mask)
for y in range(60):
    alpha = int(255 * (y / 59.0) ** 1.5)
    fm_draw.line([(0, y), (W, y)], fill=alpha)

canvas.paste(floor, (0, 1600), floor_mask)

# 3. TOP BRANDING
# A. Top Left: Mamase Podcast logo brand
eris_src = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/media_1789215531601.jpg").convert("RGBA")
mamase_logo_brand = eris_src.crop((20, 15, 420, 115)).resize((360, 90), Image.Resampling.LANCZOS)
brand_arr = np.array(mamase_logo_brand)
brand_lum = np.mean(brand_arr[:, :, :3], axis=2)
brand_alpha = np.clip((brand_lum - 15) * 8, 0, 255).astype(np.uint8)
mamase_logo_brand.putalpha(Image.fromarray(brand_alpha))
canvas.paste(mamase_logo_brand, (45, 45), mamase_logo_brand)

# B. Top Right: Official Mamase Round Logo (160x160)
logo_round = Image.open("assets/branding/mamase/logo.png").convert("RGBA").resize((160, 160), Image.Resampling.LANCZOS)
canvas.paste(logo_round, (W - 160 - 45, 45), logo_round)

# C. "เรื่องเล่าจากจักรวาล" positioned neatly to the left of the round logo
draw = ImageDraw.Draw(canvas)
font_universe_th = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 20)
font_universe_en = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 12)
txt_x = W - 160 - 45 - 230 # x ~ 645
draw.text((txt_x, 62), "เรื่องเล่าจากจักรวาล", font=font_universe_th, fill=(255, 255, 255, 245))
draw.text((txt_x, 90), "STORIES FROM THE UNIVERSE", font=font_universe_en, fill=(180, 210, 240, 220))
draw.line([(txt_x, 110), (txt_x + 200, 110)], fill=(140, 185, 230, 180), width=2)

# 4. TECHNICAL CALLOUTS (Positioned with ample breathing room)
font_callout_title = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 20)
font_callout_sub = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 13)

# A. SLS Rocket Callout (Upper Left, pointing to SLS nozzle/body at x: 230, y: 260)
# Place label nicely at x: 50, y: 300
draw.line([(220, 270), (160, 315), (50, 315)], fill=(160, 215, 255, 220), width=2)
draw.ellipse([(217, 267), (223, 273)], fill=(255, 255, 255, 255))
draw.text((50, 265), "SLS Rocket", font=font_callout_title, fill=(255, 255, 255, 255))
draw.text((50, 290), "ARTEMIS I–V LAUNCH VEHICLE", font=font_callout_sub, fill=(150, 210, 255, 240))

# B. Orion Spacecraft Callout (Pointing to Orion at x: 740, y: 230)
# Place label below Orion or to the right: x: 800, y: 340
draw.line([(760, 250), (820, 310), (1010, 310)], fill=(160, 215, 255, 220), width=2)
draw.ellipse([(757, 247), (763, 253)], fill=(255, 255, 255, 255))
draw.text((820, 320), "Orion Spacecraft", font=font_callout_title, fill=(255, 255, 255, 255))
draw.text((820, 345), "CREW & DEEP SPACE OPERATIONS", font=font_callout_sub, fill=(150, 210, 255, 240))

# C. Lunar South Pole Callout (Pointing to Moon's lower limb at x: 520, y: 1015)
draw.line([(520, 1015), (440, 1070), (180, 1070)], fill=(160, 215, 255, 220), width=2)
draw.ellipse([(517, 1012), (523, 1018)], fill=(255, 255, 255, 255))
draw.text((180, 1018), "LUNAR SOUTH POLE", font=font_callout_title, fill=(255, 255, 255, 255))
draw.text((180, 1045), "TARGET FOR ARTEMIS IV LANDING", font=font_callout_sub, fill=(150, 210, 255, 240))

# 5. EDITORIAL TYPOGRAPHY AT BOTTOM (y: 1570 to 1820)
font_title = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 80)
font_head_th = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 46)
font_sub_th = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 26)
font_sub_en = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 17)

title_y = 1580
# Outer glow for title
for dx in [-2, 0, 2]:
    for dy in [-2, 0, 2]:
        draw.text((50 + dx, title_y + dy), "ARTEMIS I–V", font=font_title, fill=(20, 80, 190, 160))
draw.text((50, title_y), "ARTEMIS I–V", font=font_title, fill=(255, 255, 255, 255))

# Thai Headline
draw.text((50, title_y + 88), "แผนกลับดวงจันทร์ทีละขั้น!", font=font_head_th, fill=(115, 220, 255, 255))
draw.text((50, title_y + 145), "แต่ละภารกิจทำอะไร และเมื่อไหร่จะเหยียบจริง?", font=font_sub_th, fill=(255, 255, 255, 240))
draw.text((50, title_y + 185), "Apollo proved we could reach. Artemis proves we can stay.", font=font_sub_en, fill=(170, 205, 240, 220))

# 6. SLOGAN BESIDE DOG (No emoji, use clean text & star dot)
font_slogan = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 24)
draw.text((720, 1490), "Same Sky", font=font_slogan, fill=(255, 255, 255, 220))
draw.text((720, 1522), "Bigger Tomorrow", font=font_slogan, fill=(255, 215, 120, 230))
# Clean golden star dot
draw.ellipse([(930, 1530), (940, 1540)], fill=(255, 215, 120, 240))

# 7. DOCUMENTARY FOOTER BAR (Clean vector-quality rendering at y: 1845..1920)
# Draw subtle separator line
draw.line([(50, 1835), (W - 50, 1835)], fill=(80, 110, 150, 120), width=1)

font_footer = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 15)
font_lang = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 16)

# Render footer sections
footer_items = [
    ("SCIENCE", 70),
    ("SPACE", 240),
    ("DISCOVERY", 400),
    ("FOR A BRIGHTER TOMORROW", 610),
]
for item, ix in footer_items:
    draw.text((ix, 1858), item, font=font_footer, fill=(190, 215, 240, 220))
    if ix < 600:
        draw.line([(ix + 120, 1855), (ix + 120, 1878)], fill=(60, 90, 130, 140), width=1)

# Language pill [ ไทย | EN ]
draw.rounded_rectangle([(W - 190, 1845), (W - 55, 1892)], radius=22, fill=(10, 25, 45, 220), outline=(50, 130, 200, 240), width=2)
draw.text((W - 170, 1855), "ไทย | EN", font=font_lang, fill=(180, 225, 255, 255))

# 8. SAVE FINAL OUTPUTS
final_img = canvas.convert("RGB")
final_img.save("assets/artemis_reel/images/artemis-reels-cover-9x16.png", quality=98)
final_img.save("assets/artemis_reel/images/scene-01-hook.png", quality=98)
final_img.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/artemis_cover_master_9x16.png", quality=98)

# Create 1:1 Square Master (y: 350 to 1430, perfectly framing Moon, Earth, host & dog)
sq_1080 = final_img.crop((0, 350, 1080, 1430))
sq_1080.save("assets/artemis_reel/images/artemis-cover-square-1x1.png", quality=98)
sq_1080.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/artemis_cover_master_1x1.png", quality=98)

print("Fixed Masterpiece Cover saved successfully!")
