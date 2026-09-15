from PIL import Image
import os

for p in [
    "assets/stellar_flyby_reel/images/scene-08-mamase-cosmic-voyage.png",
    "assets/eris_reel/images/scene-08-mamase-frontier-payoff.png",
    "assets/interstellar_space_reel/images/scene-08-cosmic-cradle.png",
    "assets/pluto_downgraded_reel/images/scene-08-pluto-charon-payoff.png"
]:
    im = Image.open(p)
    print(p, im.size)
    name = os.path.basename(p).replace(".png", "")
    im.resize((600, int(im.height * 600 / im.width))).save(f"scratch/prev_{name}.jpg")
print("Done.")
