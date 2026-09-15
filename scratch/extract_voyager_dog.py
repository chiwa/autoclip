from PIL import Image
from rembg import remove

voy = Image.open("assets/voyager1_reel/images/scene-01-hook.png")
# The dog is located around x=400..680, y=1280..1650
dog_crop = voy.crop((400, 1260, 680, 1680))
dog_crop.save("scratch/voyager_dog_crop.png")

dog_cutout = remove(dog_crop)
dog_cutout.save("scratch/voyager_dog_cutout.png")
print("Saved voyager_dog_cutout.png, size:", dog_cutout.size)
