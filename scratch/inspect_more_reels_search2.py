from PIL import Image
import os, glob

# Check where dogs appear in ANY image in assets/
for p in sorted(glob.glob("assets/**/*.png", recursive=True)):
    if "outro" in p:
        continue
    # print all scene-01 images
    if "scene-01" in p:
        print(p)
