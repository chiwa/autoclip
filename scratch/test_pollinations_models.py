import urllib.parse
import urllib.request
from PIL import Image
import os

prompt = (
    "cinematic 9:16 vertical photorealistic photograph of a young male astronomer explorer standing on a high altitude observatory observation deck at night in the Atacama desert, wearing a modern navy tactical field jacket and beanie, standing next to his loyal fluffy golden retriever dog who is standing proudly looking up. In the upper night sky, two brilliant glowing twin golden suns of Alpha Centauri shine intensely in deep space. 8k, photorealistic, masterpiece, sharp focus, cinematic lighting, 35mm lens, national geographic photography, clean empty dark space at the very top of the frame."
)

for model in ["flux", "flux-realism", "turbo"]:
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1080&height=1920&model={model}&nologo=true&seed=101"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=40) as resp:
            data = resp.read()
            out_file = f"scratch/test_{model}.jpg"
            with open(out_file, "wb") as f:
                f.write(data)
            im = Image.open(out_file)
            print(f"Model {model}: success, size={im.size}")
    except Exception as e:
        print(f"Model {model}: failed {e}")
