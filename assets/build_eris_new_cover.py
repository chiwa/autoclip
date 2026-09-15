import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

out_dir = "assets/eris_reel/images"
os.makedirs(out_dir, exist_ok=True)

src_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/media_1789215531601.jpg"
src = Image.open(src_path).convert("RGBA")

# 1. Square 1:1 Master Cover (1080x1080)
sq_1080 = src.resize((TARGET_WIDTH, TARGET_WIDTH), Image.Resampling.LANCZOS)
sq_1080.convert("RGB").save(os.path.join(out_dir, "eris-cover-square-1x1.png"), "PNG")
print("Saved 1:1 square master cover (1080x1080)")

# 2. Vertical 9:16 Reels Cover (1080x1920)
# We place the 1080x1080 square in the optimal vertical window so that:
# - Instagram 1:1 grid preview is perfectly centered
# - Top has seamless deep starry sky extension
# - Bottom has seamless rocky terrain / dark gradient extension for mobile safe area

canvas = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (12, 14, 20, 255))

# Position the 1080x1080 square at y = 420 (exactly centered vertically for 1:1 feed crop: 420 to 1500)
# Actually, let us test y = 360 to 1440 (slightly higher, leaving 480px at bottom for subtitle safe area)
paste_y = 350
canvas.paste(sq_1080, (0, paste_y))

# Top extension (0 to paste_y):
# Sample the top 120px of sq_1080, mirror and blend with starry cosmos
top_sample = sq_1080.crop((0, 0, TARGET_WIDTH, 140))
top_flipped = top_sample.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

# Tile upwards
for curr_y in range(paste_y - 140, -140, -140):
    canvas.paste(top_flipped, (0, max(0, curr_y)))

# Soft gradient blend across the seam at paste_y
blend_top = Image.new("RGBA", (TARGET_WIDTH, 100), (0, 0, 0, 0))
b_draw = ImageDraw.Draw(blend_top)
for i in range(100):
    alpha = int(120 * (1.0 - i / 100.0))
    b_draw.line([(0, i), (TARGET_WIDTH, i)], fill=(12, 14, 20, alpha))
canvas = Image.alpha_composite(canvas, Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0,0,0,0)))
# Paste blending gradient over seam
canvas.paste(top_flipped.filter(ImageFilter.GaussianBlur(8)), (0, 0))
canvas.paste(sq_1080, (0, paste_y))

# Let us do a smooth cosmic extension:
# We create a starry sky canvas for the upper area
starry_top = Image.new("RGBA", (TARGET_WIDTH, paste_y + 60), (10, 12, 18, 255))
# Add subtle stars to the extended top
np.random.seed(42)
s_draw = ImageDraw.Draw(starry_top)
for _ in range(350):
    sx = np.random.randint(0, TARGET_WIDTH)
    sy = np.random.randint(0, paste_y + 40)
    sbright = np.random.randint(140, 255)
    ssize = np.random.choice([1, 1, 1, 2], p=[0.7, 0.15, 0.1, 0.05])
    s_draw.rectangle([sx, sy, sx + ssize - 1, sy + ssize - 1], fill=(sbright, sbright, min(255, sbright + 15), 230))

# Blend starry top with the image top seam
mask_top = Image.new("L", (TARGET_WIDTH, paste_y + 60), 0)
m_draw = ImageDraw.Draw(mask_top)
for y in range(paste_y + 60):
    if y < paste_y - 40:
        val = 255
    elif y <= paste_y + 40:
        val = int(255 * (1.0 - (y - (paste_y - 40)) / 80.0))
    else:
        val = 0
    m_draw.line([(0, y), (TARGET_WIDTH, y)], fill=val)

full_canvas = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (1, 2, 4, 255))
full_canvas.paste(sq_1080, (0, paste_y))
full_canvas.paste(starry_top, (0, 0), mask=mask_top)

# Bottom extension (paste_y + 1080 to TARGET_HEIGHT, i.e., 1430 to 1920):
# The bottom of sq_1080 is dark silhouette rocks and icons.
# We extend the dark rock texture down with a natural vignette to deep space black
bot_ext = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT - (paste_y + 1080) + 40), (1, 2, 4, 255))
b_mask = Image.new("L", (TARGET_WIDTH, TARGET_HEIGHT - (paste_y + 1080) + 40), 0)
bm_draw = ImageDraw.Draw(b_mask)
for y in range(b_mask.height):
    alpha = min(255, int(255 * (y / 40.0)))
    bm_draw.line([(0, y), (TARGET_WIDTH, y)], fill=alpha)

full_canvas.paste(bot_ext, (0, paste_y + 1080 - 40), mask=b_mask)

# Save the 9:16 vertical cover
v_cover = full_canvas.convert("RGB")
v_cover.save(os.path.join(out_dir, "eris-reels-cover-9x16.png"), "PNG")
print("Saved 9:16 vertical Reels cover (1080x1920)")

# Save a mobile preview thumbnail
v_cover.resize((360, 640), Image.Resampling.LANCZOS).save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/check_new_cover_9x16.png")
sq_1080.resize((400, 400), Image.Resampling.LANCZOS).save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/check_new_cover_1x1.png")

print("Generated inspection previews.")
