from rembg import remove
from PIL import Image

inp = Image.open("scratch/turbo_chars.jpg")
out = remove(inp)
out.save("scratch/standing_duo_cutout.png")
print("Saved standing_duo_cutout.png, size:", out.size)
