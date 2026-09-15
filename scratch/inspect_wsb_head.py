from PIL import Image

wsb = Image.open("assets/where_space_begins_reel/images/scene-01-hook.png")
print("WSB dimensions:", wsb.size)
# Where is the head located? Let's crop x=100..700, y=100..800
head = wsb.crop((100, 100, 700, 800))
head.save("scratch/wsb_head.png")
print("Saved scratch/wsb_head.png")
