from PIL import Image
import os

candidates = [
    "light_year_distance_reel", "ton_618_ultramassive_black_hole_reel", 
    "tno-time-capsule-reel", "interstellar_space_reel", 
    "artemis_reel", "lunar_gateway_reel", "parallel_universe_reel"
]

for name in candidates:
    p = f"assets/{name}/images/scene-01-hook.png"
    if os.path.exists(p):
        im = Image.open(p).convert("RGB")
        thumb = im.resize((270, 480))
        thumb.save(f"scratch/thumb_{name}.jpg", quality=80)
        print(f"Saved scratch/thumb_{name}.jpg")

