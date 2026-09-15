from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# Load the source Lunar Gateway image
lg = Image.open("assets/lunar_gateway_reel/images/scene-01-hook.png").convert("RGBA")
W, H = lg.size

# In Lunar Gateway, the standing explorer and alert golden retriever are:
# Explorer: standing tall, x=650..920, y=550..1700
# Dog: sitting/standing alert looking up, x=380..680, y=1150..1700
# Lunar ground & horizon: y=1250..1920

# Let's cleanly remove:
# 1. Solar panel wing tip at x=160..390, y=500..580 (if any)
# 2. Text "Same Sky / Bigger Tomorrow" at x=680..960, y=1390..1540
# 3. Patch on left arm: American flag (x=700..745, y=1060..1105), mission patch (x=690..745, y=1110..1175)
# 4. Patch on backpack: blue badge (x=885..940, y=1105..1155)

cleaned = lg.copy()
np_img = np.array(cleaned)

# 1. Clean patches on left arm
# Jacket color is deep navy nylon around [35, 48, 62]
for y in range(1060, 1180):
    for x in range(692, 745):
        # sample texture from the dark jacket fold at x=750..770
        ref_x = 750 + (x - 692) // 3
        ref_y = y
        noise = np.random.randint(-2, 3, 3)
        np_img[y, x, :3] = np.clip(np_img[ref_y, ref_x, :3] + noise, 0, 255)

# 2. Clean backpack patch
for y in range(1105, 1155):
    for x in range(885, 940):
        # sample from backpack fabric just below at y=1160..1200
        ref_x = x
        ref_y = y + 45
        noise = np.random.randint(-3, 4, 3)
        np_img[y, x, :3] = np.clip(np_img[ref_y, ref_x, :3] + noise, 0, 255)

# 3. Clean "Same Sky Bigger Tomorrow" text
# Let's do a smart patch replacement:
# The rock background has natural craggy shadows.
# We can sample the rock texture from right below the text (y=1540..1640)
for y in range(1390, 1530):
    for x in range(680, 960):
        # If the pixel is significantly brighter than the dark rock (the yellow/white text)
        r, g, b = int(np_img[y, x, 0]), int(np_img[y, x, 1]), int(np_img[y, x, 2])
        is_yellow = (r > 160 and g > 130 and b < 100)
        is_white = (r > 160 and g > 160 and b > 160)
        if is_yellow or is_white:
            # sample from dark rock below
            sy = min(1700, y + 80)
            sx = max(680, min(950, x - 20))
            np_img[y, x, :3] = np_img[sy, sx, :3]

cleaned = Image.fromarray(np_img)

# Save the cleaned duo area to verify
duo_check = cleaned.crop((350, 540, 960, 1720))
duo_check.save("scratch/duo_cleaned_perfect.png")
print("Saved scratch/duo_cleaned_perfect.png")
