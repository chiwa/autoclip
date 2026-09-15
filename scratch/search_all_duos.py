import os
from PIL import Image

for root, dirs, files in os.walk("assets"):
    for f in files:
        if f.endswith(('.png', '.jpg')) and any(k in f.lower() for k in ['scene-08', 'scene-07', 'scene-06', 'scene-01', 'payoff', 'human', 'look']):
            p = os.path.join(root, f)
            print(p)
