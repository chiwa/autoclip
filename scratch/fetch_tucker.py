import urllib.request
import json
import urllib.parse

api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote('File:Golden Retriever standing Tucker.jpg')}&prop=imageinfo&iiprop=url|size&format=json"
req = urllib.request.Request(api_url, headers={'User-Agent': 'AutoClipBot/1.0'})
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    pages = data['query']['pages']
    for page_id in pages:
        if 'imageinfo' in pages[page_id]:
            print(pages[page_id]['imageinfo'][0])
