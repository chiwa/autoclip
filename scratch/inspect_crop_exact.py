from PIL import Image
import numpy as np

crop = Image.open("scratch/dog_real_crop.png")
arr = np.array(crop)
# Find pixels that have high brown/golden color:
# In RGB: R > 120, G > 80, B < 80 and R > G > B
golden_mask = (arr[:, :, 0] > 110) & (arr[:, :, 1] > 70) & (arr[:, :, 2] < 90) & (arr[:, :, 0] > arr[:, :, 1])
y_indices, x_indices = np.where(golden_mask)
print(f"Golden pixels X range: {x_indices.min()} .. {x_indices.max()}")
print(f"Golden pixels Y range: {y_indices.min()} .. {y_indices.max()}")

# Save the golden mask as an image to see it directly!
mask_img = Image.fromarray((golden_mask * 255).astype(np.uint8))
mask_img.save("scratch/dog_color_mask.png")
print("Saved scratch/dog_color_mask.png")
