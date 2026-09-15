import numpy as np
from PIL import Image, ImageDraw, ImageFilter

end_img = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGBA")
scale = 1080 / end_img.width
new_h = int(end_img.height * scale)
end_scaled = end_img.resize((1080, new_h), Image.Resampling.LANCZOS)
# new_h is 1918 (basically 1920)

# In end_scaled (1080x1918):
# Let us trace the foreground silhouette:
# Boy head starts at (x: 80..280, y: 1100..1220)
# Dog head starts at (x: 370..520, y: 1170..1320)
# Sea of clouds horizon starts at y ~ 1380 on the right (x: 520..1080)
# Above y=1380 on the right was the text "เพราะในจักรวาลนี้..."
# So if our mask only includes:
# - The boy (x: 0..370, y: 1100..1920)
# - The dog (x: 350..550, y: 1170..1920)
# - The sea of clouds and mountain ridge (x: 500..1080, y: 1390..1920)
# Then ALL the text in the sky (which was above y=1380 on the right) is 100% EXCLUDED naturally!

# Let us create a precise alpha mask for end_scaled:
mask = Image.new("L", (1080, new_h), 0)
m_draw = ImageDraw.Draw(mask)

# 1. Boy silhouette polygon
boy_pts = [
    (0, 1150), (60, 1120), (120, 1095), (170, 1085), (230, 1095), (270, 1130), (280, 1170),
    (310, 1220), (360, 1260), (370, 1340), (370, 1920), (0, 1920)
]
m_draw.polygon(boy_pts, fill=255)

# 2. Dog silhouette polygon
dog_pts = [
    (360, 1280), (390, 1210), (410, 1170), (430, 1210), (470, 1210), (495, 1175), (515, 1220),
    (540, 1270), (565, 1360), (570, 1920), (360, 1920)
]
m_draw.polygon(dog_pts, fill=255)

# 3. Horizon clouds and city lights on the right (y from 1400 down to 1920)
# Soft gradient transition at the cloud horizon: y = 1370 to 1420
for y in range(1370, 1420):
    val = int(255 * (y - 1370) / 50.0)
    m_draw.line([(515, y), (1080, y)], fill=val)
m_draw.rectangle([(515, 1420), (1080, new_h)], fill=255)

# Smooth blur the mask edges for photorealistic integration
mask_blurred = mask.filter(ImageFilter.GaussianBlur(3.0))

# Test saving the cutout foreground with transparent background
fg_cutout = Image.new("RGBA", (1080, new_h), (0, 0, 0, 0))
fg_cutout.paste(end_scaled, (0, 0), mask_blurred)
fg_cutout.save("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/test_fg_cutout.png")
print("Saved test_fg_cutout.png successfully!")
