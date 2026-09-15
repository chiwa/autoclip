import numpy as np
from PIL import Image

src = Image.open("assets/branding/mamase/reference/eris-master-reels-visual-reference.jpg")
print("Original size:", src.size) # (576, 1024)
# In 576x1024:
# Characters are in lower third:
# x from ~100 to ~480, y from ~560 to ~870
crop_chars = src.crop((90, 560, 480, 870))
crop_chars.save("assets/test_crop_pair.png")
print("Saved test crop pair")
