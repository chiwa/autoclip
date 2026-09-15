import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random

# Load original image
src_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/media_1789215531601.jpg"
img_orig = Image.open(src_path).convert("RGB") # 1024x1024
img_1080 = img_orig.resize((1080, 1080), Image.Resampling.LANCZOS)

# Create 1080x1920 canvas
canvas = Image.new("RGB", (1080, 1920), (5, 8, 14))

# Let's inspect the top edge of img_1080 across x=0..1080
# Notice that between x=450 and x=750, there is a cosmic nebula/milky way dust trail heading up!
# In img_1080, rows 0..30:
top_arr = np.array(img_1080.crop((0, 0, 1080, 50))) # shape (50, 1080, 3)

# Let's create the top background (height 450, width 1080)
# We can extrapolate the background column colors upwards with a soft natural diffusion + starry sky
top_bg_arr = np.zeros((450, 1080, 3), dtype=np.float32)

# Sample base column gradient from rows 0..20
base_col = np.mean(top_arr[:15, :, :], axis=0) # shape (1080, 3)

# For each row y from 0 to 450:
# At y=450 (which meets y=420 on canvas), color matches base_col.
# At y=0 (very top of phone), color smoothly fades towards deep space black-navy (4, 6, 12).
void_color = np.array([4.0, 6.0, 12.0])

for y in range(450):
    t = y / 449.0 # 0.0 at top, 1.0 at bottom (contact with img_1080)
    # Use smooth easing
    weight = t ** 1.3
    row_colors = (1.0 - weight) * void_color + weight * base_col
    top_bg_arr[y, :, :] = row_colors

top_bg = Image.fromarray(np.clip(top_bg_arr, 0, 255).astype(np.uint8))
# Apply slight horizontal blur to top_bg so there's no harsh column striation
top_bg = top_bg.filter(ImageFilter.GaussianBlur(radius=8))

# Now add delicate starfield and cosmic dust to top_bg
draw_top = ImageDraw.Draw(top_bg)
random.seed(1337)
for _ in range(180):
    sx = random.randint(0, 1079)
    sy = random.randint(0, 420)
    # Density higher around x=500..750 (where Milky Way / nebula continues)
    if random.random() < 0.5 and (sx < 450 or sx > 800):
        continue
    brightness = random.randint(80, 255)
    tint = random.choice([
        (brightness, brightness, brightness),
        (int(brightness*0.8), int(brightness*0.9), brightness), # cyan/blue
        (brightness, int(brightness*0.9), int(brightness*0.75)) # soft warm
    ])
    draw_top.point((sx, sy), fill=tint)
    if brightness > 230:
        draw_top.line([(sx-1, sy), (sx+1, sy)], fill=tint)
        draw_top.line([(sx, sy-1), (sx, sy+1)], fill=tint)

# Paste top_bg onto canvas at (0, 0)
canvas.paste(top_bg, (0, 0))

# For the transition between top_bg and img_1080:
# The top edge of img_1080 is at y=420.
# Let's feather the top 15 pixels of img_1080 using an alpha gradient
mask_top = Image.new("L", (1080, 1080), 255)
draw_mask = ImageDraw.Draw(mask_top)
for y in range(18):
    alpha = int(255 * (y / 17.0))
    draw_mask.line([(0, y), (1080, y)], fill=alpha)

# Also feather the bottom 15 pixels of img_1080 into bottom black
for y in range(1065, 1080):
    alpha = int(255 * ((1079 - y) / 14.0))
    draw_mask.line([(0, y), (1080, y)], fill=alpha)

# Create bottom background (1500 to 1920)
# The bottom of img_1080 is dark rocky vignette (color [2, 3, 5])
bottom_bg = Image.new("RGB", (1080, 420), (2, 3, 6))

# Let's add subtle film grain / dark rock silhouette texture to bottom_bg
draw_bot = ImageDraw.Draw(bottom_bg)
for y in range(420):
    for _ in range(30):
        rx = random.randint(0, 1079)
        val = random.randint(1, 6)
        draw_bot.point((rx, y), fill=(val, val+1, val+2))

canvas.paste(bottom_bg, (0, 1500))

# Paste img_1080 with feathered mask onto canvas at (0, 420)
canvas.paste(img_1080, (0, 420), mask_top)

# Save test result
out_test = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/check_seamless_v3.png"
canvas.save(out_test, quality=98)
print("Saved seamless v3")
