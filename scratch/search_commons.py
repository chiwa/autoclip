import urllib.request
import urllib.parse
import json

def search_commons(query, limit=5):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        results = []
        for pid, info in pages.items():
            title = info.get("title")
            ii = info.get("imageinfo", [{}])[0]
            results.append({
                "title": title,
                "width": ii.get("width"),
                "height": ii.get("height"),
                "url": ii.get("url"),
                "mime": ii.get("mime")
            })
        return results
    except Exception as e:
        print(f"Error {e}")
        return []

queries = [
    "Starship Flight 4",
    "Starship Flight 5",
    "Starship Boca Chica launch",
    "Starship re-entry",
    "Starship booster splashdown",
    "Starlink deployment",
    "Raptor vacuum engine",
    "Starship Mars"
]

for q in queries:
    print(f"=== {q} ===")
    res = search_commons(q, 3)
    for r in res:
        print(f" - {r.get('title')}: {r.get('width')}x{r.get('height')} -> {r.get('url')}")
