from PIL import Image

im = Image.open("scratch/voyager_chars.png")
print("voyager_chars.png size:", im.size, im.mode)
