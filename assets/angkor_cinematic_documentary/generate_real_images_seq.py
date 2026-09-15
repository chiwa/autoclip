import os
import time
import urllib.parse
import urllib.request
from PIL import Image

img_dir = "/Users/zengcode/projects/autoclip/assets/angkor_cinematic_documentary/images"

prompts = {
    3: "Cinematic view from top of Kulen Mountain looking down at a vast plain. Epic golden sunlight, morning mist, warm sandstone.",
    4: "Epic aerial drone shot of ancient Angkor city at its peak. Monumental sandstone temples, vast barays, intricate canals. Golden sunlight.",
    5: "Cinematic wide shot of an immense ancient reservoir reflecting the sun. Intricate canal systems, lush rice fields, deep teal shadows.",
    6: "Low-angle shot of ancient artisans constructing a massive sandstone temple. Moving huge stone blocks. Sunlight flaring through pillars.",
    7: "Majestic wide shot of the completed Angkor Wat. Golden sunrise illuminating the massive stone causeway. Cinematic lighting.",
    8: "Cinematic close-up tracking shot along a highly detailed sandstone bas-relief of ancient Khmer soldiers marching. Warm lighting.",
    9: "Intense cinematic shot of ancient naval warfare on Tonle Sap lake. Ancient wooden war boats clashing. Fire and smoke reflecting on water.",
    10: "Cinematic shot of massive stone faces of the Bayon temple being constructed. Golden morning light. People traveling on a Naga bridge.",
    11: "Bustling ancient Khmer marketplace. Diverse traders, artisans exchanging goods. Warm sunlight, colorful historical clothing.",
    12: "Cinematic shot of ancient merchant ships departing down a wide river towards the sea. Troops marching along a dirt road.",
    13: "Cinematic wide shot of a harsh, dry massive reservoir bed. Cracked earth, dry canals. Dusty warm sandstone, oppressive bright sunlight.",
    14: "Violent monsoon rain pouring down. Flash floods violently eroding massive earthen dikes and ancient sandstone water channels.",
    15: "Peaceful cinematic shot of Angkor Wat gradually being embraced by lush jungle vegetation. Sunlight piercing through morning mist. Warm sandstone.",
    16: "Clean modern cinematic studio background. Deep teal and warm gold ambient lighting. Professional documentary style."
}

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')]
urllib.request.install_opener(opener)

def download_pollination(prompt, filepath):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1920&height=1080&nologo=true&seed=888"
    print(f"Downloading {os.path.basename(filepath)}...")
    for _ in range(3):
        try:
            urllib.request.urlretrieve(url, filepath)
            return True
        except Exception as e:
            if '429' in str(e):
                print(f"429 Too Many Requests, sleeping 2s...")
                time.sleep(2)
            else:
                print(f"Failed to download: {e}")
                return False
    return False

for i in range(3, 17):
    out_path = os.path.join(img_dir, f"scene-{i:02d}.jpg")
    if download_pollination(prompts[i], out_path):
        # converting to PNG to replace the placeholder
        try:
            img = Image.open(out_path)
            png_path = os.path.join(img_dir, f"scene-{i:02d}.png")
            img.save(png_path, "PNG")
            os.remove(out_path)
            print(f"Converted to {png_path}")
        except Exception as e:
            print(e)
    time.sleep(1.5)

print("Done sequential!")
