import urllib.parse
import urllib.request
import os
import time
from PIL import Image

TARGET_DIR = "/Users/zengcode/projects/autoclip/assets/google-maps-universe-reel/images"
os.makedirs(TARGET_DIR, exist_ok=True)

prompts = {
    "scene-02-scale-4-billion.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "A colossal 3D universe survey mapping 4 billion galaxies and quasars. "
        "Billions of sparkling galaxy points floating in deep navy blue and black cosmic space. "
        "Layered depth with bright galaxy clusters in the midground and faint distant clusters receding into infinity. "
        "Cinematic volumetric lighting, realistic astronomy simulation. Pure clean photography, ZERO text, ZERO labels, ZERO watermarks, ZERO diagrams."
    ),
    "scene-03-cosmic-web.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "The enormous glowing cosmic web structure of the universe. "
        "Interconnected filaments of dark matter and gas glowing in ethereal cyan and warm golden light, "
        "linking bright galaxy cluster nodes across billions of light years. "
        "Dramatic three-dimensional depth, foreground filaments crossing into background depths, "
        "majestic scale, no text, no HUD, no watermark, clean documentary shot."
    ),
    "scene-04-empty-voids.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "A colossal cosmic void, a vast empty region of deep space surrounded by glowing curved walls of galaxies. "
        "Atmospheric rim light catching the edges of surrounding galaxy filaments, "
        "deep mysterious darkness in the center conveying immense silence and scale. "
        "Clean lower subtitle area, breathtaking space documentary art, no text, no watermarks, no diagrams."
    ),
    "scene-05-dark-energy.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "Visualizing Dark Energy expanding the fabric of space-time. "
        "Subtle ethereal violet-magenta and amber energy waves stretching and accelerating the distant galaxy clusters apart. "
        "Volumetric cosmic glow, beautiful physical phenomenon, cinematic lighting, "
        "sharp stars, deep space contrast, ZERO text, ZERO labels, ZERO HUD, no watermarks."
    ),
    "scene-06-cosmic-time-machine.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "Deep cosmic time machine view. Looking back over 10 billion years into the early universe. "
        "Distant infant galaxies glowing with redshifted warm amber, infrared, and soft crimson light, "
        "contrasted against nearer bluish spiral galaxies. "
        "JWST ultra deep field aesthetic, sublime cosmic depth, no text, no labels, no watermarks."
    ),
    "scene-07-future-physics.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "An advanced next-generation space telescope observatory floating in deep space, "
        "gleaming golden mirror segments, dark thermal shield, precision scientific sensors collecting cosmic light. "
        "Volumetric starlight and faint planetary nebula in the background, "
        "realistic high-tech engineering detail, cinematic depth of field, ZERO text, ZERO logos, ZERO watermarks."
    ),
    "scene-08-human-perspective.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "A solitary human silhouette standing on the rocky edge of a desert canyon at night, "
        "gazing in awe up at a magnificent, towering Milky Way arch and luminous starry cosmos. "
        "Warm starlight reflecting gently off rugged foreground rocks, deep navy sky, "
        "philosophical human connection to the infinite universe, clean lower center, no text, no watermarks."
    )
}

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')]
urllib.request.install_opener(opener)

for filename, p in prompts.items():
    dest_path = os.path.join(TARGET_DIR, filename)
    print(f"Generating {filename}...")
    encoded = urllib.parse.quote(p)
    seed = abs(hash(filename)) % 100000
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed}"
    
    success = False
    for attempt in range(3):
        try:
            urllib.request.urlretrieve(url, dest_path)
            # Verify and ensure 1080x1920
            img = Image.open(dest_path)
            if img.size != (1080, 1920):
                img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                img.save(dest_path, "PNG")
            print(f"  [OK] {filename} saved ({img.size})")
            success = True
            break
        except Exception as e:
            print(f"  [Retry {attempt+1}] Error: {e}")
            time.sleep(2)
    if not success:
        print(f"  [FAIL] Could not generate {filename}")

print("All scenes generation completed.")
