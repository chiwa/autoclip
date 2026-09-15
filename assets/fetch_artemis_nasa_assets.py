import requests, os

out_dir = "assets/artemis_reel/raw"
os.makedirs(out_dir, exist_ok=True)

urls = {
    # 1. Artemis III: Orion & Starship HLS in orbit
    "artemis3_hls": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Starship_HLS_rendering.png/1280px-Starship_HLS_rendering.png",
    # 2. Artemis IV: Astronauts on Lunar South Pole surface
    "artemis4_surface": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Artemis_astronauts_on_the_Moon_%28PIA24177%29.jpg/1280px-Artemis_astronauts_on_the_Moon_%28PIA24177%29.jpg",
    # 3. Artemis V: Lunar Gateway in orbit around the Moon
    "artemis5_gateway": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Lunar_Gateway_orbiting_the_Moon.png/1280px-Lunar_Gateway_orbiting_the_Moon.png",
    # 4. Artemis I Earthrise (Orion solar array wing selfie with Earth & Moon)
    "artemis1_earthrise": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Artemis_I_Flight_Day_13_-_Earth_and_Moon_%28NHQ202211280001%29.jpg/1280px-Artemis_I_Flight_Day_13_-_Earth_and_Moon_%28NHQ202211280001%29.jpg"
}

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

for name, url in urls.items():
    dest = os.path.join(out_dir, f"{name}.png" if ".png" in url else f"{name}.jpg")
    if not os.path.exists(dest):
        print(f"Downloading {name}...")
        try:
            r = requests.get(url, headers=headers, timeout=25)
            if r.status_code == 200:
                with open(dest, "wb") as f:
                    f.write(r.content)
                print(f"Downloaded {name} ({len(r.content)} bytes)")
            else:
                print(f"Failed {name}: status {r.status_code}")
        except Exception as e:
            print(f"Error {name}: {e}")
    else:
        print(f"{name} already exists")
