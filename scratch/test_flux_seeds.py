import urllib.parse
import urllib.request
from PIL import Image

# We want:
# Location: High-altitude Atacama Desert astronomical observatory, with large white radio telescope dish or dome in background
# Subjects: A young male astronomer explorer (wearing modern expedition field jacket, standing in 3/4 profile or side view, looking through binoculars or pointing up at the sky) and his standing fluffy golden retriever dog
# Hero subject: In the dark night sky, two brilliant twin golden suns (Alpha Centauri A and B) glowing with solar corona and lens flares
# Composition: Vertical 9:16, clean open dark sky in top 40% for text, hero stars in upper-mid, observatory deck and standing duo in lower 40%

prompt = (
    "photograph of a modern astronomical observatory deck at night under a pristine starry sky. "
    "On the right side of the deck, an athletic young man in a dark navy technical outdoor jacket and warm beanie stands in side profile looking up through binoculars at the night sky. "
    "Beside his legs stands a healthy fluffy golden retriever dog looking up attentively in the same direction. "
    "In the dark sky above, two brilliant twin golden binary stars Alpha Centauri shine radiantly like twin miniature suns with glowing flares. "
    "In the background, a white radio telescope dish and silhouetted desert mountains. "
    "Cinematic lighting, national geographic photography, 8k, photorealistic, sharp focus, 35mm photograph, award winning, zero text, zero watermark"
)

url_base = "https://image.pollinations.ai/prompt/"
encoded = urllib.parse.quote(prompt)

for seed in [12, 88, 305]:
    url = f"{url_base}{encoded}?width=768&height=1344&model=flux&seed={seed}&nologo=true"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
            out = f"scratch/flux_seed_{seed}.jpg"
            with open(out, "wb") as f:
                f.write(data)
            im = Image.open(out)
            print(f"Seed {seed}: success, size={im.size}")
    except Exception as e:
        print(f"Seed {seed}: failed {e}")
