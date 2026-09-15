from PIL import Image
import os, glob

# Let's search for all images in assets/ or scratch/ that might have the golden dog
files = glob.glob("assets/**/*.png", recursive=True) + glob.glob("assets/**/*.jpg", recursive=True)
for f in files:
    if "dog" in f.lower() or "retriever" in f.lower() or "companion" in f.lower() or "golden" in f.lower():
        print(f)

