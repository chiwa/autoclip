import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np

w, h = 1080, 1920
canvas = Image.new("RGBA", (w, h), (3, 4, 14, 255))

# Saturn full globe from Hubble left panel
sat = Image.open("scratch/saturn_downloads/decagon_left_panel.png").convert("RGBA")
scale = 1040 / sat.width
sat_fit = sat.resize((1040, int(sat.height * scale)), Image.Resampling.LANCZOS)
sat_enh = ImageEnhance.Contrast(sat_fit).enhance(1.15)

# Paste Saturn in mid-upper area
canvas.paste(sat_enh, (20, 360), sat_enh)

# Orbital ellipse & Sun representation
draw = ImageDraw.Draw(canvas)
# Sun in upper distance
sx, sy = 880, 220
for r in range(70, 0, -4):
    glow_col = (int(255 * (1 - r/90)), int(210 * (1 - r/80)), int(80 * (1 - r/70)), int(220 * (1 - r/70)))
    draw.ellipse([sx - r, sy - r*0.8, sx + r, sy + r*0.8], fill=glow_col)

# 29.5-year orbit arc
draw.arc([100, 150, 980, 1300], start=45, end=210, fill=(255, 215, 100, 160), width=3)

# Solar ray light beam traveling toward Saturn's south pole
for offset in [-15, 0, 15]:
    draw.line([(sx - 40, sy + 30), (540 + offset, 750)], fill=(255, 235, 140, 60), width=2)

# Starfield
np.random.seed(606)
for _ in range(350):
    x = np.random.randint(0, w)
    y = np.random.randint(0, h)
    b = np.random.randint(90, 255)
    r = np.random.choice([1, 1, 1, 2])
    col = (b, int(b * 0.95), int(b * 1.1), np.random.randint(180, 255))
    draw.ellipse([x, y, x + r, y + r], fill=col)

canvas.convert("RGB").save("scratch/saturn_preview/scene-06-seasonal-cycle.png")
print("Scene 06 OK")
