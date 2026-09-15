from PIL import Image

im = Image.open("scratch/pale_blue_dot_raw/eso_vlt_laser_milkyway.jpg")
W, H = im.size
# We want 9:16 aspect ratio:
# If height is 3631, target width = 3631 * 9 / 16 = 2042.4px!
# The laser is roughly in the center: x=1900..2000
# Dome is at the bottom center.
crop_w = int(H * 9 / 16)
# Center x around the laser/dome
cx = 1980
x0 = cx - crop_w // 2
x1 = x0 + crop_w
crop = im.crop((x0, 0, x1, H)).resize((1080, 1920), Image.Resampling.LANCZOS)
crop.save("scratch/test_laser_916.jpg", quality=90)
print("Saved scratch/test_laser_916.jpg")
