from PIL import Image, ImageFilter, ImageDraw
import numpy as np

# Load Artemis I-V master image
art = Image.open("assets/artemis_reel/images/scene-01-hook.png").convert("RGBA")

# Dog in Artemis I-V:
# In artemis_reel (1080x1920):
# Dog's head: x=390..520, y=1160..1280
# Dog's chest/back: x=250..500, y=1280..1650
# Dog's tail: x=140..250, y=1550..1700
# Dog sits/stands on the rocks at y=1550..1720.

# Notice how stunning the dog is!
# Let's extract the dog with a precise smooth mask that captures the fur and silhouette:
dog_crop = art.crop((120, 1140, 560, 1750))
dog_np = np.array(dog_crop)

# Let's inspect the crop
dog_crop.save("scratch/dog_raw_crop.png")
print("Saved scratch/dog_raw_crop.png", dog_crop.size)
