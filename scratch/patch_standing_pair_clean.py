from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# Load the source Artemis I-V master image
im = Image.open("assets/artemis_reel/images/scene-01-hook.png").convert("RGBA")
arr = np.array(im)

# 1. Arm patches:
# In crop_arm_exact (which was x=600..750, y=950..1250):
# American flag is roughly at x=645..690, y=1030..1065
# Triangular mission patch is roughly at x=640..685, y=1075..1130
# "ART" text is at x=710..745, y=1010..1035
# Let's paint over these cleanly using nearby jacket texture:
# Jacket sample from x=685..710, y=1080..1150
for y in range(1025, 1070):
    for x in range(645, 692):
        sample = arr[y, min(710, x + 45)]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

for y in range(1070, 1135):
    for x in range(638, 688):
        sample = arr[y, min(710, x + 50)]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

for y in range(1005, 1040):
    for x in range(710, 750):
        sample = arr[y + 35, x]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

# 2. Backpack patches:
# In crop_bp_exact (which was x=800..980, y=950..1250):
# NASA blue meatball logo is at x=820..870, y=1030..1085
# Text below logo is at x=810..880, y=1090..1110
# Text at bottom of backpack is at x=810..880, y=1210..1235
for y in range(1025, 1090):
    for x in range(815, 875):
        sample = arr[min(1200, y + 60), x]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

for y in range(1088, 1115):
    for x in range(810, 885):
        sample = arr[y - 30, x]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

for y in range(1210, 1238):
    for x in range(810, 885):
        sample = arr[y - 25, x]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

# 3. Text "Same Sky Bigger Tomorrow":
# In crop_txt_exact (x=750..1020, y=1450..1650):
# Let's clone dark craggy rock from y=1620..1720
for y in range(1470, 1610):
    for x in range(740, 1010):
        r, g, b = int(arr[y, x, 0]), int(arr[y, x, 1]), int(arr[y, x, 2])
        is_yellow = (r > 160 and g > 130 and b < 100)
        is_white = (r > 160 and g > 160 and b > 160)
        if is_yellow or is_white:
            sy = min(1750, y + 70)
            sx = max(700, min(1050, x - 25))
            arr[y, x, :3] = arr[sy, sx, :3]

cleaned_img = Image.fromarray(arr)
# Check cropped cleaned explorer and dog
check = cleaned_img.crop((600, 980, 950, 1650))
check.save("scratch/artemis_cleaned_check2.png")
print("Saved scratch/artemis_cleaned_check2.png")
