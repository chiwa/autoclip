from PIL import Image

base = Image.open("assets/iss_why_not_fall_reel/images/scene-01-hook-base.png")
fg = base.crop((0, 1000, 1080, 1920))
fg.save("scratch/iss_base_fg.png")
print("Saved scratch/iss_base_fg.png")
