from PIL import Image, ImageDraw, ImageFilter
import numpy as np

crop = Image.open("scratch/dog_real_crop.png").convert("RGBA")
w, h = crop.size

# Exact grid tracing:
# Nose/muzzle: (315, 155), (318, 175), (280, 185)
# Mouth/tongue/chin: (278, 205), (275, 235), (265, 270)
# Chest: (258, 305), (250, 360), (242, 410)
# Front right paw / leg: (240, 470), (245, 525), (255, 570), (270, 580)
# Front left paw / leg: (280, 570), (270, 500), (265, 430), (260, 370)
# Space between front and hind leg: (240, 570), (220, 500)
# Hind foot/hock: (200, 560), (180, 540)
# Rump/tail base: (150, 530), (100, 530), (40, 530), (10, 535)
# Tail tip: (0, 545), (15, 560), (80, 560), (140, 555)
# Back curve: (120, 510), (150, 440), (175, 370), (200, 290), (225, 210), (235, 170)
# Head/ears: (240, 140), (250, 110), (270, 95), (290, 95), (315, 120), (320, 150)

mask = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(mask)

polygon = [
    # Top of head to nose
    (270, 95), (295, 95), (315, 120), (320, 150), (315, 175), (282, 185),
    # Chin, throat, chest
    (278, 215), (268, 265), (255, 320), (248, 380), (242, 440),
    # Front paw
    (240, 500), (245, 550), (255, 580), (275, 580), (282, 550), (275, 490),
    (268, 430), (260, 360), (265, 430), (275, 490), (282, 550), (275, 580),
    # Underbelly & hind leg
    (245, 580), (230, 510), (210, 530), (195, 565), (170, 555), (180, 500),
    # Tail
    (140, 520), (80, 525), (20, 535), (2, 545), (15, 562), (80, 560), (135, 550),
    # Rump, flank, back
    (150, 460), (175, 380), (200, 300), (220, 220), (235, 160), (245, 115)
]

d.polygon(polygon, fill=255)

# Also ensure chest and front leg are fully solid
d.polygon([(250, 320), (285, 550), (240, 550), (235, 320)], fill=255)
# Ensure hind flank is solid
d.polygon([(150, 460), (230, 530), (170, 555)], fill=255)

# Soft blur mask for natural fur feathering
soft_mask = mask.filter(ImageFilter.GaussianBlur(1.2))

dog_clean = crop.copy()
dog_clean.putalpha(soft_mask)
dog_clean.save("scratch/dog_clean_artemis_final.png")
print("Saved scratch/dog_clean_artemis_final.png")
