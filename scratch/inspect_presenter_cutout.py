from PIL import Image

im = Image.open("assets/characters/mamase-presenter-cutout.png")
print("Cutout size:", im.size, im.mode)
thumb = im.resize((500, int(im.height * 500 / im.width)))
thumb.save("scratch/cutout_thumb.png")
print("Saved scratch/cutout_thumb.png")
