from PIL import Image
import numpy as np

crop = Image.open("scratch/test_patches_local.png").convert("RGBA")
arr = np.array(crop)

# Let's clean:
# 1. American flag:
# Flag is at x: 26..66, y: 35..65
# The cloth around it has horizontal folds and lighting.
# Instead of a box, interpolate from left (x=24) and right (x=68) horizontally!
for y in range(32, 68):
    c_left = arr[y, 23, :3].astype(float)
    c_right = arr[y, 69, :3].astype(float)
    for x in range(24, 69):
        t = (x - 24) / (69 - 24)
        col = (1.0 - t) * c_left + t * c_right
        arr[y, x, :3] = np.clip(col + np.random.randint(-2, 3, 3), 0, 255)

# 2. Triangle patch:
# Patch is at x: 18..52, y: 92..150
for y in range(90, 152):
    c_left = arr[y, 16, :3].astype(float)
    c_right = arr[y, 55, :3].astype(float)
    for x in range(17, 55):
        t = (x - 17) / (55 - 17)
        col = (1.0 - t) * c_left + t * c_right
        arr[y, x, :3] = np.clip(col + np.random.randint(-2, 3, 3), 0, 255)

# 3. ART text:
# x: 96..132, y: 24..45
for y in range(22, 48):
    c_top = arr[20, x if 'x' in locals() else 100, :3].astype(float) # from top and bottom
    for x in range(94, 136):
        c_top = arr[20, x, :3].astype(float)
        c_bot = arr[50, x, :3].astype(float)
        t = (y - 22) / (48 - 22)
        col = (1.0 - t) * c_top + t * c_bot
        arr[y, x, :3] = np.clip(col + np.random.randint(-2, 3, 3), 0, 255)

# 4. NASA logo on backpack:
# x: 186..226, y: 46..94
for y in range(44, 96):
    c_left = arr[y, 184, :3].astype(float)
    c_right = arr[y, 228, :3].astype(float)
    for x in range(185, 228):
        t = (x - 185) / (228 - 185)
        col = (1.0 - t) * c_left + t * c_right
        arr[y, x, :3] = np.clip(col + np.random.randint(-2, 3, 3), 0, 255)

# 5. Text below NASA:
for y in range(106, 120):
    for x in range(175, 240):
        c_top = arr[104, x, :3].astype(float)
        c_bot = arr[122, x, :3].astype(float)
        t = (y - 106) / (120 - 106)
        col = (1.0 - t) * c_top + t * c_bot
        arr[y, x, :3] = np.clip(col + np.random.randint(-2, 3, 3), 0, 255)

# 6. Text bottom:
for y in range(215, 228):
    for x in range(175, 240):
        c_top = arr[213, x, :3].astype(float)
        c_bot = arr[230, x, :3].astype(float)
        t = (y - 215) / (228 - 215)
        col = (1.0 - t) * c_top + t * c_bot
        arr[y, x, :3] = np.clip(col + np.random.randint(-2, 3, 3), 0, 255)

clean_patch = Image.fromarray(arr)
clean_patch.save("scratch/test_patches_smart_interp.png")
print("Saved scratch/test_patches_smart_interp.png")
