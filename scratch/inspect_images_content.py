from PIL import Image
import os, glob

# Check all scene-01 images in assets to see their exact character style:
for p in sorted(glob.glob("assets/**/scene-01*.png", recursive=True)):
    print(p)
