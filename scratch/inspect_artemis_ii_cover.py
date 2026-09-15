from PIL import Image

a2 = Image.open("assets/artemis_ii_far_side_reel/images/scene-01-hook.png")
# Let's crop explorer and dog in artemis_ii_far_side_reel
# Let's save a crop of lower half
crop = a2.crop((0, 900, 1080, 1920))
crop.save("scratch/artemis_ii_lower_half.png")
print("Saved scratch/artemis_ii_lower_half.png")
