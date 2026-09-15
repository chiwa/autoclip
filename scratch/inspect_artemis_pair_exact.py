from PIL import Image

# In assets/artemis_reel/images/scene-01-hook.png (1080x1920):
# Explorer is standing on lunar surface, looking up at the Moon
# Dog is sitting/standing alert looking up at the Moon
# Let's crop x=150..850, y=950..1850
im = Image.open("assets/artemis_reel/images/scene-01-hook.png")
pair = im.crop((150, 950, 850, 1850))
pair.save("scratch/artemis_exact_pair.png")
print("Saved scratch/artemis_exact_pair.png")
