from PIL import Image

im = Image.open("assets/planet_nine_reel/images/scene-08-cosmic-frontier.png")
im.crop((0, 0, 1080, 1100)).save("scratch/frontier_top.jpg", quality=90)
print("Saved scratch/frontier_top.jpg")
