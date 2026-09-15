import glob, os
from PIL import Image

for f in glob.glob("assets/*_reel*/images/scene-01-hook*.png"):
    im = Image.open(f)
    print(f"{f}: size={im.size}")
