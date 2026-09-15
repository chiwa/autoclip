import urllib.parse
import urllib.request

prompt = "Premium cinematic historical documentary key art. Extremely massive glowing 3D cosmic web map of the universe, 4 billion galaxies connected by dark energy filaments. Deep space navy blue, glowing cyan and warm gold rim lights. Volumetric lighting, epic scale, hyper-detailed structure. Empty space on the bottom right for a presenter."
encoded = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed=101"

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

try:
    urllib.request.urlretrieve(url, "/Users/zengcode/projects/autoclip/assets/scene-01-bg-only.png")
    print("SUCCESS")
except Exception as e:
    print("ERROR", e)
