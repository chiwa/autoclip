from PIL import Image

im = Image.open("scratch/pale_blue_dot_raw/eso_vlt_laser_milkyway.jpg")
print("Laser plate size:", im.size)

# If we crop to 9:16:
# Target is 1080 x 1920.
# The image is 3000 x 2657 (or similar). Let's check aspect ratio.
w, h = im.size
# 9:16 crop from this image
target_w = int(h * 9 / 16)
print(f"Target w for full h: {target_w} (available: {w})")
# If w < target_w, we scale width to 1080 and crop height
scale = 1080 / w
new_h = int(h * scale)
print(f"Scaled to 1080w -> h is {new_h}")
