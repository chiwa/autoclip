from PIL import Image

art = Image.open("assets/artemis_reel/images/scene-01-hook.png")
# In assets/artemis_reel/images/scene-01-hook.png (1080x1920):
# Where is the dog?
# Let's crop x=250..650, y=1150..1750
crop = art.crop((250, 1150, 650, 1750))
crop.save("scratch/dog_real_crop.png")
print("Saved scratch/dog_real_crop.png", crop.size)
