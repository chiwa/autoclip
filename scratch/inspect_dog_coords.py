from PIL import Image

crop = Image.open("scratch/dog_raw_crop.png")
# Let's print out the size and find where the dog pixels actually are:
print("Crop size:", crop.size)
# The crop is 440 x 610.
# Let's save a grid overlay so we see the exact coordinates
from PIL import ImageDraw
grid = crop.copy()
d = ImageDraw.Draw(grid)
for x in range(0, 440, 50):
    d.line([(x, 0), (x, 610)], fill=(255, 0, 0, 128))
    d.text((x + 2, 5), str(x), fill=(255, 255, 0))
for y in range(0, 610, 50):
    d.line([(0, y), (440, y)], fill=(255, 0, 0, 128))
    d.text((5, y + 2), str(y), fill=(255, 255, 0))

grid.save("scratch/dog_grid.png")
print("Saved scratch/dog_grid.png")
