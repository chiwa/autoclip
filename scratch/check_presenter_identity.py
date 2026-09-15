from PIL import Image

p1 = Image.open("assets/characters/mamase-presenter-v1.png")
print("mamase-presenter-v1:", p1.size, p1.mode)

p2 = Image.open("assets/characters/mamase-presenter-cutout.png")
print("mamase-presenter-cutout:", p2.size, p2.mode)
