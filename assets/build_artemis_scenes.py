import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import random

out_dir = "assets/artemis_reel/images"
os.makedirs(out_dir, exist_ok=True)
W, H = 1080, 1920

# Load official Mamase corner logo
logo_raw = Image.open("assets/branding/mamase/logo.png").convert("RGBA")
# 19% frame width ≈ 205x205 with 36px margin
logo = logo_raw.resize((205, 205), Image.Resampling.LANCZOS)
logo_pos = (W - 205 - 36, 36)

def add_logo(img):
    c = img.convert("RGBA")
    c.paste(logo, logo_pos, logo)
    return c.convert("RGB")

print("Building Artemis scenes 02 to 08...")

# -------------------------------------------------------------
# SCENE 02: Artemis I - SLS Liftoff at Kennedy Space Center
# -------------------------------------------------------------
s2_src = Image.open("assets/artemis_ii_far_side_reel/images/scene-02-launch.png").convert("RGB")
s2_img = add_logo(s2_src.resize((W, H), Image.Resampling.LANCZOS))
s2_img.save(os.path.join(out_dir, "scene-02-artemis-1.png"), quality=98)
print("Scene 02 ready.")

# -------------------------------------------------------------
# SCENE 03: Artemis II - 4 Astronauts Inside Orion Viewing Moon
# -------------------------------------------------------------
s3_src = Image.open("assets/artemis_ii_far_side_reel/images/scene-06-lunar-observation.png").convert("RGB")
s3_img = add_logo(s3_src.resize((W, H), Image.Resampling.LANCZOS))
s3_img.save(os.path.join(out_dir, "scene-03-artemis-2.png"), quality=98)
print("Scene 03 ready.")

