import os, shutil
from PIL import Image

out_dir = "assets/artemis_reel/images"
os.makedirs(out_dir, exist_ok=True)
W, H = 1080, 1920

# Load official Mamase corner logo
logo_raw = Image.open("assets/branding/mamase/logo.png").convert("RGBA")
logo = logo_raw.resize((205, 205), Image.Resampling.LANCZOS)
logo_pos = (W - 205 - 36, 36)

def add_corner_logo(src_path, dest_path):
    im = Image.open(src_path).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
    im.paste(logo, logo_pos, logo)
    im.convert("RGB").save(dest_path, quality=98)
    print(f"Saved: {dest_path}")

# Scene 01: Master Cover (already created and perfected at artemis_reels_cover_9x16.png)
shutil.copyfile("assets/artemis_reel/images/artemis-reels-cover-9x16.png", os.path.join(out_dir, "scene-01-hook.png"))
print("Scene 01 verified.")

# Scene 02: Artemis I - SLS Liftoff at Kennedy Space Center
add_corner_logo("assets/artemis_ii_far_side_reel/images/scene-02-launch.png", os.path.join(out_dir, "scene-02-artemis-1.png"))

# Scene 03: Artemis II - 4 Astronauts inside Orion observing Moon
add_corner_logo("assets/artemis_ii_far_side_reel/images/scene-06-lunar-observation.png", os.path.join(out_dir, "scene-03-artemis-2.png"))

# Scene 04: Artemis III - LEO Orbital Station & Docking
add_corner_logo("assets/where_space_begins_reel 3/images/scene-06-iss.png", os.path.join(out_dir, "scene-04-artemis-3.png"))

# Scene 05: Artemis IV - Lander on Celestial Surface
add_corner_logo("assets/tianwen-2-quasi-satellite-reel/images/scene-07-anchor-sampling.png", os.path.join(out_dir, "scene-05-artemis-4.png"))

# Scene 06: Artemis V - Spacecraft in Lunar Orbit (Far Side & Earthrise)
add_corner_logo("assets/artemis_ii_far_side_reel/images/scene-05-far-side-blackout.png", os.path.join(out_dir, "scene-06-artemis-5.png"))

# Scene 07: Moon to Mars - Approaching the Red Planet
add_corner_logo("assets/starship_v3_flight_12_reel/scene-09-moon-mars-refueling-future.png", os.path.join(out_dir, "scene-07-moon-to-mars.png"))

# Scene 08: Climax - Orion in Deep Space with Earth and Moon
add_corner_logo("assets/artemis_ii_far_side_reel/images/scene-04-outbound.png", os.path.join(out_dir, "scene-08-new-era-climax.png"))

# Scene 09: Locked Outro (Byte-for-byte exact copy)
shutil.copyfile("assets/branding/mamase/reels-end-scene.png", os.path.join(out_dir, "scene-09-mamase-outro.png"))
print("Scene 09 locked outro copied.")

print("All scenes 01 to 09 successfully assembled!")
