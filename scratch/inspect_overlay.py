from PIL import Image

crop = Image.open("scratch/dog_real_crop.png")
print("Dog real crop size (W x H):", crop.size)
