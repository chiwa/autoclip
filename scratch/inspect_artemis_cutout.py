from PIL import Image
import numpy as np

# Load the Artemis I-V master image
art = Image.open("assets/artemis_reel/images/scene-01-hook.png").convert("RGBA")

# Let's crop just the standing explorer and dog:
# Dog: x=210..600, y=1200..1700
# Explorer: x=510..880, y=670..1700
# Let's crop this region (x=200..900, y=660..1720)
crop = art.crop((200, 660, 900, 1720))
crop.save("scratch/artemis_raw_pair_crop.png")
print("Saved scratch/artemis_raw_pair_crop.png")
