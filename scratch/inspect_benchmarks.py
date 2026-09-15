from PIL import Image
import os

benchmarks = [
    "assets/iss_why_not_fall_reel/images/scene-01-hook.png",
    "assets/voyager1_reel/images/scene-01-hook.png",
    "assets/branding/mamase/reference/eris-master-reels-visual-reference.jpg",
    "assets/tianwen-2-quasi-satellite-reel/images/scene-01-hook.png"
]

for b in benchmarks:
    if os.path.exists(b):
        im = Image.open(b)
        print(f"{b}: size={im.size}, mode={im.mode}")
    else:
        print(f"{b}: NOT FOUND")
