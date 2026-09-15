from PIL import Image, ImageFilter, ImageDraw
import numpy as np

crop = Image.open("scratch/test_patches_local.png").convert("RGBA")
arr = np.array(crop)

# In test_patches_local.png (250w, 240h):
# We have pure dark jacket fabric right next to the patches!
# 1. American flag (x: 24..68, y: 32..68)
# Fill with jacket fabric from x: 24..68, y: 72..85 (vertical reflection/sample)
jacket_slice = arr[70:85, 24:68].copy()
# tile it over y=32..68
for y in range(30, 70):
    src_y = 70 + (y % 14)
    arr[y, 24:68, :3] = arr[src_y, 24:68, :3]

# 2. Triangular patch (x: 20..58, y: 92..150)
# Sample from jacket at x: 65..95, y: 92..150 (horizontal shift)
for y in range(90, 152):
    for x in range(18, 60):
        src_x = 65 + (x - 18) // 2
        arr[y, x, :3] = arr[y, src_x, :3]

# 3. "ART" letters (x: 95..135, y: 22..48)
# Sample from jacket below at y: 52..75
for y in range(20, 50):
    for x in range(92, 138):
        arr[y, x, :3] = arr[y + 30, x, :3]

# 4. NASA blue round logo on backpack (x: 185..228, y: 45..95)
# Backpack dark nylon fabric from x: 185..228, y: 135..180
for y in range(42, 98):
    src_y = 135 + (y - 42)
    arr[y, 185:230, :3] = arr[src_y, 185:230, :3]

# 5. Text below NASA "CES EXPEDITION" (x: 178..240, y: 105..120)
for y in range(104, 122):
    arr[y, 178:242, :3] = arr[y + 35, 178:242, :3]

# 6. Text at bottom "GEXPEDITION" (x: 175..240, y: 215..228)
for y in range(213, 230):
    arr[y, 175:242, :3] = arr[y - 25, 175:242, :3]

# Add very subtle natural sensor noise to blend seamless fabric grain
noise = np.random.randint(-2, 3, arr[:, :, :3].shape)
arr[:, :, :3] = np.clip(arr[:, :, :3] + noise, 0, 255)

clean_patch = Image.fromarray(arr)
# apply 1px median filter to seam areas only
clean_patch.save("scratch/test_patches_cleaned_smooth.png")
print("Saved scratch/test_patches_cleaned_smooth.png")
