from PIL import Image

iss = Image.open("assets/iss_why_not_fall_reel/images/scene-01-hook.png")
voy = Image.open("assets/voyager1_reel/images/scene-01-hook.png")

iss.crop((0, 1100, 1080, 1920)).save("scratch/iss_bottom_part.jpg")
voy.crop((0, 1100, 1080, 1920)).save("scratch/voyager_bottom_part.jpg")
print("Saved iss_bottom_part.jpg and voyager_bottom_part.jpg")
