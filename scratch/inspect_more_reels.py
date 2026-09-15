from PIL import Image
import os

candidates = [
    "assets/where_space_begins_reel/images/scene-01-hook.png",
    "assets/artemis_ii_far_side_reel/images/scene-01-hook.png",
    "assets/speed_of_light_reel/images/scene-01-hook.png",
    "assets/venus-day-longer-than-year-reel/images/scene-01-hook.png",
    "assets/black_hole_before_galaxy_reel/images/scene-01-hook.png",
    "assets/edge_of_universe_reel/images/scene-01-hook.png",
    "assets/stellar_flyby_reel/images/scene-01-hook.png"
]

for c in candidates:
    if os.path.exists(c):
        im = Image.open(c)
        print(c, im.size)
