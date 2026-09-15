from PIL import Image
import os, glob

for f in sorted(glob.glob("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/*.jpg")):
    im = Image.open(f)
    bname = os.path.basename(f).replace(".jpg", "")
    thumb = im.resize((400, int(im.height * 400 / im.width)))
    thumb.save(f"scratch/u_{bname}.jpg")
    print(f"Saved scratch/u_{bname}.jpg")
