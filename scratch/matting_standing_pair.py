from PIL import Image, ImageFilter, ImageDraw
import numpy as np

# Load lunar gateway scene-01
lg = Image.open("assets/lunar_gateway_reel/images/scene-01-hook.png").convert("RGBA")

# In lunar gateway, let's crop the standing explorer and dog:
# The explorer is on the right: x=500..950, y=550..1700
# The dog is in the middle: x=300..650, y=1150..1700
# The lunar terrain is at y=1250..1920
# Let's inspect the exact crop:
pair_crop = lg.crop((320, 520, 950, 1720))
pair_crop.save("scratch/pair_crop_raw.png")
print("Saved pair_crop_raw.png", pair_crop.size)
