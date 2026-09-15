from PIL import Image

iss = Image.open("assets/iss_why_not_fall_reel/images/scene-01-hook.png")
voyager = Image.open("assets/voyager1_reel/images/scene-01-hook.png")

print("ISS size:", iss.size)
print("Voyager size:", voyager.size)

# Let's see what the bottom 800 pixels look like
iss_bottom = iss.crop((0, 1120, 1080, 1920))
voyager_bottom = voyager.crop((0, 1120, 1080, 1920))

iss_bottom.save("scratch/iss_bottom.png")
voyager_bottom.save("scratch/voyager_bottom.png")
print("Saved bottom crops.")
