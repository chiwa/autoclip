import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random

# Load original master artwork (1024x1024)
src_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/media_1789215531601.jpg"
img_orig = Image.open(src_path).convert("RGB")
img_1080 = img_orig.resize((1080, 1080), Image.Resampling.LANCZOS)

# Create 1080x1920 canvas
canvas = Image.new("RGB", (1080, 1920), (5, 7, 13))

# For the top 420 px:
# We want pure clean dark starry space.
# Instead of column extrusion (which created vertical beams), let's create a smooth 2D radial / gradient glow
# that matches the actual nebula glow at (550, 420) where the Milky Way enters from below!
top_canvas = Image.new("RGB", (1080, 430), (4, 6, 12))
draw_top = ImageDraw.Draw(top_canvas)

# Let's paint a soft diffuse cosmic nebula cone that aligns with the Milky Way dust trail
# In img_1080, the Milky Way trail is centered around x=580, y=0..100, with soft blue/cyan/purple dust.
# We can create a soft diffuse glow centered at (580, 430):
glow_layer = Image.new("RGBA", (1080, 430), (0, 0, 0, 0))
draw_glow = ImageDraw.Draw(glow_layer)

for r in range(350, 0, -5):
    alpha = int(45 * (1.0 - r / 350.0))
    draw_glow.ellipse([580 - r*1.4, 430 - r*0.8, 580 + r*1.4, 430 + r*0.8], fill=(25, 40, 75, alpha))

for r in range(180, 0, -4):
    alpha = int(35 * (1.0 - r / 180.0))
    draw_glow.ellipse([570 - r, 430 - r*0.9, 570 + r, 430 + r*0.9], fill=(45, 60, 95, alpha))

top_canvas = Image.alpha_composite(top_canvas.convert("RGBA"), glow_layer).convert("RGB")
top_canvas = top_canvas.filter(ImageFilter.GaussianBlur(radius=15))

# Add natural crisp stars and fine dust
draw_stars = ImageDraw.Draw(top_canvas)
random.seed(999)
for _ in range(260):
    sx = random.randint(0, 1079)
    sy = random.randint(0, 420)
    bright = random.randint(50, 255)
    tint = random.choice([
        (bright, bright, bright),
        (int(bright*0.82), int(bright*0.9), bright), # icy cyan-blue
        (bright, int(bright*0.96), int(bright*0.82)) # delicate stellar warm
    ])
    draw_stars.point((sx, sy), fill=tint)
    # Give a few brighter stars slight 4-point diffraction
    if bright > 240 and random.random() < 0.3:
        draw_stars.line([(sx-2, sy), (sx+2, sy)], fill=tint)
        draw_stars.line([(sx, sy-2), (sx, sy+2)], fill=tint)
        draw_stars.point((sx, sy), fill=(255, 255, 255))

canvas.paste(top_canvas, (0, 0))

# Bottom background (1480 to 1920) - seamless dark cinematic ground
bottom_canvas = Image.new("RGB", (1080, 440), (2, 3, 5))
canvas.paste(bottom_canvas, (0, 1480))

# Now mask img_1080 with smooth cosine feathering at the top (y=0..25) and bottom (y=1060..1080)
mask = Image.new("L", (1080, 1080), 255)
draw_mask = ImageDraw.Draw(mask)

# Top feather (25 px)
for y in range(25):
    # smooth cosine fade
    alpha = int(255 * (1.0 - np.cos(np.pi * y / 24.0)) / 2.0)
    draw_mask.line([(0, y), (1080, y)], fill=alpha)

# Bottom feather (15 px)
for y in range(1065, 1080):
    t = (1079 - y) / 14.0
    alpha = int(255 * (1.0 - np.cos(np.pi * t)) / 2.0)
    draw_mask.line([(0, y), (1080, y)], fill=alpha)

# Paste img_1080
canvas.paste(img_1080, (0, 420), mask)

# Save final clean versions
final_9x16 = "assets/eris_reel/images/eris-reels-cover-9x16.png"
final_scene01 = "assets/eris_reel/images/scene-01-hook.png"
final_1x1 = "assets/eris_reel/images/eris-cover-square-1x1.png"

canvas.save(final_9x16, quality=98)
canvas.save(final_scene01, quality=98)
img_1080.save(final_1x1, quality=98)

# Save to brain artifacts for display
canvas.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/eris_cover_seamless_master_9x16.png")
img_1080.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/eris_cover_seamless_master_1x1.png")

print("Successfully generated seamless master cover v5!")
