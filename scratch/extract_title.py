from PIL import Image, ImageFilter
import numpy as np

ref = Image.open('assets/branding/mamase/reference/mamase-reels-editorial-poster-master.png').convert('RGBA')
arr = np.array(ref).astype(np.float32)

# In ref (941x1672):
# Title "ALPHA": y=330..530, x=50..680
crop_alpha = arr[330:530, 50:680].copy()
# Title "CENTAURI": y=530..600, x=50..680
crop_centauri = arr[530:600, 50:680].copy()

# For ALPHA, the sun glow is in the upper right (around x > 400, y < 100 in crop)
# Let's see the luminance:
lum_a = 0.299*crop_alpha[:,:,0] + 0.587*crop_alpha[:,:,1] + 0.114*crop_alpha[:,:,2]
# Alpha text itself is bright silver/white and cyan glow (> 120)
# Sun background is around 30..80
alpha_mask = np.clip((lum_a - 40.0) / (180.0 - 40.0), 0, 1) ** 1.3 * 255.0
img_alpha = Image.fromarray(np.clip(crop_alpha, 0, 255).astype(np.uint8))
img_alpha.putalpha(Image.fromarray(alpha_mask.astype(np.uint8)))
img_alpha.save('scratch/elem_alpha.png')

lum_c = 0.299*crop_centauri[:,:,0] + 0.587*crop_centauri[:,:,1] + 0.114*crop_centauri[:,:,2]
cent_mask = np.clip((lum_c - 20.0) / (130.0 - 20.0), 0, 1) ** 1.1 * 255.0
img_cent = Image.fromarray(np.clip(crop_centauri, 0, 255).astype(np.uint8))
img_cent.putalpha(Image.fromarray(cent_mask.astype(np.uint8)))
img_cent.save('scratch/elem_centauri.png')

print("Title elements extracted.")
