from PIL import Image
import os, glob

# Check where dogs appear in other folders
for p in sorted(glob.glob("scratch/**/*.png") + glob.glob("scratch/**/*.jpg")):
    if any(k in p.lower() for k in ["dog", "retriever", "companion"]):
        print(p)
