import numpy as np
from PIL import Image, ImageDraw, ImageFilter

crop = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/test_mountain_crop.png").convert("RGBA")
cw, ch = crop.size

# Clean the faint text on the hoodie (x: 15..170, y: 370..560)
# We can sample clean dark fabric from nearby
hoodie_clean = crop.crop((20, 520, 150, 580)).resize((160, 200), Image.Resampling.BICUBIC)
hoodie_clean = hoodie_clean.filter(ImageFilter.GaussianBlur(3))
crop.paste(hoodie_clean, (15, 370))

# Now let us clean the text on the right: "เพราะในจักรวาลนี้..."
# The text is at x: 680..950, y: 280..460
# In this region, the background is the starry Milky Way.
# We can clone the starry sky from the upper-right or blend it out cleanly.
sky_patch = crop.crop((600, 50, 950, 200)).resize((300, 200))
sky_patch = sky_patch.filter(ImageFilter.GaussianBlur(4))
crop.paste(sky_patch, (680, 280))

crop.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/test_clean_crop.png")
print("Saved clean crop")
