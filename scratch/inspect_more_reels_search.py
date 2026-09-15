import os, glob

# Let's search all .png and .jpg files in assets/ and scratch/ to see if there is any other standing explorer/dog
all_imgs = glob.glob("assets/**/*.png", recursive=True) + glob.glob("scratch/**/*.png", recursive=True)
print(f"Total images found: {len(all_imgs)}")
# Check files with 'scene' or 'cover' or 'character' or 'explorer'
for p in all_imgs:
    low = p.lower()
    if any(k in low for k in ["man", "guy", "explorer", "presenter", "pee", "standing", "human", "character"]):
        print(p)
