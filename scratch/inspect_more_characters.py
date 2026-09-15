from PIL import Image
import os

for p in [
    "assets/google-maps-universe-reel/images/scene-08-human-perspective.png",
    "assets/light_year_distance_reel/images/scene-04-voyager-human-speed.png",
    "scratch/camping_dog.jpg"
]:
    im = Image.open(p)
    print(p, im.size, im.mode)
    name = os.path.basename(p).replace(".png", "").replace(".jpg", "")
    thumb = im.resize((600, int(im.height * 600 / im.width)), Image.Resampling.LANCZOS)
    thumb.save(f"scratch/prev_{name}.jpg", quality=85)
print("Done.")
