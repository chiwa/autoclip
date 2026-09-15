from PIL import Image
import numpy as np

im = Image.open("assets/lunar_gateway_reel/images/scene-01-hook.png")
# explorer + dog
crop = im.crop((150, 500, 900, 1850))
crop.save("scratch/full_resolution_standing_pair.png")
print("Saved scratch/full_resolution_standing_pair.png", crop.size)
