from PIL import Image
import os, glob

for p in sorted(glob.glob("assets/*reel*/images/scene-01-hook.png")):
    name = p.split("/")[1]
    thumb_path = f"scratch/thumb_{name}.jpg"
    if not os.path.exists(thumb_path):
        im = Image.open(p).convert("RGB")
        thumb = im.resize((270, 480))
        thumb.save(thumb_path, quality=80)
        print(f"Generated {thumb_path}")
