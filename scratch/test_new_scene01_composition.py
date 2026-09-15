import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

TARGET_W = 1080
TARGET_H = 1920

print("1. Creating base cosmic background...")
# High-altitude Chilean night sky: deep midnight navy gradient
top_color = np.array([2, 5, 14], dtype=np.float32)       # Midnight space
mid_color = np.array([6, 18, 44], dtype=np.float32)      # Deep royal sapphire
bot_color = np.array([4, 10, 22], dtype=np.float32)     # Horizon deep navy

grad = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
for y in range(TARGET_H):
    norm_y = y / float(TARGET_H)
    if norm_y < 0.60:
        t = norm_y / 0.60
        grad[y, :] = top_color * (1.0 - t) + mid_color * t
    else:
        t = (norm_y - 0.60) / 0.40
        grad[y, :] = mid_color * (1.0 - t) + bot_color * t

canvas = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8)).convert("RGBA")

# Add subtle Milky Way dust lane arching across the sky
nebula = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
n_draw = ImageDraw.Draw(nebula)
for r in range(500, 40, -12):
    a = int(22 * (1.0 - r / 500.0))
    n_draw.ellipse([700 - r*1.2, 850 - r*0.8, 700 + r*1.2, 850 + r*0.8], fill=(32, 18, 65, a))
for r in range(380, 30, -10):
    a = int(30 * (1.0 - r / 380.0))
    n_draw.ellipse([660 - r*1.0, 830 - r*0.7, 660 + r*1.0, 830 + r*0.7], fill=(15, 45, 100, a))
nebula = nebula.filter(ImageFilter.GaussianBlur(40))
canvas = Image.alpha_composite(canvas, nebula)

# Multi-colored pinpoint stars
s_draw = ImageDraw.Draw(canvas)
np.random.seed(424)
for _ in range(700):
    sx = np.random.randint(0, TARGET_W)
    sy = np.random.randint(0, 1400)
    b = np.random.randint(75, 255)
    roll = np.random.rand()
    if roll < 0.40:
        tint = (b, int(b * 0.94), int(b * 0.86), 255)
    elif roll < 0.80:
        tint = (int(b * 0.88), int(b * 0.95), b, 255)
    else:
        tint = (b, b, b, 255)
    s_draw.point((sx, sy), fill=tint)
    if b > 232 and sy < 1100:
        s_draw.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        s_draw.line([(sx, sy-1), (sx, sy+1)], fill=tint)

# 2. Add Observatory Elements & Mountain Silhouettes in Lower/Midground
print("2. Adding observatory horizon...")
# Silhouetted Andes mountain ridge along the horizon (around y=1300..1600)
ridge = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
r_draw = ImageDraw.Draw(ridge)
# Soft distant mountain silhouette
m_points = [
    (0, 1380), (180, 1340), (380, 1370), (560, 1310), (740, 1350), (920, 1290), (1080, 1330),
    (1080, 1920), (0, 1920)
]
r_draw.polygon(m_points, fill=(6, 12, 24, 230))

# Distant observatory telescope dome on the mountain ridge at x=780..900, y=1250..1320
# Dome base
r_draw.rectangle([800, 1260, 870, 1310], fill=(12, 22, 38, 255))
# Dome roof (semicircle)
r_draw.ellipse([800, 1230, 870, 1290], fill=(18, 30, 48, 255))
# Slit on dome
r_draw.line([(835, 1232), (835, 1275)], fill=(40, 65, 95, 255), width=3)
# Faint red warning beacon on dome
r_draw.point((835, 1230), fill=(255, 60, 40, 255))

# Soft atmospheric horizon glow
for y in range(1250, 1400):
    a = int(25 * (1.0 - abs(y - 1320) / 70.0))
    r_draw.line([(0, y), (TARGET_W, y)], fill=(20, 50, 90, a))

canvas = Image.alpha_composite(canvas, ridge)

# 3. Hero Subject: Authentic ESO Alpha Centauri A & B (Twin Suns)
print("3. Compositing Alpha Centauri A & B...")
eso_raw = Image.open("assets/alpha_centauri_reel/raw/alpha_centauri_ab.png").convert("RGB")
eso_crop = eso_raw.crop((80, 320, 1170, 920))
arr = np.array(eso_crop).astype(np.float32)

h_eso, w_eso = arr.shape[:2]
Y, X = np.ogrid[:h_eso, :w_eso]
edge_dist = np.minimum(np.minimum(X, w_eso - 1 - X), np.minimum(Y, h_eso - 1 - Y)).astype(np.float32)
feather = np.clip(edge_dist / 90.0, 0, 1)
feather_mask = (1.0 - np.cos(np.pi * feather)) / 2.0
subtracted = np.clip((arr - 22.0) * (255.0 / (255.0 - 22.0)), 0, 255)

lum = 0.299 * subtracted[:, :, 0] + 0.587 * subtracted[:, :, 1] + 0.114 * subtracted[:, :, 2]
alpha = np.clip(lum / 110.0, 0, 1) ** 1.25 * feather_mask * 255.0

# Warm solar color grading
subtracted[:, :, 0] = np.clip(subtracted[:, :, 0] * 1.05, 0, 255)
subtracted[:, :, 1] = np.clip(subtracted[:, :, 1] * 0.95, 0, 255)
subtracted[:, :, 2] = np.clip(subtracted[:, :, 2] * 0.70, 0, 255)

