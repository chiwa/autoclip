from PIL import Image

base = Image.open("assets/iss_why_not_fall_reel/images/scene-01-hook-base.png")
top = base.crop((0, 0, 1080, 1100))
top.save("scratch/iss_base_top.png")
print("Saved scratch/iss_base_top.png")
