import urllib.request
from PIL import Image

url = "https://upload.wikimedia.org/wikipedia/commons/3/30/Starry_Night_at_La_Silla.jpg"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = resp.read()
    with open("scratch/la_silla.jpg", "wb") as f:
        f.write(data)

im = Image.open("scratch/la_silla.jpg")
print("Downloaded La Silla! Size:", im.size)
thumb = im.resize((800, int(im.height * 800 / im.width)))
thumb.save("scratch/la_silla_thumb.jpg")
