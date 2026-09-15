import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random

# Load original uploaded image
src_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/media_1789215531601.jpg"
img_orig = Image.open(src_path).convert("RGB") # 1024x1024

# Create high-res square master at 1080x1080
img_1080 = img_orig.resize((1080, 1080), Image.Resampling.LANCZOS)
img_1080.save("assets/eris_reel/images/eris-cover-square-1x1.png")

# Now create vertical 9:16 (1080 x 1920)
# Top 420 px: Cosmic deep space, stars, subtle nebula/glow gradient matching the top of img_1080.
# Center 420..1500 px: Exact 1080x1080 artwork!
# Bottom 1500..1920 px: Rocky textured foreground matching the bottom rocks of img_1080.

canvas = Image.new("RGB", (1080, 1920), (5, 8, 14))

# 1. Analyze the top edge of img_1080 (first 30-50 pixels)
# The top edge is very dark navy/black with fine starlight.
# Let's sample the background color at top:
top_strip = np.array(img_1080.crop((0, 0, 1080, 40)))
avg_top_color = tuple(np.median(top_strip, axis=(0, 1)).astype(int))
print("Avg top color:", avg_top_color)

# Paste the central square
canvas.paste(img_1080, (0, 420))

# 2. Build the top sky (0 to 450)
# Create a smooth gradient from deep cosmic void (3, 5, 10) down to the exact top edge of the image
top_bg = Image.new("RGB", (1080, 450), (4, 6, 11))
draw_top = ImageDraw.Draw(top_bg)

# Add faint cosmic nebula tint and stars in top_bg
random.seed(42)
for _ in range(120):
    sx = random.randint(0, 1079)
    sy = random.randint(0, 400)
    brightness = random.randint(120, 240)
    # slight blue/cyan or warm star tint
    color = random.choice([
        (brightness, brightness, brightness),
        (int(brightness*0.85), int(brightness*0.9), brightness),
        (brightness, int(brightness*0.95), int(brightness*0.8))
    ])
    draw_top.point((sx, sy), fill=color)
    if random.random() < 0.1:
        # slightly larger star
        draw_top.ellipse((sx-1, sy-1, sx+1, sy+1), fill=color)

# Smooth blur for faint background stars
# Paste top_bg onto canvas at (0, 0)
canvas.paste(top_bg, (0, 0))
# Re-paste img_1080 at (0, 420) so the top edge of img_1080 is crisp, but let's check the seam:
# In img_1080, y=0 is row 420 on canvas.
# Does img_1080 have a hard line at y=0? Let's check:
# Actually, img_1080 top row has text ("Mamase PODCAST" and "เรื่องเล่าจากจักรวาล").
# The top background of img_1080 is solid dark black/navy.
# Let's inspect the top edge transition:
edge_y420 = np.array(img_1080.crop((0, 0, 1080, 10)))
print("Top edge min/max/mean:", edge_y420.min(), edge_y420.max(), edge_y420.mean())

# 3. Build bottom rocky terrain (1480 to 1920)
# In img_1080, bottom row has navigation icons ("SCIENCE", "SPACE", "DISCOVERY", etc.) on black background.
# Wait! Let's check the bottom edge of img_1080:
edge_bottom = np.array(img_1080.crop((0, 1070, 1080, 1080)))
print("Bottom edge min/max/mean:", edge_bottom.min(), edge_bottom.max(), edge_bottom.mean())
# The bottom edge of img_1080 is almost pure black! (5, 7, 12)
# So extending downward to 1920 is a rich dark cinematic gradient with subtle textured rocky vignetting.

# Let's fill 1500 to 1920 with smooth deep dark slate/black (matching the bottom strip)
bottom_bg = Image.new("RGB", (1080, 420), tuple(edge_bottom[-1, 540]))
canvas.paste(bottom_bg, (0, 1500))
canvas.paste(img_1080, (0, 420))

canvas.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/check_clean_cover_9x16.png")
print("Saved clean 9:16 cover")
