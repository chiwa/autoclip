import urllib.parse
import urllib.request
import os
import time
from PIL import Image

TARGET_DIR = "/Users/zengcode/projects/autoclip/assets/tno-time-capsule-reel/images"
os.makedirs(TARGET_DIR, exist_ok=True)

# Outro image copy
os.system(f"cp /Users/zengcode/projects/autoclip/dist/mamase-saturn-decagon-reel-v1/images/scene-09-mamase-outro.png {TARGET_DIR}/scene-09-mamase-outro.png")

prompts = {
    "scene-02-frozen-frontier.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "A cluster of dark, frozen primordial Trans-Neptunian Objects and icy asteroids floating in the deep outer solar system beyond Neptune. "
        "Distant blue gas giant Neptune glowing softly far in the background, faint point-like distant sun, "
        "realistic astronomy, sharp starlight, volumetric cosmic dust, ZERO text, ZERO labels, ZERO watermarks."
    ),
    "scene-03-absolute-zero.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "Extreme macro surface of an ancient Kuiper Belt object, crystalline water ice, frozen methane frost, "
        "reddish-brown organic tholin patches completely preserved since the dawn of the solar system. "
        "Raking dramatic sunlight highlighting pristine crater rims and sharp frozen ridges, cinematic depth of field, ZERO text, ZERO watermarks."
    ),
    "scene-04-hubble-webb-collaboration.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "The Hubble Space Telescope and the James Webb Space Telescope floating together in deep cosmos, "
        "JWST's gleaming golden hexagonal mirror array and silver sunshield in foreground, Hubble in midground, "
        "both pointing their instruments toward the deep outer solar system. "
        "Realistic aerospace engineering, volumetric starlight, ZERO text, ZERO logos, ZERO watermarks."
    ),
    "scene-05-75-spectra-analysis.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "A field of multiple glowing icy Trans-Neptunian Objects in deep space, "
        "subtle ethereal rainbow-colored infrared diffraction spikes and optical spectroscopic light rays converging from their surfaces. "
        "Scientific astronomical imaging, breathtaking cosmic depth, deep navy space, ZERO text, ZERO diagrams, ZERO watermarks."
    ),
    "scene-06-solar-system-birth.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "The early solar system 4.5 billion years ago, a colossal swirling protoplanetary accretion disk of glowing gas and molten dust surrounding the newborn Sun. "
        "Icy boulders and planetesimals condensing at the cold outer rim, dramatic orange and deep space navy contrast, "
        "epic origin of planets, ZERO text, ZERO labels, ZERO watermarks."
    ),
    "scene-07-planetary-migration.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "Majestic gas giant planets Jupiter and Saturn migrating in the ancient solar system, "
        "their immense gravitational forces scattering thousands of icy comets and asteroids toward the outer Kuiper Belt. "
        "Dynamic orbital arcs of dust, volumetric golden sunlight, deep blue space, cinematic scale, ZERO text, ZERO watermarks."
    ),
    "scene-08-understanding-our-roots.png": (
        "High-budget cinematic science documentary visual, 8k resolution. "
        "Dramatic low-angle view across the rugged icy horizon of a distant Trans-Neptunian Object, "
        "looking across millions of miles back toward the inner solar system where planet Earth and the glowing Sun shine like brilliant beacons in the dark infinite cosmos. "
        "Sublime philosophical perspective, sparkling ice reflections, clean lower center, ZERO text, ZERO watermarks."
    )
}

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')]
urllib.request.install_opener(opener)

for filename, p in prompts.items():
    dest_path = os.path.join(TARGET_DIR, filename)
    print(f"Generating {filename}...")
    encoded = urllib.parse.quote(p)
    seed = abs(hash(filename + "_tno_v1")) % 100000 + 12345
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

print("TNO scenes generation completed.")
