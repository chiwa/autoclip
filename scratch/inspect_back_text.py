from PIL import Image
import numpy as np

end_img = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGB")
# Total size: (941, 1672)
# Scale to width 1080
scale = 1080.0 / end_img.width
new_h = int(end_img.height * scale)
scaled = end_img.resize((1080, new_h), Image.Resampling.LANCZOS)
# Lower 880px: crop is from (new_h - 880) to new_h
fg = scaled.crop((0, new_h - 880, 1080, new_h))

# In fg, where is the text?
# On the left side of the explorer: x=0..200, y=200..600
text_crop = fg.crop((0, 200, 250, 600))
text_crop.save("scratch/back_text_crop.png")
print("Saved scratch/back_text_crop.png")
