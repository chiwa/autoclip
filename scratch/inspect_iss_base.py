from PIL import Image

im = Image.open("assets/iss_why_not_fall_reel/images/scene-01-hook-base.png")
print("ISS hook base size:", im.size, im.mode)
