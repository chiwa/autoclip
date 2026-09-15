from PIL import Image

for path in [
    "assets/oort_cloud_reel/images/scene-05-voyager-journey.png",
    "assets/planet_nine_reel/images/scene-08-cosmic-frontier.png",
    "assets/roman_dark_universe_reel/images/scene-01-hook.png",
    "assets/interstellar_space_reel/images/scene-01-hook.png"
]:
    try:
        im = Image.open(path)
        print(path, im.size, im.mode)
    except Exception as e:
        print(path, "error", e)
