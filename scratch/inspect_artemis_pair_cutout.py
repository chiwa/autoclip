from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# Load the Artemis I-V master
art = Image.open("assets/artemis_reel/images/scene-01-hook.png").convert("RGBA")

# Let's crop the standing explorer and dog:
# Dog: x=210..550, y=1250..1700
# Explorer: x=580..860, y=670..1700
# In local coordinates of art.crop((200, 660, 900, 1720)):
# local width = 700, local height = 1060
crop = art.crop((200, 660, 900, 1720))
arr = np.array(crop)

# Let's inspect local coordinates of:
# 1. American flag on left arm:
# In global: x=650..700, y=1020..1065 -> local: x=450..500, y=360..405
# 2. Triangular patch:
# In global: x=640..685, y=1075..1130 -> local: x=440..485, y=415..470
# 3. "ART" letters:
# In global: x=710..745, y=1010..1035 -> local: x=510..545, y=350..375
# 4. NASA logo on backpack:
# In global: x=820..870, y=1030..1085 -> local: x=620..670, y=370..425
# 5. Text below NASA logo:
# In global: x=810..880, y=1090..1110 -> local: x=610..680, y=430..450
# 6. Text at bottom of backpack:
# In global: x=810..880, y=1210..1235 -> local: x=610..680, y=550..575
# 7. "Same Sky Bigger Tomorrow":
# In global: x=750..1020, y=1450..1650 -> local: x=550..700, y=790..990

# Let's verify these by saving small cutouts around each
crop.crop((430, 340, 680, 580)).save("scratch/test_patches_local.png")
crop.crop((530, 780, 700, 980)).save("scratch/test_text_local.png")
print("Saved local test crops.")
