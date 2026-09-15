from PIL import Image
import numpy as np

im = Image.open("assets/branding/mamase/mamase_podcast_header.png")
print("Header format:", im.format, "size:", im.size, "mode:", im.mode)
arr = np.array(im)
print("Channels:", arr.shape)
if arr.shape[2] == 4:
    print("Alpha min:", arr[:, :, 3].min(), "max:", arr[:, :, 3].max())
    print("Corner alpha:", arr[0, 0, 3], "Corner RGB:", arr[0, 0, :3])

# Check ISS header
iss = Image.open("assets/iss_why_not_fall_reel/images/scene-01-hook.png")
iss_header = iss.crop((58, 46, 58 + 400, 46 + 106))
iss_header.save("scratch/iss_header_crop.png")
print("Saved ISS header crop.")
