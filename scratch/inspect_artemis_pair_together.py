from PIL import Image

art = Image.open("assets/artemis_reel/images/scene-01-hook.png")
# In artemis_reel, let's look at the pair together:
# Dog: x=210..550, y=1150..1700
# Explorer: x=510..880, y=660..1700
# Notice that between the dog and explorer is the natural ground!
# If we keep them together as an intact unit:
pair_unit = art.crop((200, 660, 920, 1720))
pair_unit.save("scratch/pair_unit_together.png")
print("Saved scratch/pair_unit_together.png", pair_unit.size)
