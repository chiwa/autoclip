from PIL import Image, ImageDraw

dog_crop = Image.open("scratch/dog_real_crop.png")
w, h = dog_crop.size

grid = dog_crop.copy()
d = ImageDraw.Draw(grid)
for x in range(0, w, 50):
    d.line([(x, 0), (x, h)], fill=(255, 0, 0, 128))
    d.text((x + 2, 5), str(x), fill=(255, 255, 0))
for y in range(0, h, 50):
    d.line([(0, y), (w, y)], fill=(255, 0, 0, 128))
    d.text((5, y + 2), str(y), fill=(255, 255, 0))

grid.save("scratch/dog_real_grid.png")
print("Saved scratch/dog_real_grid.png")
