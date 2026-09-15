import requests, os
from PIL import Image

out_dir = "assets/voyager1_reel/raw"
os.makedirs(out_dir, exist_ok=True)

# Let's fetch high-res public domain NASA/JPL/ESO scientific photography
urls = {
    # 1. Voyager 1 in Space / Golden Record artist concept (NASA/JPL-Caltech)
    "voyager_space": "https://upload.wikimedia.org/wikipedia/commons/d/d2/Voyager_spacecraft_model.png",
    # 2. Golden Record Cover (NASA/JPL) - ultra high-res
    "golden_record": "https://upload.wikimedia.org/wikipedia/commons/5/56/Voyager_Golden_Record_Cover.png",
    # 3. Deep Space Network 70-meter antenna at Goldstone or Canberra under starry night sky
    "dsn_antenna": "https://upload.wikimedia.org/wikipedia/commons/e/e4/70-meter_Antenna_at_Goldstone%2C_California.jpg",
    # 4. Pale Blue Dot (Earth from Voyager 1 at 6 billion km)
    "pale_blue_dot": "https://upload.wikimedia.org/wikipedia/commons/7/73/Pale_Blue_Dot.png",
    # 5. Interstellar medium / Milky way star clouds (NASA Hubble / ESO)
    "milkyway_eso": "https://upload.wikimedia.org/wikipedia/commons/6/60/ESO_-_Milky_Way.jpg"
}

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

for name, url in urls.items():
    dest = os.path.join(out_dir, f"{name}.jpg" if not url.endswith(".png") else f"{name}.png")
    if not os.path.exists(dest):
        print(f"Downloading {name}...")
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            with open(dest, "wb") as f:
                f.write(r.content)
            print(f"Downloaded {name} ({len(r.content)} bytes)")
        else:
            print(f"Failed {name}: {r.status_code}")
    else:
        print(f"{name} already exists")

