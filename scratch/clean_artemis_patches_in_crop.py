from PIL import Image
import numpy as np

crop = Image.open("scratch/crop_500_700_900_1100.png").convert("RGBA")
arr = np.array(crop)

# In crop_500_700_900_1100.png (400w x 400h):
# 1. American flag: x=95..145, y=275..315
# Left of flag is jacket (x=70..90), right is jacket fold
for y in range(275, 315):
    c_l = arr[y, 90, :3].astype(float)
    c_r = arr[y, 150, :3].astype(float)
    for x in range(92, 148):
        t = (x - 92) / (148 - 92)
        col = (1.0 - t) * c_l + t * c_r
        arr[y, x, :3] = np.clip(col + np.random.randint(-2, 3, 3), 0, 255)

# 2. Triangular patch: x=85..125, y=345..400
for y in range(340, 400):
    c_l = arr[y, 75, :3].astype(float)
    c_r = arr[y, 135, :3].astype(float)
    for x in range(80, 130):
        t = (x - 80) / (130 - 80)
        col = (1.0 - t) * c_l + t * c_r
        arr[y, x, :3] = np.clip(col + np.random.randint(-2, 3, 3), 0, 255)

# 3. ART text: x=155..195, y=230..265
for y in range(230, 265):
    c_t = arr[225, x if 'x' in locals() else 170, :3].astype(float)
    for x in range(150, 200):
        c_t = arr[225, x, :3].astype(float)
        c_b = arr[270, x, :3].astype(float)
        t = (y - 230) / (265 - 230)
        col = (1.0 - t) * c_t + t * c_b
        arr[y, x, :3] = np.clip(col + np.random.randint(-2, 3, 3), 0, 255)

# 4. NASA logo on backpack: x=275..325, y=260..325
for y in range(258, 328):
    c_l = arr[y, 268, :3].astype(float)
    c_r = arr[y, 335, :3].astype(float)
    for x in range(270, 332):
        t = (x - 270) / (332 - 270)
        col = (1.0 - t) * c_l + t * c_r
        arr[y, x, :3] = np.clip(col + np.random.randint(-2, 3, 3), 0, 255)

# 5. Text below NASA: x=265..345, y=345..365
for y in range(342, 368):
    for x in range(260, 350):
        c_t = arr[338, x, :3].astype(float)
        c_b = arr[372, x, :3].astype(float)
        t = (y - 342) / (368 - 342)
        col = (1.0 - t) * c_t + t * c_b
        arr[y, x, :3] = np.clip(col + np.random.randint(-2, 3, 3), 0, 255)

clean_img = Image.fromarray(arr)
clean_img.save("scratch/crop_cleaned_perfect.png")
print("Saved scratch/crop_cleaned_perfect.png")
