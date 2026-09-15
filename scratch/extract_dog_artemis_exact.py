from PIL import Image, ImageDraw, ImageFilter
import numpy as np

crop = Image.open("scratch/dog_raw_crop.png").convert("RGBA")
w, h = crop.size

# Precise polygon tracing from the grid:
# Dog is located at x: 100..440, y: 80..470
# Nose/mouth: (438, 90), (435, 110), (410, 110)
# Chin/throat: (405, 130), (395, 160)
# Chest: (385, 200), (370, 240), (360, 280), (350, 320)
# Front right leg: (350, 360), (355, 410), (360, 445), (370, 460)
# Front left leg: (415, 340), (420, 390), (425, 440), (435, 460)
# Paws: (435, 465), (350, 465)
# Belly: (340, 430), (320, 410)
# Hind leg/hock: (300, 420), (280, 440), (270, 460)
# Tail: (250, 460), (200, 450), (140, 445), (105, 450), (120, 465), (170, 465), (240, 465)
# Back / flank: (220, 410), (240, 340), (270, 270), (290, 200), (315, 130)
# Head / ears: (330, 85), (350, 75), (370, 70), (390, 75), (420, 80), (438, 90)

mask = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(mask)

polygon = [
    (438, 90), (438, 115), (405, 120), (395, 150), (385, 190), (372, 230),
    (360, 275), (352, 320), (352, 370), (358, 415), (365, 455), (375, 465),
    (435, 465), (438, 455), (430, 410), (425, 350), (420, 300),
    (435, 465), (375, 465), (355, 465), (345, 435), (325, 410), (300, 425),
    (275, 450), (250, 462), (200, 452), (140, 448), (105, 452), (115, 465),
    (165, 468), (235, 468), (265, 455), (240, 380), (255, 300), (275, 230),
    (295, 160), (320, 110), (340, 80), (365, 72), (390, 72), (420, 80)
]

# Let's also do a flood-fill or edge-aware refinement for fur:
d.polygon(polygon, fill=255)

# Include the full front legs correctly
d.polygon([(350, 320), (360, 465), (438, 465), (420, 320)], fill=255)

# Blur mask slightly for realistic soft fur edges
soft_mask = mask.filter(ImageFilter.GaussianBlur(1.0))

dog_out = crop.copy()
dog_out.putalpha(soft_mask)
dog_out.save("scratch/dog_extracted_artemis.png")
print("Saved scratch/dog_extracted_artemis.png")
