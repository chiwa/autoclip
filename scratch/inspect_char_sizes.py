from PIL import Image
for p in ["scratch/iss_chars.png", "scratch/voyager_cutout.png", "assets/crop_chars.png", "scratch/crop_chars_cutout.png"]:
    try:
        im = Image.open(p)
        print(f"{p}: size={im.size}, mode={im.mode}")
    except Exception as e:
        print(f"{p}: error {e}")
