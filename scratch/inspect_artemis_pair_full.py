from PIL import Image

im = Image.open("assets/lunar_gateway_reel/images/scene-01-hook.png")
# Let's crop explorer and dog full height:
# x=150..950, y=950..1850
crop = im.crop((150, 950, 950, 1850))
crop.save("scratch/lunar_gateway_pair_full.png")
print("Saved", crop.size)
