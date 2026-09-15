import urllib.parse
import urllib.request
import os
import time
from PIL import Image

TARGET_DIR = "/Users/zengcode/projects/autoclip/assets/google-maps-universe-reel/images"

better_prompts = {
    "scene-02-scale-4-billion.png": (
        "Cinematic astronomy visualization of the largest 3D universe map, DESI survey style. "
        "A dense, intricate 3D point cloud of 4 billion galaxies, quasars, and star clusters glowing in gold, cyan, and white. "
        "Vast observable universe sphere with rich multi-layered depth, volumetric galaxy clusters, "
        "intricate astronomical data visualization, clean deep space, 8k documentary art, ZERO text, ZERO watermarks, ZERO labels."
    ),
    "scene-03-cosmic-web.png": (
        "Majestic 3D cosmic web filaments, interconnected glowing neural-like network of dark matter and gas, "
        "threads of cyan, gold, and white light connecting dense spherical galaxy clusters across billions of light years. "
        "Complex three-dimensional structure filling 75% of the frame with incredible depth and volumetric glow, "
        "cinematic science documentary benchmark, clean background, ZERO text, ZERO watermarks."
    ),
    "scene-04-empty-voids.png": (
        "Cosmic void astronomy view. An enormous dark empty cavern in deep space, "
        "framed all around by glowing walls of intricate cosmic web filaments and glittering galaxy clusters. "
        "Stunning scale contrast between the vast quiet void and the luminous surrounding web, "
        "cinematic deep space lighting, rich textures, ZERO text, ZERO watermarks."
    ),
    "scene-05-dark-energy.png": (
        "Dark Energy accelerating cosmic expansion. Breathtaking visualization of space-time fabric expanding, "
        "glowing galaxy clusters moving outward along subtle ethereal violet, magenta, and amber energy wavefields. "
        "Volumetric cosmic lighting, majestic astrophysical phenomenon, high contrast, clean starry backdrop, ZERO text, ZERO labels."
    ),
    "scene-06-cosmic-time-machine.png": (
        "JWST ultra deep space telescope field, cosmic time machine looking 13 billion years into the past. "
        "Dozens of distinct glowing infant galaxies, redshifted warm amber, crimson, and golden ancient proto-galaxies, "
        "gravitational lensing arcs curving around massive foreground galaxy clusters, deep cosmic blackness, hyper-detailed, ZERO text, ZERO watermarks."
    ),
    "scene-07-future-physics.png": (
        "Giant next-generation space telescope floating in deep space, majestic gold hexagonal mirror segments reflecting cosmic light, "
        "sleek titanium truss structure, multi-layer silver thermal sunshield gleaming in sunlight. "
        "Distant colorful nebulae and sharp stars in background, authentic aerospace engineering, crisp sharp details, ZERO text, ZERO logos, ZERO watermarks."
    )
}

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')]
urllib.request.install_opener(opener)

for filename, p in better_prompts.items():
    dest_path = os.path.join(TARGET_DIR, filename)
    print(f"Regenerating {filename}...")
    encoded = urllib.parse.quote(p)
    # Use different distinct seeds
    seed = abs(hash(filename + "_v2")) % 100000 + 54321
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed}"
    
    for attempt in range(3):
        try:
            urllib.request.urlretrieve(url, dest_path)
            img = Image.open(dest_path)
            if img.size != (1080, 1920):
                img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                img.save(dest_path, "PNG")
            print(f"  [OK] {filename} saved ({img.size})")
            break
        except Exception as e:
            print(f"  [Retry {attempt+1}] Error: {e}")
            time.sleep(2)

print("Regeneration completed.")
