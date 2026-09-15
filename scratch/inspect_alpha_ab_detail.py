from PIL import Image
import numpy as np

im = Image.open("assets/alpha_centauri_reel/raw/alpha_centauri_ab.png")
arr = np.array(im)
print("Shape:", arr.shape)
print("Max value:", arr.max(), "Min value:", arr.min(), "Mean:", arr.mean())
# Find bright regions
bright = (arr > 200).all(axis=2)
coords = np.argwhere(bright)
print("Bright points count:", len(coords))
if len(coords) > 0:
    min_y, min_x = coords.min(axis=0)
    max_y, max_x = coords.max(axis=0)
    print(f"Bright area bbox: x={min_x}..{max_x}, y={min_y}..{max_y}")
