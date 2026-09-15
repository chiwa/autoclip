from PIL import Image

im = Image.open("assets/artemis_reel/images/scene-01-hook.png")
# Let's crop from x=200..900, y=450..1200
crop = im.crop((200, 450, 900, 1200))
crop.save("scratch/artemis_pair_upper.png")
print("Saved scratch/artemis_pair_upper.png")
