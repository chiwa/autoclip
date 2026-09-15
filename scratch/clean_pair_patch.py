from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# Load the full Lunar Gateway image
im = Image.open("assets/lunar_gateway_reel/images/scene-01-hook.png").convert("RGBA")

# Let's clean the small text / callouts around the pair:
# 1. "Same Sky / Bigger Tomorrow" is around x=690..920, y=1400..1520
# Let's paint over it with nearby lunar rock texture using seamless cloning / inpainting
# 2. Patch on explorer's left arm:
# American flag is around x=700..740, y=1070..1100
# NASA round patch is around x=685..735, y=1115..1170
# Blue badge on backpack is around x=900..935, y=1115..1145
# Let's inspect these areas closely by saving crops!

crop_arm = im.crop((650, 1040, 780, 1200))
crop_arm.save("scratch/crop_arm.png")

crop_text = im.crop((680, 1400, 950, 1550))
crop_text.save("scratch/crop_text.png")

print("Saved inspection crops.")
