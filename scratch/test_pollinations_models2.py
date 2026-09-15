import urllib.parse
import urllib.request
from PIL import Image

models = ["flux", "turbo", "sana"]
prompt = "cinematic vertical 9:16 shot of astronomer standing with golden retriever dog on mountain observatory at night looking up at starry sky"

for m in models:
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?model={m}&seed=123"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            out = f"scratch/test_{m}_simple.jpg"
            with open(out, "wb") as f:
                f.write(data)
            im = Image.open(out)
            print(f"Model {m}: SUCCESS, size={im.size}")
    except Exception as e:
        print(f"Model {m}: FAILED, {e}")
