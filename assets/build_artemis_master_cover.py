import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

out_dir = "assets/artemis_reel/images"
os.makedirs(out_dir, exist_ok=True)

# 1. Load base master reference (1024x1024)
base_src = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/media_1789215531601.jpg").convert("RGBA")
base_1080 = base_src.resize((1080, 1080), Image.Resampling.LANCZOS)

# 2. Let's inspect the left typography area to cleanly repaint with Artemis typography:
# The left area with text is roughly x: 30..560, y: 120..800
# Notice that behind the text is deep starry sky and the subtle left glow of the moon.
# Let's see: we can clean the text area using a dark cosmic patch with authentic stars, 
# or clone/inpaint the cosmic sky, then render crisp vector-quality typography!

print("Base loaded successfully:", base_1080.size)
