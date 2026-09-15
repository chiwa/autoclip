from PIL import Image, ImageDraw, ImageFilter
import numpy as np

crop = Image.open("scratch/dog_raw_crop.png").convert("RGBA")
w, h = crop.size

# Let's create a polygon mask around the dog:
# In dog_raw_crop.png:
# Nose/snout: (380, 40)
# Top of head: (340, 20)
# Ears / back of head: (305, 45)
# Neck / back: (290, 80), (275, 140), (245, 230), (220, 310), (200, 380)
# Hind leg / rump: (150, 440)
# Tail: (60, 450), (10, 460), (30, 475), (80, 480), (130, 465)
# Hind paw / rocks: (140, 480), (220, 480)
# Front paws / chest: (350, 460), (380, 370), (410, 260), (410, 190), (390, 100), (430, 60)

mask = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(mask)

polygon = [
    (385, 25), (425, 40), (435, 65), (415, 95), (415, 170), (425, 220),
    (405, 300), (395, 360), (390, 430), (370, 460), (345, 460), (335, 400),
    (315, 350), (290, 370), (275, 440), (250, 465), (200, 465), (150, 460),
    (110, 465), (50, 460), (15, 460), (10, 468), (35, 480), (90, 480),
    (150, 475), (200, 460), (180, 400), (205, 330), (230, 250), (260, 170),
    (280, 110), (300, 60), (315, 35), (345, 20), (370, 20)
]
d.polygon(polygon, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(1.2))

# Apply mask
dog_rgba = crop.copy()
dog_rgba.putalpha(mask)
dog_rgba.save("scratch/dog_isolated_test.png")
print("Saved scratch/dog_isolated_test.png")
