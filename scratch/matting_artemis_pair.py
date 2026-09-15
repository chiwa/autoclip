from PIL import Image, ImageFilter, ImageDraw
import numpy as np

# Load the Artemis I-V master image
im = Image.open("assets/artemis_reel/images/scene-01-hook.png").convert("RGBA")

# Let's crop the dog and explorer with the surrounding ground:
# In artemis_reel (1080w, 1920h):
# Dog is at x=200..600, y=1200..1700
# Explorer is at x=550..850, y=700..1650
# Ground is at y=1250..1920
# Let's clean the patches on the explorer:
# Left arm patches:
# American flag: x=700..745, y=1060..1105
# Triangle patch: x=700..745, y=1130..1180
# Backpack NASA patch: x=940..980, y=1090..1150
# Text "Same Sky Bigger Tomorrow": x=800..1080, y=1540..1660
# Leader line pointing to moon: x=400..550, y=900..1150
# "LUNAR SOUTH POLE": x=40..400, y=750..880

# Let's inspect coordinates of patches in artemis_reel:
crop_arm = im.crop((680, 1000, 780, 1200))
crop_arm.save("scratch/artemis_crop_arm.png")

crop_bp = im.crop((920, 1050, 1010, 1180))
crop_bp.save("scratch/artemis_crop_bp.png")

print("Saved artemis patch crops.")
