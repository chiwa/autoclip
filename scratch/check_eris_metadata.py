from PIL import Image
from PIL.ExifTags import TAGS

im = Image.open("assets/branding/mamase/reference/eris-master-reels-visual-reference.jpg")
print("Size:", im.size)
print("Format:", im.format)
print("Info keys:", im.info.keys())
for k, v in im.info.items():
    if k != "exif":
        print(f"{k}: {str(v)[:200]}")
