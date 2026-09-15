from PIL import Image, ImageFilter
import numpy as np

# Load the source Artemis I-V master image
im = Image.open("assets/artemis_reel/images/scene-01-hook.png").convert("RGBA")
arr = np.array(im)

# 1. Flag on arm: x=650..700, y=800..840
# Let's paint over flag with jacket dark grey/black fabric (around [38, 44, 48])
for y in range(798, 835):
    for x in range(650, 700):
        sample = arr[y, 635]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

# 2. Patch below flag on arm: x=640..680, y=840..885
for y in range(835, 888):
    for x in range(640, 680):
        sample = arr[y, 625]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

# 3. Text "ART" on shoulder: x=740..785, y=775..805
for y in range(772, 808):
    for x in range(740, 785):
        sample = arr[y + 15, x]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

# 4. NASA round logo on backpack: x=875..920, y=790..845
for y in range(790, 845):
    for x in range(875, 920):
        sample = arr[y, 865]
        noise = np.random.randint(-3, 4, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

# 5. Text below NASA logo on backpack: x=865..930, y=845..860
for y in range(845, 860):
    for x in range(865, 930):
        sample = arr[y - 15, x]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

# 6. Text "Same Sky Bigger Tomorrow": x=800..1080, y=1540..1660
for y in range(1540, 1660):
    for x in range(800, 1070):
        r, g, b = int(arr[y, x, 0]), int(arr[y, x, 1]), int(arr[y, x, 2])
        if (r > 150 and g > 150 and b > 150) or (r > 160 and g > 130 and b < 90):
            # rock sample
            sy = min(1800, y + 60)
            sx = max(800, x - 15)
            arr[y, x, :3] = arr[sy, sx, :3]

# 7. Cyan leader line: from x=460, y=750 down to x=350, y=825
for y in range(745, 830):
    for x in range(340, 480):
        # if pixel is cyan/white line
        r, g, b = int(arr[y, x, 0]), int(arr[y, x, 1]), int(arr[y, x, 2])
        if b > 180 and g > 150 and r < 200:
            # sample starry space above/right
            arr[y, x, :3] = arr[max(720, y - 15), min(500, x + 15), :3]

cleaned_img = Image.fromarray(arr)
# Check cropped cleaned explorer and dog
check = cleaned_img.crop((200, 600, 1000, 1750))
check.save("scratch/artemis_cleaned_check.png")
print("Saved scratch/artemis_cleaned_check.png")
