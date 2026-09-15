from PIL import Image
import numpy as np

crop = Image.open("scratch/dog_real_crop.png")
arr = np.array(crop)

# In the shadow of the dog's body, R is lower (around 40..100), but R > G and R > B, and G > B.
# Let's inspect RGB values across the dog's body at x=200, y=200..400:
for y in range(200, 420, 20):
    print(f"y={y}, x=200: RGB={arr[y, 200, :3]}")

# Also check the gray lunar ground at x=100, y=200..400:
for y in range(200, 420, 20):
    print(f"y={y}, x=100 (ground): RGB={arr[y, 100, :3]}")

