from PIL import Image

im = Image.open("assets/lunar_gateway_reel/images/scene-01-hook.png")
# The explorer and dog are in lower right / mid bottom:
# Let's crop the explorer and dog region to inspect
# In lunar_gateway_reel (1080x1920):
# Explorer is around x=500..880, y=1050..1700
# Dog is around x=200..600, y=1250..1750
crop = im.crop((180, 1000, 900, 1750))
crop.save("scratch/artemis_pair_crop.png")
print("Saved scratch/artemis_pair_crop.png", crop.size)
