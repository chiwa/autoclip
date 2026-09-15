from PIL import Image
import numpy as np

# Let's inspect where_space_begins scene-01-hook.png
wsb = Image.open("assets/where_space_begins_reel/images/scene-01-hook.png")
print("WSB size:", wsb.size)

# Also check other reels for clean standing dogs or explorers:
import glob
for p in glob.glob("assets/*reel*/images/*.png") + glob.glob("assets/*reel*/*.png"):
    print(p)

