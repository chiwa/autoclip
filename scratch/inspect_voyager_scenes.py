import glob

print("Voyager 1 files:")
for p in sorted(glob.glob("assets/voyager1_reel/images/*.png")):
    print(p)
