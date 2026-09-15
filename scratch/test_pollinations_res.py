import urllib.parse
import urllib.request
from PIL import Image

for w, h in [(1024, 1024), (896, 1152), (832, 1216), (768, 1024)]:
    url = f"https://image.pollinations.ai/prompt/stars?width={w}&height={h}&model=turbo&seed=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            out = f"scratch/test_{w}_{h}.jpg"
            with open(out, "wb") as f:
                f.write(data)
            im = Image.open(out)
            print(f"Requested {w}x{h} -> got {im.size}")
    except Exception as e:
        print(f"Requested {w}x{h} -> failed {e}")
