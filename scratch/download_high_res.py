import urllib.request
import time

urls = {
    "booster_final_approach.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Starship_Booster_Return_on_Final_Approach_%2854063904149%29.jpg",
    "starship_mars_spacex.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/ed/SpaceX_Starship_and_Mars.jpg",
    "starship_sn9_pad.jpg": "https://upload.wikimedia.org/wikipedia/commons/3/33/Starship_SN9_Launch_Pad.jpg",
}

for name, url in urls.items():
    dest = f"scratch/starship_raw/{name}"
    print(f"Downloading {name}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as out:
        out.write(resp.read())
    print(f"Saved {dest}")
    time.sleep(1)

