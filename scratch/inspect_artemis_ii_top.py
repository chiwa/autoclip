from PIL import Image

im = Image.open("assets/artemis_ii_far_side_reel/images/scene-01-hook.png")
# Let's crop explorer's head at x=400..900, y=200..600
head = im.crop((400, 200, 900, 600))
head.save("scratch/artemis_ii_head_clean.png")
print("Saved scratch/artemis_ii_head_clean.png")
