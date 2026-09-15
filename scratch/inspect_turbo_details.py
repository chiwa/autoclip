from PIL import Image

im = Image.open("scratch/test_turbo.jpg")
print("Turbo image size:", im.size)
# Let's crop the human and dog
chars = im.crop((150, 200, 480, 1000))
chars.save("scratch/turbo_chars.jpg", quality=95)
print("Saved scratch/turbo_chars.jpg")
