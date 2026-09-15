import os
from PIL import Image

for root, dirs, files in os.walk("assets"):
    for f in files:
        if any(w in f.lower() for w in ["char", "presenter", "cutout", "dog", "explorer", "duo"]):
            print(os.path.join(root, f))

for root, dirs, files in os.walk("scratch"):
    for f in files:
        if any(w in f.lower() for w in ["char", "presenter", "cutout", "dog", "explorer", "duo"]):
            print(os.path.join(root, f))
