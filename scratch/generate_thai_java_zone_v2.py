import os
import time
import urllib.request
import urllib.parse
from PIL import Image, ImageFilter, ImageEnhance

TARGET_W, TARGET_H = 1080, 1920
OUT_DIR = "scratch/tjz_v2"
os.makedirs(OUT_DIR, exist_ok=True)

# Base style prefix adhering strictly to Thai Java Zone shared visual style bible:
# - clean modern software-engineering explainer
# - realistic professional developer workspace or enterprise architecture
# - soft natural lighting, dark neutral tech background, subtle depth
# - vertical 9:16 framing
# - NO text, NO watermarks, NO HUD, NO fake labels, NO cyberpunk, NO neon, NO sci-fi fantasy
BASE_PROMPT = "Clean modern software engineering explainer visual, cinematic photography, vertical 9:16 aspect ratio, dark neutral tech background, soft natural lighting, subtle depth of field, authentic professional software engineering realism, high resolution, 8k, zero text, zero watermarks, zero logos, no cyberpunk, no neon"

scenes = [
    {
        "id": "scene-01-hook",
        "name": "Hook: Why Java Dominates Enterprise",
        "seed": 101,
        "prompt": f"{BASE_PROMPT}, a focused senior software engineer at a sleek dark modern developer workstation late at night, angled over-the-shoulder view of multiple high-resolution curved monitors displaying real backend Java code and dark IDE interface, mechanical keyboard, warm desk lamp ambient glow, dark slate and charcoal room, cinematic professional developer aesthetic"
    },
    {
        "id": "scene-02-stability",
        "name": "Stability: Running Flawlessly for Decades",
        "seed": 202,
        "prompt": f"{BASE_PROMPT}, an imposing heavy-duty 42U enterprise server rack in a modern tier-4 corporate data center, perspective view looking up, neatly routed glowing blue and amber fiber optic cables, subtle status LED indicator lights, solid industrial steel chassis, reflective server room floor, rock-solid enterprise stability and hardware reliability"
    },
    {
        "id": "scene-03-enterprise-ecosystem",
        "name": "Ecosystem: Spring Boot, Kafka, Enterprise Stack",
        "seed": 303,
        "prompt": f"{BASE_PROMPT}, sophisticated enterprise software architecture war room, large dark glass wall display showing a complex distributed microservices network topology graph with interconnected service nodes and message queues, soft teal and amber subtle accent glow, modern engineering meeting room, clean technical architecture blueprint"
    },
    {
        "id": "scene-04-modern-performance",
        "name": "Modern JVM: High Throughput & Concurrency",
        "seed": 404,
        "prompt": f"{BASE_PROMPT}, macro close-up photography of a powerful enterprise server motherboard, central multi-core server CPU processor heatsink surrounded by dense high-speed DDR5 memory modules and copper heat pipes, subtle cool cyan data bus lighting pulses representing blazing high-throughput multi-threaded computing power, precision industrial hardware"
    },
    {
        "id": "scene-05-scale-and-maintainability",
        "name": "Maintainability: Large Teams & Long-term Code",
        "seed": 505,
        "prompt": f"{BASE_PROMPT}, professional enterprise software engineering office floor at dusk, collaborative tech workspace with multiple developer desks, dual-monitor workstations showing code, architectural whiteboards in background, soft natural warm evening lighting, professional developers working, clean modern corporate software engineering company"
    },
    {
        "id": "scene-06-real-world-usage",
        "name": "Mission Critical: Banking & Financial Systems",
        "seed": 606,
        "prompt": f"{BASE_PROMPT}, global financial operations center and banking NOC control room at night, tiered operator consoles with dual screens, large wall-sized curved video displays showing global transaction flow maps and live financial telemetry curves, dark ambient mood lighting, high-security mission-critical enterprise operations"
    },
    {
        "id": "scene-07-conclusion",
        "name": "Conclusion: The Backbone of Global Systems",
        "seed": 707,
        "prompt": f"{BASE_PROMPT}, sleek and elegant modern software engineering cockpit setup, vertical framing, dual premium displays showing completed green deployment build metrics and stable production monitoring charts, warm ambient lighting on wooden desk mat with ergonomic keyboard, calm confident finish, dark neutral slate aesthetic"
    }
]

print("Starting generation of 7 Thai Java Zone master images...")
for sc in scenes:
    sc_id = sc["id"]
    out_raw = os.path.join(OUT_DIR, f"{sc_id}_raw.jpg")
    out_final = os.path.join(OUT_DIR, f"{sc_id}.png")
    
    encoded = urllib.parse.quote(sc["prompt"])
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1344&nologo=true&model=turbo&seed={sc['seed']}"
    
    print(f"\n[Scene {sc_id}] Generating: {sc['name']}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    
    success = False
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = resp.read()
                with open(out_raw, "wb") as f:
                    f.write(data)
                success = True
                break
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}, retrying in 3s...")
            time.sleep(3)
            
    if not success:
        print(f"FAILED {sc_id}")
        continue
        
    # High-quality processing to 1080x1920 PNG
    im = Image.open(out_raw)
    # Scale to 1080x1920 with Lanczos
    im_scaled = im.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    
    # Subtle enhancement: slight contrast & sharpness to make details pop
    enh_contrast = ImageEnhance.Contrast(im_scaled)
    im_enh = enh_contrast.enhance(1.05)
    
    enh_sharp = ImageEnhance.Sharpness(im_enh)
    im_final = enh_sharp.enhance(1.1)
    
    # Save final lossless PNG
    im_final.save(out_final, format="PNG", optimize=True)
    fsize = os.path.getsize(out_final)
    print(f"  -> Saved {out_final}: 1080x1920 PNG ({fsize:,} bytes)")
    time.sleep(2)

print("\nAll generations finished!")
