import urllib.parse
import urllib.request
from PIL import Image

prompt = (
    "A stunning cinematic vertical 9:16 master shot of a breathtaking night sky over a grassy mountain ridge. "
    "Looking up at a pair of brilliant, luminous twin golden suns (Alpha Centauri A and B) glowing intensely in deep space, "
    "surrounded by a vibrant cosmic nebula of deep sapphire blue, ultramarine, violet, and sparkling stars. "
    "In the lower foreground, a silhouette of a solitary stargazer explorer in modern outdoor jacket standing next to a loyal golden retriever dog, "
    "both gazing up at the magnificent bright binary stars. Atmospheric lighting, crystal clear 8k resolution, razor sharp details, vivid saturated colors, cinematic composition, award-winning astrophotography."
)

encoded_prompt = urllib.parse.quote(prompt)
# test models: flux, sana
url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&model=flux&nologo=true&seed=42"
print("Downloading from:", url[:80], "...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as resp:
    data = resp.read()
    with open('scratch/test_flux_1080.jpg', 'wb') as f:
        f.write(data)

im = Image.open('scratch/test_flux_1080.jpg')
print("Successfully saved! Size:", im.size, "Mode:", im.mode)
