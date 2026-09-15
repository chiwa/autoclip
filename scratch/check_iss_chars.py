from PIL import Image
iss = Image.open("assets/iss_why_not_fall_reel/images/scene-01-hook.png")
# let's crop bottom
bottom = iss.crop((0, 1000, 1080, 1920))
bottom.save("scratch/iss_chars_full.png")
print("Saved scratch/iss_chars_full.png")
