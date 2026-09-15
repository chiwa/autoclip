from PIL import Image, ImageFilter, ImageOps
import numpy as np

ref = Image.open('assets/branding/mamase/reference/mamase-reels-editorial-poster-master.png').convert('RGBA')
arr = np.array(ref).astype(np.float32)

# 1. Script top-right
# Crop x=710..925, y=25..140 in ref (941x1672)
crop_script = arr[25:140, 710:925].copy()
lum = 0.299*crop_script[:,:,0] + 0.587*crop_script[:,:,1] + 0.114*crop_script[:,:,2]
# Background is dark navy (~10)
alpha_script = np.clip((lum - 15.0) / (120.0 - 15.0), 0, 1) ** 1.1 * 255.0
img_script = Image.fromarray(np.clip(crop_script, 0, 255).astype(np.uint8))
img_script.putalpha(Image.fromarray(alpha_script.astype(np.uint8)))
img_script.save('scratch/elem_script.png')

# 2. Kicker
crop_kicker = arr[210:330, 50:260].copy()
lum = 0.299*crop_kicker[:,:,0] + 0.587*crop_kicker[:,:,1] + 0.114*crop_kicker[:,:,2]
alpha_kicker = np.clip((lum - 16.0) / (130.0 - 16.0), 0, 1) ** 1.1 * 255.0
img_kicker = Image.fromarray(np.clip(crop_kicker, 0, 255).astype(np.uint8))
img_kicker.putalpha(Image.fromarray(alpha_kicker.astype(np.uint8)))
img_kicker.save('scratch/elem_kicker.png')

# 3. Thai Hook lines: y=590..930, x=50..580
crop_hook = arr[590:930, 50:580].copy()
lum = 0.299*crop_hook[:,:,0] + 0.587*crop_hook[:,:,1] + 0.114*crop_hook[:,:,2]
alpha_hook = np.clip((lum - 18.0) / (140.0 - 18.0), 0, 1) ** 1.1 * 255.0
img_hook = Image.fromarray(np.clip(crop_hook, 0, 255).astype(np.uint8))
img_hook.putalpha(Image.fromarray(alpha_hook.astype(np.uint8)))
img_hook.save('scratch/elem_hook.png')

# 4. Quote
crop_quote = arr[870:980, 720:920].copy()
lum = 0.299*crop_quote[:,:,0] + 0.587*crop_quote[:,:,1] + 0.114*crop_quote[:,:,2]
alpha_quote = np.clip((lum - 18.0) / (130.0 - 18.0), 0, 1) ** 1.1 * 255.0
img_quote = Image.fromarray(np.clip(crop_quote, 0, 255).astype(np.uint8))
img_quote.putalpha(Image.fromarray(alpha_quote.astype(np.uint8)))
img_quote.save('scratch/elem_quote.png')

# 5. Bottom bar: y=1530..1655, x=20..925
crop_bar = arr[1530:1655, 20:925].copy()
lum = 0.299*crop_bar[:,:,0] + 0.587*crop_bar[:,:,1] + 0.114*crop_bar[:,:,2]
alpha_bar = np.clip((lum - 20.0) / (120.0 - 20.0), 0, 1) ** 1.2 * 255.0
img_bar = Image.fromarray(np.clip(crop_bar, 0, 255).astype(np.uint8))
img_bar.putalpha(Image.fromarray(alpha_bar.astype(np.uint8)))
img_bar.save('scratch/elem_bar.png')

print("All elements isolated successfully.")
