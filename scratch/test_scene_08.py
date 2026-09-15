from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

w, h = 1080, 1920
canvas = Image.new("RGBA", (w, h), (3, 4, 12, 255))

# Sourced from Hubble's full natural-color Saturn 2025
base = Image.open("scratch/saturn_downloads/hubble_saturn_2025.jpg").convert("RGBA")
scale = 1080 / base.width
bh = int(base.height * scale)
base_fit = base.resize((1080, bh), Image.Resampling.LANCZOS)
base_enh = ImageEnhance.Contrast(base_fit).enhance(1.18)

# Feather top and bottom
arr = np.array(base_enh, dtype=np.float32)
fade = 140
arr[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
arr[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

canvas.paste(faded, (0, 360), faded)

# Starfield
np.random.seed(808)
for _ in range(400):
    x = np.random.randint(0, w)
    y = np.random.randint(0, h)
    b = np.random.randint(90, 255)
    r = np.random.choice([1, 1, 1, 2])
    col = (b, int(b * 0.95), int(b * 1.1), np.random.randint(180, 255))
    canvas.paste(col, (x, y, x + r, y + r))

canvas.convert("RGB").save("scratch/saturn_preview/scene-08-philosophical-climax.png")
print("Scene 08 OK")
