from PIL import Image
import os

for p in [
    "assets/forever_young_story/draft/presenter-candidate-a.png",
    "assets/forever_young_story/draft/presenter-candidate-b-active-male.png"
]:
    im = Image.open(p)
    print(p, im.size)
    thumb = im.resize((600, int(im.height * 600 / im.width)))
    thumb.save(f"scratch/{os.path.basename(p)}.jpg", quality=85)
print("Done.")
