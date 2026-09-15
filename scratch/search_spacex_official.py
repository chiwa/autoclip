import urllib.request
import urllib.parse
import json
import time

def search_files(query, limit=5):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "MamaseVideoProducer/1.0 (contact: user@example.com)"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        results = []
        for pid, info in pages.items():
            title = info.get("title", "")
            ii = info.get("imageinfo", [{}])[0]
            w = ii.get("width", 0)
            h = ii.get("height", 0)
            u = ii.get("url", "")
            if w and h and u and u.lower().endswith((".jpg", ".png", ".jpeg")):
                results.append({"title": title, "w": w, "h": h, "url": u})
        return results
    except Exception as e:
        print(f"Error for {query}: {e}")
        return []

searches = [
    '"Integrated Flight Test" liftoff',
    '"Starship" liftoff SpaceX',
    '"Starship" "Integrated Flight Test 4"',
    '"Starship" "Integrated Flight Test 5"',
    '"Starlink" deployment orbit',
    '"Starship" plasma reentry'
]

for s in searches:
    time.sleep(1.5)
    print(f"=== {s} ===")
    res = search_files(s, 5)
    for r in res:
        print(f"{r['w']}x{r['h']} | {r['title']} | {r['url']}")
