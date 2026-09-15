import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import uniform_filter, binary_dilation

end_img = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGB")
arr = np.array(end_img).astype(np.float32)

# The text "เพราะในจักรวาลนี้..." is in rows 800..1150, cols 580..935
# Detect the text strokes:
sub = arr[800:1150, 580:935]
local_mean = uniform_filter(sub, size=(11, 11, 1))
diff = sub - local_mean
# Letters are bright compared to surrounding sky
mask = (diff[:, :, 0] > 18) & (diff[:, :, 1] > 18) & (diff[:, :, 2] > 18) & (sub[:, :, 0] > 70)
mask_dilated = binary_dilation(mask, iterations=2)

# Replace letter pixels with local background using Gaussian blurred background
sub_clean = uniform_filter(sub, size=(19, 19, 1))
sub[mask_dilated] = sub_clean[mask_dilated]
arr[800:1150, 580:935] = sub

clean_end = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
clean_end.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/clean_end_scene.png")
print("Saved clean_end_scene.png")
