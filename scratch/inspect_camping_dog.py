from PIL import Image

im = Image.open("scratch/camping_dog.jpg")
print("Camping dog size:", im.size)
# What is in this 5184x3456 photo?
thumb = im.resize((800, int(im.height * 800 / im.width)))
thumb.save("scratch/camping_dog_thumb.jpg")
print("Saved scratch/camping_dog_thumb.jpg")
