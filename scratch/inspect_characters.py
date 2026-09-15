from PIL import Image
import os

for p in ["assets/characters/mamase-presenter-cutout.png", "assets/characters/mamase-presenter-v1.png", "scratch/standing_duo_cutout.png", "scratch/mamase_presenter_cutout.png"]:
    if os.path.exists(p):
        im = Image.open(p)
        print(p, im.size, im.mode)
