import urllib.request, os

out_dir = "assets/voyager1_reel/raw"
os.makedirs(out_dir, exist_ok=True)

targets = {
    "golden_record_cover.jpg": "https://upload.wikimedia.org/wikipedia/commons/5/56/The_Sounds_of_Earth_Record_Cover_-_GPN-2000-001978.jpg",
    "dss43_canberra_70m.jpg": "https://upload.wikimedia.org/wikipedia/commons/9/9c/DSS43_is_a_70-meter-wide_%28230-feet-wide%29_radio_antenna_at_the_Deep_Space_Network%27s_Canberra_facility_in_Australia.jpg",
    "voyager_model.png": "https://upload.wikimedia.org/wikipedia/commons/6/60/Voyager_spacecraft_model.png"
}

headers = {"User-Agent": "MamaseEducationalBot/1.0 (https://mamase.org)"}

for filename, url in targets.items():
    dest = os.path.join(out_dir, filename)
    if not os.path.exists(dest):
        print(f"Downloading {filename}...")
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
            f.write(resp.read())
        print(f"Saved {filename} ({os.path.getsize(dest)} bytes)")
    else:
        print(f"{filename} exists.")
