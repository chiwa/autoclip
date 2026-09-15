from PIL import Image

wsb = Image.open("assets/where_space_begins_reel/images/scene-01-hook.png")
# The face is further to the right!
# Let's crop x=300..900, y=50..700
face = wsb.crop((300, 50, 900, 700))
face.save("scratch/wsb_face_pos.png")
print("Saved scratch/wsb_face_pos.png")
