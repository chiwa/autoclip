from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# Load the source Lunar Gateway image
lg = Image.open("assets/lunar_gateway_reel/images/scene-01-hook.png").convert("RGBA")

# Let's inspect the exact regions of text/patches to clean:
# 1. Flag & NASA patch on explorer's left arm (in full 1080x1920 coordinates):
# explorer arm is around x=700..750, y=1040..1180
# 2. Text "Same Sky / Bigger Tomorrow" with yellow dot:
# x=680..980, y=1390..1540
# 3. Patch on backpack:
# x=880..940, y=1100..1160

# We can inpaint / sample surrounding cloth texture:
# Arm jacket is dark navy nylon: color around (32, 45, 58)
# We can paint smoothly over the flag and patch with the jacket texture and grain!

pair_layer = lg.copy()

# A. Clean the arm patch (x: 695..740, y: 1060..1180)
# Sample cloth from just above/below/left of patch
draw = ImageDraw.Draw(pair_layer)

# Let's write a targeted texture blend for the arm patch
arm_crop = pair_layer.crop((680, 1050, 760, 1190))
arm_np = np.array(arm_crop)
# Patch is at local coords: x=15..60, y=15..130
# Replace with cloth texture from x=60..75 or slightly left
for y in range(15, 130):
    for x in range(15, 60):
        # sample from nearby jacket
        sample = arm_np[y, min(75, x + 35)]
        # add slight natural variation
        noise = np.random.randint(-3, 4, 3)
        val = np.clip(sample[:3] + noise, 0, 255)
        arm_np[y, x, :3] = val

arm_clean = Image.fromarray(arm_np)
pair_layer.paste(arm_clean, (680, 1050))

# B. Clean the backpack patch (x: 885..940, y: 1105..1155)
# Backpack is khaki canvas (85, 78, 65)
bp_crop = pair_layer.crop((870, 1095, 955, 1165))
bp_np = np.array(bp_crop)
for y in range(10, 60):
    for x in range(15, 70):
        sample = bp_np[min(65, y + 10), max(5, x - 15)]
        noise = np.random.randint(-4, 5, 3)
        bp_np[y, x, :3] = np.clip(sample[:3] + noise, 0, 255)
bp_clean = Image.fromarray(bp_np)
pair_layer.paste(bp_clean, (870, 1095))

# C. Clean "Same Sky Bigger Tomorrow" text (x: 680..980, y: 1390..1540)
# This is on the dark lunar rock / hillside behind the dog and beside the explorer's leg.
# We sample from the rock texture right next to it:
txt_crop = pair_layer.crop((670, 1380, 990, 1550))
txt_np = np.array(txt_crop)
# Sample from rock below (y=120..160) or right
for y in range(10, 160):
    for x in range(10, 310):
        # check if it's text pixel (high brightness yellow/white text)
        r, g, b = int(txt_np[y, x, 0]), int(txt_np[y, x, 1]), int(txt_np[y, x, 2])
        if (r > 140 and g > 130) or (r > 160 and g > 120 and b < 80): # white or yellow
            # sample from dark rock nearby
            sample_y = min(165, y + 25)
            sample_x = max(5, x - 20)
            txt_np[y, x, :3] = txt_np[sample_y, sample_x, :3]

txt_clean = Image.fromarray(txt_np)
# subtle blur on inpaint seam
txt_clean = txt_clean.filter(ImageFilter.MedianFilter(3))
pair_layer.paste(txt_clean, (670, 1380))

# Save cleaned pair inspection crop
cleaned_crop = pair_layer.crop((320, 750, 960, 1720))
cleaned_crop.save("scratch/cleaned_pair_inspection.png")
print("Saved scratch/cleaned_pair_inspection.png")
