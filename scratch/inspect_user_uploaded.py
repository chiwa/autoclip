from PIL import Image
import os, glob

for f in sorted(glob.glob("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/*.jpg")):
    im = Image.open(f)
    print(os.path.basename(f), im.size, im.mode)
