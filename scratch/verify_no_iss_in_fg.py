from PIL import Image

base = Image.open("assets/iss_why_not_fall_reel/images/scene-01-hook-base.png")
# Let's crop y from 1000 to 1920
fg = base.crop((0, 1000, 1080, 1920))
fg.save("scratch/test_iss_fg_1000.png")
print("Saved scratch/test_iss_fg_1000.png. Size:", fg.size)
