from PIL import Image

for path in [
    "assets/stellar_flyby_reel/images/scene-01-hook.png",
    "assets/light_year_distance_reel/images/scene-01-hook.png",
    "assets/edge_of_universe_reel/images/scene-01-hook.png",
    "assets/jupiter_as_a_star_reel/images/scene-01-hook.png"
]:
    im = Image.open(path)
    print(path, im.size, im.mode)
