import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import binary_dilation, median_filter

img = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGB")
arr = np.array(img).astype(np.float32)

# Region containing the text on the right: rows 800..1150, cols 580..935
sub = arr[800:1150, 580:935]

# Detect text: letters are bright compared to their local background
# Local mean using uniform filter
from scipy.ndimage import uniform_filter
local_mean = uniform_filter(sub, size=(15, 15, 1))
diff = sub - local_mean
# Letters have positive diff > 25 and high brightness
text_mask = (diff[:, :, 0] > 22) & (diff[:, :, 1] > 22) & (diff[:, :, 2] > 22) & (sub[:, :, 0] > 80)
# Dilate mask slightly by 2 pixels
text_mask_dilated = binary_dilation(text_mask, iterations=3)

# Replace text pixels with median filtered version
sub_median = median_filter(sub, size=(7, 7, 1))
sub[text_mask_dilated] = sub_median[text_mask_dilated]

arr[800:1150, 580:935] = sub
cleaned_img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
cleaned_img.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/test_erased.png")
print("Saved test_erased.png")
