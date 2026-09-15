import urllib.parse
import urllib.request
from PIL import Image

prompt = (
    "photorealistic master key art, 35mm photograph, a young male explorer in dark winter parka and beanie standing beside his alert golden retriever dog on an astronomical observatory deck at night, looking up in awe at the starry cosmos. High altitude desert mountains in the background. Cinematic lighting, rich navy and warm starlight contrast, 8k resolution, crisp details, award-winning national geographic documentary photography, no text, no watermark"
)

url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=768&height=1344&model=flux&seed=555&nologo=true"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as resp:
    data = resp.read()
    with open("scratch/test_flux_aspect.jpg", "wb") as f:
        f.write(data)

im = Image.open("scratch/test_flux_aspect.jpg")
print("FLUX Aspect ratio test size:", im.size)
