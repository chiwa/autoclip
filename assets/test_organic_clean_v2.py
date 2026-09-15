import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter, binary_dilation, median_filter

img = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGB")
arr = np.array(img).astype(np.float32)

sub = arr[800:1160, 560:935]
local_mean = uniform_filter(sub, size=(15, 15, 1))
diff = sub - local_mean

# Letters are brighter than background
mask = (diff[:, :, 0] > 8) & (diff[:, :, 1] > 8) & (diff[:, :, 2] > 8)
mask_dilated = binary_dilation(mask, iterations=5)

# Background texture replacement via median filter
sub_med = median_filter(sub, size=(21, 21, 1))
sub[mask_dilated] = sub_med[mask_dilated]
arr[800:1160, 560:935] = sub

clean_end = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
clean_end.crop((550, 780, 940, 1180)).save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/check_clean_v2.png")
print("Saved check_clean_v2.png")
