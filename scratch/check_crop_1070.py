from PIL import Image

fg = Image.open("scratch/test_iss_fg_1000.png")
# Crop from y=70 downwards: this is y=1070 to 1920 of full canvas!
clean_fg = fg.crop((0, 70, 1080, 920))
clean_fg.save("scratch/clean_iss_fg_1070.png")
print("Saved clean_iss_fg_1070.png, size:", clean_fg.size)
