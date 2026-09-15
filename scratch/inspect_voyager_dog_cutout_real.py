from PIL import Image

# Check scratch/voyager_dog_cutout.png and scratch/iss_dog_crop.png
for p in ["scratch/voyager_dog_cutout.png", "scratch/iss_dog_crop.png"]:
    im = Image.open(p)
    print(p, im.size, im.mode)