# -------------------------------------------------------------
# SCENE 04: Artemis III - Orion & HLS Docking in Low Earth Orbit
# -------------------------------------------------------------
# Base: Beautiful orbital Earth view from voyager1 scene 05 or where space begins
earth_base = Image.open("assets/where_space_begins_reel 3/images/scene-06-iss.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
# Overlay Orion spacecraft
orion_raw = Image.open("assets/artemis_ii_far_side_reel/images/scene-04-outbound.png").convert("RGBA")
orion_crop = orion_raw.crop((180, 320, 900, 1100)) # crop Orion capsule
# create smooth mask for Orion
o_arr = np.array(orion_crop)
o_lum = np.mean(o_arr[:,:,:3], axis=2)
o_mask = Image.fromarray(np.clip((o_lum - 12) * 10, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
orion_crop.putalpha(o_mask)
orion_docking = orion_crop.resize((700, int(orion_crop.height * (700 / orion_crop.width))), Image.Resampling.LANCZOS)

s4_canvas = earth_base.convert("RGBA")
# Paste Orion in upper-mid LEO
s4_canvas.paste(orion_docking, (190, 420), orion_docking)
s4_img = add_logo(s4_canvas)
s4_img.save(os.path.join(out_dir, "scene-04-artemis-3.png"), quality=98)
print("Scene 04 ready.")

# -------------------------------------------------------------
# SCENE 05: Artemis IV - Astronauts on South Pole Lunar Surface
# -------------------------------------------------------------
# Base: Lunar surface from artemis cover
lunar_bg = Image.open("assets/crop_moon.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
# Dark contrast lunar regolith with sharp low-angle lighting
# Let's create an evocative lunar south pole landscape
s5_canvas = Image.new("RGB", (W, H), (2, 3, 6))
# Top half: deep starry space with Earth
earth_disc = Image.open("assets/voyager1_reel/images/scene-05-attowatt-signal-earth.png").crop((200, 50, 880, 730)).resize((340, 340), Image.Resampling.LANCZOS)
# Mask earth
e_mask = Image.new("L", (340, 340), 0)
em_draw = ImageDraw.Draw(e_mask)
em_draw.ellipse([(10, 10), (330, 330)], fill=255)
e_mask = e_mask.filter(ImageFilter.GaussianBlur(2))

s5_canvas.paste(earth_disc, (120, 180), e_mask)

# Add stars to upper sky
s5_draw = ImageDraw.Draw(s5_canvas)
random.seed(2028)
for _ in range(400):
    sx = random.randint(0, W - 1)
    sy = random.randint(0, 850)
    b = random.randint(70, 255)
    s5_draw.point((sx, sy), fill=(b, b, min(255, b+25)))

# Bottom half (y: 800 to 1920): High-contrast lunar south pole cratered surface
lunar_ground = Image.open("assets/crop_chars.png").crop((0, 200, 440, 510)).resize((W, 1120), Image.Resampling.LANCZOS)
# Enhance contrast for harsh solar rim lighting at South Pole
lunar_ground = ImageEnhance.Contrast(lunar_ground).enhance(1.4)
s5_canvas.paste(lunar_ground, (0, 800))

# Add towering commercial lander / Artemis astronauts silhouette against Earth
# Draw Artemis lander structure and solar panels on the right
l_draw = ImageDraw.Draw(s5_canvas)
# Lander body: vertical cylinder (x: 680..860, y: 580..1200)
l_draw.rectangle([(710, 620), (830, 1150)], fill=(220, 225, 235))
# Lander nosecone
l_draw.polygon([(710, 620), (830, 620), (770, 520)], fill=(240, 245, 255))
# Landing legs
l_draw.line([(710, 1100), (620, 1300)], fill=(120, 130, 140), width=8)
l_draw.line([(830, 1100), (920, 1300)], fill=(120, 130, 140), width=8)
l_draw.line([(770, 1120), (770, 1280)], fill=(100, 110, 120), width=6)
# Lander shadow
l_draw.polygon([(620, 1300), (920, 1300), (350, 1450), (200, 1400)], fill=(5, 6, 10))

# 2 Astronauts walking on surface
# Astronaut 1 (x: 480, y: 1240)
l_draw.ellipse([(475, 1240), (495, 1262)], fill=(240, 245, 255)) # helmet
l_draw.rectangle([(470, 1262), (500, 1310)], fill=(230, 235, 245)) # suit torso
l_draw.rectangle([(473, 1310), (484, 1360)], fill=(200, 205, 215)) # leg 1
l_draw.rectangle([(486, 1310), (497, 1360)], fill=(200, 205, 215)) # leg 2
l_draw.line([(480, 1360), (320, 1410)], fill=(10, 12, 18), width=6) # shadow

# Astronaut 2 (x: 530, y: 1250)
l_draw.ellipse([(525, 1250), (545, 1272)], fill=(240, 245, 255))
l_draw.rectangle([(520, 1272), (550, 1318)], fill=(230, 235, 245))
l_draw.rectangle([(523, 1318), (534, 1365)], fill=(200, 205, 215))
l_draw.rectangle([(536, 1318), (547, 1365)], fill=(200, 205, 215))
l_draw.line([(530, 1365), (380, 1415)], fill=(10, 12, 18), width=6)

# Add dramatic horizontal low-sun lens flare across south pole
for i in range(12):
    alpha = int(45 * (1.0 - i / 12.0))
    l_draw.line([(0, 800 - i), (W, 800 - i)], fill=(255, 230, 180))
    l_draw.line([(0, 800 + i), (W, 800 + i)], fill=(255, 230, 180))

s5_img = add_logo(s5_canvas)
s5_img.save(os.path.join(out_dir, "scene-05-artemis-4.png"), quality=98)
print("Scene 05 ready.")

# -------------------------------------------------------------
# SCENE 06: Artemis V - Lunar Gateway Station in Lunar Orbit
# -------------------------------------------------------------
# Base: Massive Moon limb from artemis cover with solar panels and station
s6_canvas = Image.new("RGB", (W, H), (2, 4, 8))
# Giant Moon in lower/middle frame
moon_large = Image.open("assets/crop_moon.png").convert("RGB").resize((1300, 1300), Image.Resampling.LANCZOS)
s6_canvas.paste(moon_large, (-110, 550))

# Upper deep space
s6_draw = ImageDraw.Draw(s6_canvas)
random.seed(2029)
for _ in range(300):
    sx = random.randint(0, W - 1)
    sy = random.randint(0, 600)
    b = random.randint(80, 255)
    s6_draw.point((sx, sy), fill=(b, b, min(255, b+20)))

# Paste Lunar Gateway station in upper-mid orbit (x: 320, y: 280)
# We can use the high-detail spacecraft model with solar wings
gateway = orion_crop.resize((480, int(orion_crop.height * (480 / orion_crop.width))), Image.Resampling.LANCZOS)
# Add gold solar wings for Gateway
g_draw = ImageDraw.Draw(gateway)
# Draw Gateway gold solar array wings
g_draw.rectangle([(20, 100), (140, 160)], fill=(240, 180, 40), outline=(255, 255, 255))
g_draw.rectangle([(340, 100), (460, 160)], fill=(240, 180, 40), outline=(255, 255, 255))
s6_canvas.paste(gateway.convert("RGB"), (300, 240), gateway.split()[3])

s6_img = add_logo(s6_canvas)
s6_img.save(os.path.join(out_dir, "scene-06-artemis-5.png"), quality=98)
print("Scene 06 ready.")

# -------------------------------------------------------------
# SCENE 07: Moon to Mars - Red Planet Mars Destination
# -------------------------------------------------------------
s7_src = Image.open("assets/starship_v3_flight_12_reel/scene-09-moon-mars-refueling-future.png").convert("RGB")
s7_img = add_logo(s7_src.resize((W, H), Image.Resampling.LANCZOS))
s7_img.save(os.path.join(out_dir, "scene-07-moon-to-mars.png"), quality=98)
print("Scene 07 ready.")

# -------------------------------------------------------------
# SCENE 08: Climax - Grand Panoramic Earth & Moon in Deep Space
# -------------------------------------------------------------
# Authentic Earthrise / Earth & Moon vista
s8_canvas = Image.new("RGB", (W, H), (1, 2, 5))
s8_draw = ImageDraw.Draw(s8_canvas)
# Starfield
random.seed(1968)
for _ in range(450):
    sx = random.randint(0, W - 1)
    sy = random.randint(0, H - 1)
    b = random.randint(60, 255)
    s8_draw.point((sx, sy), fill=(b, b, min(255, b+20)))

# Glowing Earth in upper frame
earth_climax = Image.open("assets/voyager1_reel/images/scene-05-attowatt-signal-earth.png").crop((150, 40, 930, 820)).resize((580, 580), Image.Resampling.LANCZOS)
em_mask = Image.new("L", (580, 580), 0)
ImageDraw.Draw(em_mask).ellipse([(10, 10), (570, 570)], fill=255)
em_mask = em_mask.filter(ImageFilter.GaussianBlur(3))
s8_canvas.paste(earth_climax, (250, 160), em_mask)

# Moon in lower-right frame
moon_climax = Image.open("assets/crop_moon.png").convert("RGB").resize((700, 700), Image.Resampling.LANCZOS)
mm_mask = Image.new("L", (700, 700), 0)
ImageDraw.Draw(mm_mask).ellipse([(15, 15), (685, 685)], fill=255)
mm_mask = mm_mask.filter(ImageFilter.GaussianBlur(3))
s8_canvas.paste(moon_climax, (300, 1050), mm_mask)

s8_img = add_logo(s8_canvas)
s8_img.save(os.path.join(out_dir, "scene-08-new-era-climax.png"), quality=98)
print("Scene 08 ready.")

# -------------------------------------------------------------
# SCENE 09: Locked Outro (Byte-for-byte exact copy)
# -------------------------------------------------------------
import shutil
shutil.copyfile("assets/branding/mamase/reels-end-scene.png", os.path.join(out_dir, "scene-09-mamase-outro.png"))
print("Scene 09 locked outro copied.")

print("All Artemis scenes 01 to 09 successfully created!")
