import urllib.request, json, os

out_dir = "assets/voyager1_reel/raw"
os.makedirs(out_dir, exist_ok=True)

# Search for Deep space network night or radio telescope night
headers = {"User-Agent": "MamaseEducationalBot/1.0 (https://mamase.org)"}
query = "Goldstone%2070%20meter%20night"
url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={query}&gsrnamespace=6&prop=imageinfo&iiprop=url&format=json"

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        pages = data.get("query", {}).get("pages", {})
        for pid, p in pages.items():
            print(p["title"], p.get("imageinfo", [{}])[0].get("url"))
except Exception as e:
    print("Error:", e)
