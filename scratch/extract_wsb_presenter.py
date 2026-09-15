from rembg import remove
from PIL import Image

inp = Image.open("assets/where_space_begins_reel/images/scene-01-hook.png")
out = remove(inp)
out.save("scratch/wsb_presenter_cutout.png")
print("Saved wsb_presenter_cutout.png, size:", out.size)
