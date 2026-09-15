import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

# 1. Load raw generated masterpiece (768x1376)
src = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/artemis_cover_test_1789221334812.jpg").convert("RGB")

# Scale to 1080x1920 (exact 9:16 Reels resolution)
canvas = src.resize((1080, 1920), Image.Resampling.LANCZOS)
W, H = canvas.size # 1080, 1920

# 2. Inpaint / Clean the bottom text area (y: 1600 to 1920)
# In 1080x1920, the host's shoes are at y ~ 1560, dog paws at y ~ 1580.
# The AI text starts at y ~ 1660 down to 1920.
# Between y: 1540 and 1650, there are gorgeous, high-contrast dark lunar rocks!
# We can sample multiple rocky texture patches from y: 1530..1640 (left, center, right) 
# and blend them over y: 1650..1920, fading gracefully to deep dark regolith / vignette at the bottom!

# Sample rocky slices
rock_left = canvas.crop((40, 1540, 400, 1630))
rock_mid = canvas.crop((400, 1540, 750, 1630))
rock_right = canvas.crop((750, 1540, 1040, 1630))

# Build clean rocky foreground
rock_canvas = canvas.copy()
draw_r = ImageDraw.Draw(rock_canvas)

# Fill y: 1660..1920 with seamless blended dark rocks
for curr_y in range(1650, 1920, 70):
    # Paste flipped / jittered rock patches
    p_left = rock_left.transpose(Image.Transpose.FLIP_LEFT_RIGHT).resize((400, 80), Image.Resampling.LANCZOS)
    p_mid = rock_mid.resize((400, 80), Image.Resampling.LANCZOS)
    p_right = rock_right.transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((350, 80), Image.Resampling.LANCZOS)
    
    # Apply soft vertical fade factor as we go lower
    depth_factor = max(0.2, 1.0 - (curr_y - 1650) / 320.0)
    
    rock_canvas.paste(p_left, (20, curr_y))
    rock_canvas.paste(p_mid, (380, curr_y))
    rock_canvas.paste(p_right, (740, curr_y))

# Add natural dark vignette to bottom 250px so text & icons pop with maximum readability
vignette = Image.new("RGBA", (W, 350), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
for y in range(350):
    alpha = int(245 * (y / 349.0) ** 1.2)
    v_draw.line([(0, y), (W, y)], fill=(3, 5, 8, alpha))

canvas = Image.alpha_composite(rock_canvas.convert("RGBA"), Image.new("RGBA", (W, H), (0,0,0,0)))
canvas.paste(vignette, (0, H - 350), vignette)

# 3. Add Top Branding:
# A. Top Left: Mamase Podcast branding (from Eris)
eris_src = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/media_1789215531601.jpg").convert("RGBA")
# Crop Mamase Podcast logo text from Eris (x: 20..420, y: 15..110 in 1024x1024)
mamase_logo_brand = eris_src.crop((20, 15, 420, 115)).resize((380, 95), Image.Resampling.LANCZOS)

# Create alpha mask for brand logo (black background becomes transparent)
brand_arr = np.array(mamase_logo_brand)
brand_lum = np.mean(brand_arr[:, :, :3], axis=2)
brand_alpha = np.clip((brand_lum - 15) * 8, 0, 255).astype(np.uint8)
mamase_logo_brand.putalpha(Image.fromarray(brand_alpha))

canvas.paste(mamase_logo_brand, (45, 45), mamase_logo_brand)

# B. Top Right: Official Mamase Round Logo + "เรื่องเล่าจากจักรวาล"
logo_round = Image.open("assets/branding/mamase/logo.png").convert("RGBA").resize((170, 170), Image.Resampling.LANCZOS)
canvas.paste(logo_round, (W - 170 - 45, 45), logo_round)

# Stories from Universe text
draw = ImageDraw.Draw(canvas)
font_universe_th = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 20)
font_universe_en = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 13)
draw.text((W - 170 - 240, 60), "เรื่องเล่าจากจักรวาล", font=font_universe_th, fill=(255, 255, 255, 240))
draw.text((W - 170 - 240, 88), "STORIES FROM THE UNIVERSE", font=font_universe_en, fill=(180, 210, 240, 220))
draw.line([(W - 170 - 240, 108), (W - 170 - 60, 108)], fill=(150, 190, 230, 180), width=2)

# 4. Add Technical Callouts with Leader Lines
font_callout_title = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 22)
font_callout_sub = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 14)

