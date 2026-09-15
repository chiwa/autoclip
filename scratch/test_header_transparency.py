from PIL import Image
import numpy as np

header_raw = Image.open("assets/branding/mamase/mamase_podcast_header.png").convert("RGB")
arr = np.array(header_raw).astype(np.float32)

# Max RGB value as alpha
lum = np.max(arr, axis=2)
alpha = np.clip(lum * 1.5, 0, 255).astype(np.uint8)

# Make transparent RGBA
clean_header = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
clean_header.putalpha(Image.fromarray(alpha))

# Test pasting onto a colored background
bg = Image.new("RGBA", (500, 200), (10, 30, 80, 255))
bg.paste(clean_header, (50, 50), clean_header)
bg.save("scratch/test_header_pasted.png")
print("Saved scratch/test_header_pasted.png successfully!")
