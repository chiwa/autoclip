from PIL import Image

wsb = Image.open("assets/where_space_begins_reel/images/scene-01-hook.png")
face = wsb.crop((0, 0, 520, 700))
face.save("scratch/wsb_face_glasses.png")
print("Saved scratch/wsb_face_glasses.png")