# SLS Rocket Callout (Upper Left, pointing to SLS)
# SLS is at x ~ 230, y ~ 260
draw.line([(240, 250), (180, 210), (50, 210)], fill=(160, 215, 255, 230), width=2)
draw.ellipse([(237, 247), (243, 253)], fill=(255, 255, 255, 255))
draw.text((50, 160), "SLS Rocket", font=font_callout_title, fill=(255, 255, 255, 255))
draw.text((50, 185), "ARTEMIS I–V LAUNCH VEHICLE", font=font_callout_sub, fill=(150, 210, 255, 240))

# Orion Spacecraft Callout (Upper Right, pointing to Orion)
# Orion is at x ~ 740, y ~ 230
draw.line([(740, 230), (810, 200), (950, 200)], fill=(160, 215, 255, 230), width=2)
draw.ellipse([(737, 227), (743, 233)], fill=(255, 255, 255, 255))
draw.text((810, 150), "Orion Spacecraft", font=font_callout_title, fill=(255, 255, 255, 255))
draw.text((810, 175), "CREW & DEEP SPACE OPERATIONS", font=font_callout_sub, fill=(150, 210, 255, 240))

# Lunar South Pole Callout (Pointing to Moon's lower edge)
# Moon lower limb is at x ~ 540, y ~ 1030
draw.line([(520, 1010), (450, 1060), (220, 1060)], fill=(160, 215, 255, 230), width=2)
draw.ellipse([(517, 1007), (523, 1013)], fill=(255, 255, 255, 255))
draw.text((220, 1010), "LUNAR SOUTH POLE", font=font_callout_title, fill=(255, 255, 255, 255))
draw.text((220, 1035), "TARGET FOR ARTEMIS IV LANDING", font=font_callout_sub, fill=(150, 210, 255, 240))

# 5. Add Master Editorial Typography at the Bottom (y: 1570 to 1820)
# This is prominently positioned above the bottom footer bar, perfectly visible in Reels!
font_title = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 78)
font_head_th = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 46)
font_sub_th = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 26)
font_sub_en = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 18)

# Title: "ARTEMIS I–V"
title_y = 1580
# Glow
for dx in [-2, 0, 2]:
    for dy in [-2, 0, 2]:
        draw.text((50 + dx, title_y + dy), "ARTEMIS I–V", font=font_title, fill=(30, 90, 200, 140))
draw.text((50, title_y), "ARTEMIS I–V", font=font_title, fill=(255, 255, 255, 255))

# Thai Headline
draw.text((50, title_y + 85), "แผนกลับดวงจันทร์ทีละขั้น!", font=font_head_th, fill=(120, 220, 255, 255)) # Cyan pop
draw.text((50, title_y + 140), "แต่ละภารกิจทำอะไร และเมื่อไหร่จะเหยียบจริง?", font=font_sub_th, fill=(255, 255, 255, 240))
draw.text((50, title_y + 178), "Apollo proved we could reach. Artemis proves we can stay.", font=font_sub_en, fill=(170, 205, 240, 220))

# 6. Add Slogan beside dog
font_slogan = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 24)
draw.text((720, 1500), "Same Sky", font=font_slogan, fill=(255, 255, 255, 220))
draw.text((720, 1530), "Bigger Tomorrow 🐾", font=font_slogan, fill=(255, 215, 120, 230))

# 7. Add Bottom Documentary Footer Bar (y: 1840 to 1920)
footer_src = eris_src.crop((0, 960, 1024, 1024)).resize((1080, 80), Image.Resampling.LANCZOS)
f_arr = np.array(footer_src)
f_lum = np.mean(f_arr[:, :, :3], axis=2)
f_alpha = np.clip((f_lum - 10) * 8, 0, 255).astype(np.uint8)
footer_src.putalpha(Image.fromarray(f_alpha))
canvas.paste(footer_src, (0, 1835), footer_src)

# Save final 9:16 vertical cover
final_cover = canvas.convert("RGB")
final_cover.save("assets/artemis_reel/images/artemis-reels-cover-9x16.png", quality=98)
final_cover.save("assets/artemis_reel/images/scene-01-hook.png", quality=98)
final_cover.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/artemis_cover_cinematic_9x16.png", quality=98)

# Also create 1:1 square crop (centered on the Moon and characters: y = 300 to 1380 or y = 420 to 1500)
sq_1080 = final_cover.crop((0, 420, 1080, 1500))
sq_1080.save("assets/artemis_reel/images/artemis-cover-square-1x1.png", quality=98)
sq_1080.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/artemis_cover_cinematic_1x1.png", quality=98)

print("Cinematic Artemis Masterpiece Cover rendered successfully!")
