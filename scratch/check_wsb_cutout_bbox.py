from PIL import Image
import numpy as np

im = Image.open("scratch/wsb_presenter_cutout.png")
arr = np.array(im)
alpha = arr[:, :, 3]
coords = np.argwhere(alpha > 30)
min_y, min_x = coords.min(axis=0)
max_y, max_x = coords.max(axis=0)
print(f"Presenter bbox: x={min_x}..{max_x}, y={min_y}..{max_y}, width={max_x-min_x}, height={max_y-min_y}")

# Crop to bbox
cropped = im.crop((min_x, min_y, max_x + 1, max_y + 1))
cropped.save("scratch/presenter_tight_cutout.png")
print("Saved presenter_tight_cutout.png, size:", cropped.size)