eso_enh = ImageEnhance.Color(Image.fromarray(subtracted.astype(np.uint8))).enhance(1.40)
eso_enh = ImageEnhance.Contrast(eso_enh).enhance(1.25)
clean_stars = eso_enh.convert("RGBA")
clean_stars.putalpha(Image.fromarray(alpha.astype(np.uint8)))

# Position the twin stars in the center-right sky: center at (680, 980)
# Scale to width 750
eso_w = 750
eso_h = int(clean_stars.height * (eso_w / clean_stars.width))
eso_scaled = clean_stars.resize((eso_w, eso_h), Image.Resampling.LANCZOS)

star_x = 650 - eso_w // 2
star_y = 980 - eso_h // 2

# Golden Coronas
corona = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(corona)
c_star_a = (star_x + int(eso_w * 0.35), star_y + int(eso_h * 0.50))
c_star_b = (star_x + int(eso_w * 0.65), star_y + int(eso_h * 0.50))

for r in range(220, 12, -4):
    a = int(50 * (1.0 - r / 220.0))
    c_draw.ellipse([c_star_a[0] - r*1.2, c_star_a[1] - r*1.2, c_star_a[0] + r*1.2, c_star_a[1] + r*1.2], fill=(255, 205, 90, a))
    c_draw.ellipse([c_star_b[0] - r*1.0, c_star_b[1] - r*1.0, c_star_b[0] + r*1.0, c_star_b[1] + r*1.0], fill=(255, 175, 70, a))

corona = corona.filter(ImageFilter.GaussianBlur(22))
canvas = Image.alpha_composite(canvas, corona)
canvas.paste(eso_scaled, (star_x, star_y), eso_scaled)

# Proxima Centauri (red dwarf, 4.24 ly) to the right at (980, 890)
proxima = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
p_draw = ImageDraw.Draw(proxima)
px, py = 980, 890
for r in range(45, 2, -2):
    a = int(85 * (1.0 - r / 45.0))
    p_draw.ellipse([px - r, py - r, px + r, py + r], fill=(255, 65, 30, a))
p_draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 230, 210, 255))
p_draw.line([(px - 12, py), (px + 12, py)], fill=(255, 120, 80, 200), width=2)
p_draw.line([(px, py - 12), (px, py + 12)], fill=(255, 120, 80, 200), width=2)
canvas = Image.alpha_composite(canvas, proxima.filter(ImageFilter.GaussianBlur(1.5)))

# 4. Foreground: Observation Deck with Standing Explorer Duo
print("4. Placing standing Mamase explorer and dog...")
# Observatory deck platform in foreground (wood/metal deck floor from y=1720 to 1920)
deck = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
d_draw = ImageDraw.Draw(deck)
d_draw.rectangle([0, 1720, TARGET_W, 1920], fill=(8, 12, 18, 255))
# Deck railing along y=1680
d_draw.line([(0, 1680), (TARGET_W, 1680)], fill=(30, 42, 58, 255), width=6)
for rx in range(120, TARGET_W, 180):
    d_draw.line([(rx, 1680), (rx, 1720)], fill=(25, 35, 50, 255), width=4)
canvas = Image.alpha_composite(canvas, deck)

# Load Presenter Cutout
p_raw = Image.open("scratch/presenter_tight_cutout.png").convert("RGBA")
# Presenter: height ~820px, positioned on the left at x=0..450, y=1100..1920
p_h = 820
p_w = int(p_raw.width * (p_h / p_raw.height))
p_scaled = p_raw.resize((p_w, p_h), Image.Resampling.LANCZOS)

# Soft shadow behind presenter
p_shadow = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
p_shadow.paste(Image.new("RGBA", (p_w, p_h), (0, 0, 0, 180)), (10, 1105), mask=p_scaled.split()[3])
p_shadow = p_shadow.filter(ImageFilter.GaussianBlur(16))
canvas = Image.alpha_composite(canvas, p_shadow)

# Paste presenter at (0, 1100)
canvas.paste(p_scaled, (0, 1100), p_scaled)

# Load Dog Cutout
dog_raw = Image.open("scratch/voyager_dog_cutout.png").convert("RGBA")
# Dog: height ~420px, positioned beside the presenter at x=320..580, y=1480..1900
d_h = 420
d_w = int(dog_raw.width * (d_h / dog_raw.height))
dog_scaled = dog_raw.resize((d_w, d_h), Image.Resampling.LANCZOS)

# Soft shadow behind dog
d_shadow = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
d_shadow.paste(Image.new("RGBA", (d_w, d_h), (0, 0, 0, 180)), (320, 1490), mask=dog_scaled.split()[3])
d_shadow = d_shadow.filter(ImageFilter.GaussianBlur(12))
canvas = Image.alpha_composite(canvas, d_shadow)

# Paste dog at (310, 1480)
canvas.paste(dog_scaled, (310, 1480), dog_scaled)

# Save test raw base
raw_path = "assets/alpha_centauri_reel/raw/scene-01-hook-raw.png"
os.makedirs("assets/alpha_centauri_reel/raw", exist_ok=True)
canvas.convert("RGB").save(raw_path, quality=98)
print(f"Saved raw base to {raw_path}")

# Preview thumbnail
thumb = canvas.convert("RGB").resize((540, 960))
thumb.save("scratch/test_new_raw_thumb.jpg")
print("Saved preview thumbnail.")
