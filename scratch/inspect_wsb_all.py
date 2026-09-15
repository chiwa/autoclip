from PIL import Image

for i in range(1, 8):
    p = f"assets/where_space_begins_reel/images/scene-{i:02d}*.png"
    import glob
    files = glob.glob(p)
    if files:
        im = Image.open(files[0])
        print(files[0], im.size)
        thumb = im.convert("RGB").resize((270, 480))
        thumb.save(f"scratch/thumb_wsb_{i}.jpg", quality=80)
