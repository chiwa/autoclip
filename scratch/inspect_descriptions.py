from PIL import Image
import os

candidates = [
    "speed_of_light_reel", "venus-day-longer-than-year-reel", 
    "stellar_flyby_reel", "black_hole_before_galaxy_reel", 
    "artemis_ii_far_side_reel", "where_space_begins_reel",
    "jupiter_as_a_star_reel"
]

for name in candidates:
    p = f"assets/{name}/images/scene-01-hook.png"
    if os.path.exists(p):
        im = Image.open(p).convert("RGB")
        thumb = im.resize((270, 480))
        thumb.save(f"scratch/thumb_{name}.jpg", quality=80)
        print(f"Saved scratch/thumb_{name}.jpg")

