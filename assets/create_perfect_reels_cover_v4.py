import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random

# Load original master artwork (1024x1024)
src_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/media_1789215531601.jpg"
img_orig = Image.open(src_path).convert("RGB")
img_1080 = img_orig.resize((1080, 1080), Image.Resampling.LANCZOS)

# 1. Save 1:1 square master cover
img_1080.save("assets/eris_reel/images/eris-cover-square-1x1.png")

# 2. Build 1080x1920 canvas
canvas = Image.new("RGB", (1080, 1920), (3, 4, 7))

# Build top cosmic background (450 height)
top_arr = np.array(img_1080.crop((0, 0, 1080, 50)))
base_col = np.mean(top_arr[:15, :, :], axis=0) # shape (1080, 3)

top_bg_arr = np.zeros((450, 1080, 3), dtype=np.float32)
void_color = np.array([4.0, 5.0, 10.0])

for y in range(450):
    t = y / 449.0
    weight = t ** 1.4
    top_bg_arr[y, :, :] = (1.0 - weight) * void_color + weight * base_col

top_bg = Image.fromarray(np.clip(top_bg_arr, 0, 255).astype(np.uint8))
top_bg = top_bg.filter(ImageFilter.GaussianBlur(radius=6))

# Add fine stars & subtle cosmic dust to the top space
draw_top = ImageDraw.Draw(top_bg)
random.seed(2026)
for _ in range(220):
    sx = random.randint(0, 1079)
    sy = random.randint(0, 420)
    # Density slightly higher along the galactic vertical axis
    if random.random() < 0.4 and (sx < 400 or sx > 850):
        continue
    bright = random.randint(70, 255)
    tint = random.choice([
        (bright, bright, bright),
        (int(bright*0.8), int(bright*0.9), bright), # icy cyan
        (bright, int(bright*0.95), int(bright*0.8)) # warm stellar
    ])
    draw_top.point((sx, sy), fill=tint)
    if bright > 235:
        draw_top.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        draw_top.line([(sx, sy-1), (sx, sy+1)], fill=tint)

canvas.paste(top_bg, (0, 0))

# 3. Build bottom section (from y=1400 to 1920)
# Sample rocky foreground texture from y=800..1000 of img_1080 (where the rugged rocky ridge is)
# In img_1080, the bottom rocks are at rows ~780 to ~980, before the navigation bar.
# Let's crop a slice of pure dark rocky ridge:
# Left side of rocks: (0, 800, 450, 950)
# Right side of rocks: (650, 800, 1080, 950)
# Let's see what the bottom rows of img_1080 have:
# Rows 1020..1080 have the black bar with icons.
# We will blend the bottom of img_1080 smoothly down into a dark atmospheric silhouette foreground!
# At y=1500 (bottom of 1:1 square), the image ends with black bar (RGB ~ 2, 2, 4).
# We can make a rich deep vignette fading seamlessly to (0, 0, 0) at y=1920.

# Let's check the bottom rows (1070..1080) of img_1080:
bot_color = np.array(img_1080.crop((0, 1070, 1080, 1080)))[-1] # shape (1080, 3)
bot_bg_arr = np.zeros((430, 1080, 3), dtype=np.float32)

for y in range(430):
    t = y / 429.0 # 0 at top (meets y=1500), 1 at bottom
    # subtle drop to pure black
    fade = (1.0 - t ** 0.8)
    for c in range(3):
        bot_bg_arr[y, :, c] = bot_color[:, c] * fade

bot_bg = Image.fromarray(np.clip(bot_bg_arr, 0, 255).astype(np.uint8))
canvas.paste(bot_bg, (0, 1490))

# 4. Mask and paste img_1080 at (0, 420)
mask_composite = Image.new("L", (1080, 1080), 255)
draw_m = ImageDraw.Draw(mask_composite)

# Feather top 20 pixels
for y in range(20):
    alpha = int(255 * (y / 19.0))
    draw_m.line([(0, y), (1080, y)], fill=alpha)

# Feather bottom 15 pixels
for y in range(1065, 1080):
    alpha = int(255 * ((1079 - y) / 14.0))
    draw_m.line([(0, y), (1080, y)], fill=alpha)

canvas.paste(img_1080, (0, 420), mask_composite)

# Save high-res master 9:16
canvas.save("assets/eris_reel/images/eris-reels-cover-9x16.png", quality=98)
# Also update scene-01-hook.png for the video package
canvas.save("assets/eris_reel/images/scene-01-hook.png", quality=98)

# Copy to brain for artifact viewing
canvas.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/eris_cover_final_9x16.png")
img_1080.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/eris_cover_final_1x1.png")

print("Generated and saved both 9:16 and 1:1 official master covers!")
