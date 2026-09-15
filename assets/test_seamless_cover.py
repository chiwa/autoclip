import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

TARGET_W = 1080
TARGET_H = 1920

src = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/media_1789215531601.jpg").convert("RGBA")

# Let us analyze scaling:
# If we scale src to 1080 width, it is 1080x1080.
# The core content (Eris, Explorer, Dog, and Text) is concentrated from x: 0 to 1080, y: 30 to 1000.
# What if we scale src by 1.25x so width is 1350x1350, or scale it to 1080 and extend vertically?
# Extending vertically is much better because it preserves all text, annotations, and borders!

# Let us do a perfect seamless vertical extension:
sq = src.resize((TARGET_W, TARGET_W), Image.Resampling.LANCZOS)

# We place the square at y = 380 (so top has 380px sky, bottom has 460px rock/darkness)
# In Instagram Reels feed (1:1 crop from center), the crop is y: (1920 - 1080)//2 = 420 to 1500.
# Placing sq at y = 420 makes the 1:1 feed crop EXACTLY match the original square image 100%!
paste_y = 420

canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (15, 18, 26, 255))
canvas.paste(sq, (0, paste_y))

# TOP EXTENSION (y: 0 to 420):
# The top row of sq (at paste_y = 420) has color [16, 18, 24] with stars and faint Milky Way dust.
# We extract the top 200px of sq (which is purely starry sky):
top_sky = sq.crop((0, 0, TARGET_W, 200))
# To make it seamlessly continuous upwards, we flip it vertically:
top_sky_flipped = top_sky.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

# Tile upwards into canvas:
canvas.paste(top_sky_flipped, (0, paste_y - 200))
canvas.paste(top_sky, (0, paste_y - 400))

# Now create a smooth feather mask over the seam at paste_y
# Feather zone: paste_y - 80 to paste_y + 80
seam_blend = Image.new("RGBA", (TARGET_W, 160), (0, 0, 0, 0))
# Let us use a linear blur blend across the seam
fade_mask = Image.new("L", (TARGET_W, TARGET_H), 255)
fm_draw = ImageDraw.Draw(fade_mask)

# For the top extension, apply a subtle gradient so it gradually deepens to rich cosmic black at the very top (y=0)
top_vignette = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
tv_draw = ImageDraw.Draw(top_vignette)
for y in range(0, paste_y):
    alpha = int(140 * ((paste_y - y) / float(paste_y)) ** 1.2)
    tv_draw.line([(0, y), (TARGET_W, y)], fill=(6, 8, 12, alpha))
canvas = Image.alpha_composite(canvas, top_vignette)

# Repaste sq cleanly
canvas.paste(sq, (0, paste_y))

# Smooth the seam at paste_y with a feathered gradient of the flipped sky
feather_h = 100
feather_band = top_sky_flipped.crop((0, 200 - feather_h, TARGET_W, 200))
feather_mask = Image.new("L", (TARGET_W, feather_h), 0)
f_draw = ImageDraw.Draw(feather_mask)
for i in range(feather_h):
    f_draw.line([(0, i), (TARGET_W, i)], fill=int(255 * (1.0 - i / float(feather_h))))
canvas.paste(feather_band, (0, paste_y - feather_h), mask=feather_mask)

# BOTTOM EXTENSION (y: 1500 to 1920):
# The bottom of sq at y=1500 is dark rocky foreground with icons.
# We extend down to y=1920 with deep silhouette rocky tone [1, 2, 4]
bot_band = Image.new("RGBA", (TARGET_W, TARGET_H - (paste_y + TARGET_W)), (2, 3, 5, 255))
canvas.paste(bot_band, (0, paste_y + TARGET_W))

# Save preview
final_img = canvas.convert("RGB")
final_img.resize((360, 640)).save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/check_seamless_v2.png")
print("Saved seamless v2 preview")
