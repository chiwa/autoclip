from PIL import Image
import numpy as np

crop = Image.open("scratch/test_patches_local.png").convert("RGBA")
arr = np.array(crop)

# In test_patches_local.png (250w x 240h):
# American flag: x=20..75, y=30..70
# Triangle patch: x=10..60, y=90..155
# ART text: x=90..140, y=20..50
# NASA blue logo: x=180..230, y=40..100
# Text below NASA: x=175..245, y=105..125
# Text bottom: x=175..245, y=210..235

# Let's clone/inpaint smoothly:
# 1. Flag: sample from jacket at x=10..60, y=70..85
for y in range(25, 75):
    for x in range(18, 78):
        sample = arr[min(85, max(72, y + 25)), x]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

# 2. Triangle patch: sample from jacket at x=70..100, y=y
for y in range(85, 160):
    for x in range(8, 65):
        sample = arr[y, min(95, x + 45)]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

# 3. ART text: sample from jacket at x=x, y=55..75
for y in range(18, 52):
    for x in range(88, 145):
        sample = arr[y + 25, x]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

# 4. NASA logo: sample from backpack cloth below at y=130..170
for y in range(35, 102):
    for x in range(178, 235):
        sample = arr[y + 65, x]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

# 5. Text below NASA: sample from backpack cloth at y=135..155
for y in range(103, 128):
    for x in range(172, 248):
        sample = arr[y + 30, x]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

# 6. Text bottom: sample from backpack cloth at y=185..205
for y in range(208, 238):
    for x in range(172, 248):
        sample = arr[y - 20, x]
        noise = np.random.randint(-2, 3, 3)
        arr[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)

clean_patch = Image.fromarray(arr)
clean_patch.save("scratch/test_patches_cleaned.png")
print("Saved scratch/test_patches_cleaned.png")
