from PIL import Image

for i in [2, 3, 4, 5, 6, 7, 8]:
    p = f"assets/voyager1_reel/images/scene-{i:02d}*.png"
    import glob
    files = glob.glob(p)
    if files:
        im = Image.open(files[0]).convert("RGB")
        thumb = im.resize((270, 480))
        thumb.save(f"scratch/thumb_voyager_{i}.jpg", quality=80)
        print(f"Saved scratch/thumb_voyager_{i}.jpg")
