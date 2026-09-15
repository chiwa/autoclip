from PIL import Image

def analyze_image(path):
    im = Image.open(path)
    print(f"=== {path} ===")
    print("Size:", im.size)
    # Check bounding boxes or save slices
    # Let's crop top, middle, bottom
    w, h = im.size
    top = im.crop((0, 0, w, 600))
    mid = im.crop((0, 500, w, 1300))
    bot = im.crop((0, 1200, w, h))
    top.save(f"scratch/{os.path.basename(path)}_top.jpg", quality=85)
    mid.save(f"scratch/{os.path.basename(path)}_mid.jpg", quality=85)
    bot.save(f"scratch/{os.path.basename(path)}_bot.jpg", quality=85)

import os
analyze_image("assets/iss_why_not_fall_reel/images/scene-01-hook.png")
analyze_image("assets/voyager1_reel/images/scene-01-hook.png")
print("Done saving slices.")
