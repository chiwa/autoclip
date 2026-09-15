from PIL import Image

# Let's crop from assets/artemis_reel/images/scene-01-hook.png:
# Explorer: x=500..880, y=660..1700
# Dog: x=100..550, y=1100..1700
art = Image.open("assets/artemis_reel/images/scene-01-hook.png")
print("Dimensions:", art.size)

# Let's crop the dog alone:
dog = art.crop((120, 1150, 560, 1720))
dog.save("scratch/dog_alone.png")

# Explorer alone:
explorer = art.crop((520, 660, 880, 1720))
explorer.save("scratch/explorer_alone.png")

print("Saved scratch/dog_alone.png and scratch/explorer_alone.png")
