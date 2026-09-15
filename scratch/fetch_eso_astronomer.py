import urllib.request
import json

def get_wiki_image_url(title):
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size&format=json"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'AutoClipBot/1.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        pages = data['query']['pages']
        for page_id in pages:
            if 'imageinfo' in pages[page_id]:
                return pages[page_id]['imageinfo'][0]
    return None

import urllib.parse
info1 = get_wiki_image_url("File:Starry Night at La Silla.jpg")
print("La Silla info:", info1)

info2 = get_wiki_image_url("File:An Astronomer's Outlook (15883573804).jpg")
print("Astronomer Outlook info:", info2)
