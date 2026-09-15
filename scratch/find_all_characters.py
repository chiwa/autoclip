import os
from PIL import Image

for root, dirs, files in os.walk("."):
    if any(p in root for p in [".git", "node_modules", ".venv"]):
        continue
    for f in files:
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and any(w in f.lower() for w in ['presenter', 'explorer', 'character', 'dog', 'person', 'human', 'camping']):
            p = os.path.join(root, f)
            try:
                im = Image.open(p)
                print(f"{p}: size={im.size}")
            except:
                pass
