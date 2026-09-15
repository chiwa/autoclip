from PIL import Image

im = Image.open("assets/artemis_ii_far_side_reel/images/scene-01-hook.png")
# Let's crop explorer and terrain in artemis_ii_far_side_reel:
# Explorer is at x=380..1080, y=250..1920
# Lunar terrain is at y=1050..1920
# Notice that here, 'พี' is standing in 3/4 view, facing the viewer with warm smile,
# wearing glasses, stylish dark blue flight jacket, dark tee, brown trousers, one hand in pocket, one hand pointing up!
# Exactly like mamase-presenter-cutout, but rendered natively in the scene with cinematic lighting!
print("Explorer in Artemis II size:", im.size)
crop = im.crop((380, 240, 1080, 1920))
crop.save("scratch/artemis_ii_pee_native.png")
print("Saved scratch/artemis_ii_pee_native.png")
