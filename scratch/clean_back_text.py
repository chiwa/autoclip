import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import median_filter, uniform_filter

fg = Image.open("scratch/back_text_crop.png")
arr = np.array(fg).astype(np.float32)

# The text "Good Stories Brighter Horizons" is around rows 100..380, cols 10..180
# The jacket fabric is very dark charcoal/black (RGB around 10..30)
# The text has higher brightness (RGB around 50..90, warmer tint)
sub = arr[100:380, 10:180].copy()
local_min = uniform_filter(sub, size=(25, 25, 1))

# Median filter with large kernel to remove text strokes completely
med = median_filter(sub, size=(21, 21, 1))

# Blend median filtered patch
arr[100:380, 10:180] = med

clean_crop = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
clean_crop.save("scratch/back_text_cleaned.png")
print("Saved scratch/back_text_cleaned.png")
