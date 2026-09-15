from PIL import Image

im = Image.open("assets/artemis_ii_far_side_reel/images/scene-01-hook.png")
crop = im.crop((100, 950, 950, 1800))
crop.save("scratch/artemis_ii_pair_crop.png")
print("Saved scratch/artemis_ii_pair_crop.png", crop.size)
