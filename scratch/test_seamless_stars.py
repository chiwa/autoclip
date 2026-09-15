import numpy as np
from PIL import Image, ImageFilter

eso_raw = Image.open("assets/alpha_centauri_reel/raw/alpha_centauri_ab.png").convert("RGB")
eso_crop = eso_raw.crop((80, 320, 1170, 920))
arr = np.array(eso_crop).astype(np.float32)

h, w = arr.shape[:2]
# Radial / border feathering mask
Y, X = np.ogrid[:h, :w]
# Distance from edge
dist_left = X
dist_right = w - 1 - X
dist_top = Y
dist_bottom = h - 1 - Y
edge_dist = np.minimum(np.minimum(dist_left, dist_right), np.minimum(dist_top, dist_bottom)).astype(np.float32)

# Feather border over 80 pixels using smooth cosine
feather = np.clip(edge_dist / 80.0, 0, 1)
feather_mask = (1.0 - np.cos(np.pi * feather)) / 2.0

# Background subtraction: subtract dark sky pedestal (around 24)
subtracted = np.clip((arr - 22.0) * (255.0 / (255.0 - 22.0)), 0, 255)

# Calculate alpha based on luminance and feathering
lum = 0.299 * subtracted[:, :, 0] + 0.587 * subtracted[:, :, 1] + 0.114 * subtracted[:, :, 2]
alpha = np.clip(lum / 120.0, 0, 1) ** 1.3 * feather_mask * 255.0

clean_stars = Image.fromarray(subtracted.astype(np.uint8)).convert("RGBA")
clean_stars.putalpha(Image.fromarray(alpha.astype(np.uint8)))

# Test pasting onto a solid navy canvas
test_bg = Image.new("RGBA", (w + 100, h + 100), (8, 22, 52, 255))
test_bg.paste(clean_stars, (50, 50), clean_stars)
test_bg.save("scratch/test_seamless_stars.png")

# Check if there is ANY edge artifact at (50, 50)
test_arr = np.array(test_bg)
edge_diff = np.abs(test_arr[50, 50, :3].astype(float) - test_arr[40, 40, :3].astype(float)).max()
print("Max difference at edge border:", edge_diff)
print("Saved scratch/test_seamless_stars.png successfully!")
