from PIL import Image

im = Image.open("assets/where_space_begins_reel/images/scene-01-hook.png")
print("Where space begins scene-01:", im.size)
thumb = im.resize((600, int(im.height * 600 / im.width)))
thumb.save("scratch/wsb_scene01_thumb.jpg")
print("Saved wsb_scene01_thumb.jpg")
