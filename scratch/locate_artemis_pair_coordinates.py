from PIL import Image

art = Image.open("assets/artemis_reel/images/scene-01-hook.png")
# In Artemis I-V, the explorer and dog:
# Let's save a wide crop around y=700..1200
crop = art.crop((500, 700, 900, 1100))
crop.save("scratch/artemis_explorer_upper_real.png")
print("Saved scratch/artemis_explorer_upper_real.png")
