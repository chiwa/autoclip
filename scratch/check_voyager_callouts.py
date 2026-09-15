from PIL import Image

voy = Image.open("assets/voyager1_reel/images/scene-01-hook.png")
# Let's save the middle of voyager1
voy.crop((0, 400, 1080, 1200)).save("scratch/voyager_mid_check.jpg", quality=90)
print("Saved scratch/voyager_mid_check.jpg")
