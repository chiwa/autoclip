from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# Load the Artemis I-V master
art = Image.open("assets/artemis_reel/images/scene-01-hook.png").convert("RGBA")

# Let's clean the patches using precise inpainting:
# 1. American flag on left arm:
# In artemis: x=650..700, y=1020..1065
# 2. Triangle patch:
# In artemis: x=640..685, y=1075..1130
# 3. "ART" letters:
# In artemis: x=710..745, y=1010..1035
# 4. NASA logo on backpack:
# In artemis: x=820..870, y=1030..1085
# 5. Text below NASA:
# In artemis: x=810..880, y=1090..1110
# 6. Text at bottom of backpack:
# In artemis: x=810..880, y=1210..1235
# 7. "Same Sky Bigger Tomorrow":
# In artemis: x=750..1020, y=1450..1650

# Let's inspect the exact pixel bounds of the explorer's head & face:
# In artemis: head is around x=660..780, y=700..830
head_crop = art.crop((650, 680, 800, 850))
head_crop.save("scratch/artemis_head.png")
print("Saved scratch/artemis_head.png")
