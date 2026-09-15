import os
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

TARGET_W = 1080
TARGET_H = 1920

out_dir = "assets/rogue_planets_reel/images"
os.makedirs(out_dir, exist_ok=True)

# Logo Setup
logo_raw = Image.open("assets/branding/mamase/logo.png").convert("RGBA")
logo_size = 205
logo = logo_raw.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
logo_x = TARGET_W - logo_size - 36
logo_y = 36

l_shadow = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
l_shadow.paste(Image.new("RGBA", (logo_size, logo_size), (0, 0, 0, 220)), (logo_x, logo_y + 3), mask=logo.split()[3])
l_shadow = l_shadow.filter(ImageFilter.GaussianBlur(12))

def apply_logo(im):
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    # Check if logo is already present in upper right by inspecting pixel around (940, 140)
    # If not, composite it
    im = Image.alpha_composite(im, l_shadow)
    im.paste(logo, (logo_x, logo_y), mask=logo)
    return im.convert("RGB")

print("--- Assembling Mamase Rogue Planets Reel Scenes ---")

# Scene 01: Master Key Art (already verified & saved)
print("1. Scene 01: Preserving user-approved Key Art...")
# scene-01-hook.png is already in out_dir

# Scene 02: Scale & Numbers (Countless rogue worlds drifting in Milky Way)
print("2. Scene 02: Cosmic starry ocean of rogue worlds...")
s2_base = Image.open("assets/interstellar_space_reel/images/scene-08-cosmic-cradle.png").convert("RGB")
s2_enh = ImageEnhance.Color(s2_base).enhance(1.05)
s2_enh = ImageEnhance.Contrast(s2_enh).enhance(1.05)
s2_enh.save(os.path.join(out_dir, "scene-02-scale-galaxy-ocean.png"), quality=98)

# Scene 03: Origin (Gravitational ejection by giant gas planet)
print("3. Scene 03: Gravitational ejection by proto-planetary giant...")
s3_base = Image.open("assets/planet_nine_reel/images/scene-03-massive-sculptor.png").convert("RGB")
s3_enh = ImageEnhance.Color(s3_base).enhance(1.08)
s3_enh.save(os.path.join(out_dir, "scene-03-gravitational-ejection.png"), quality=98)

# Scene 04: Extreme Cold (-200C frozen surface with ice crystals)
print("4. Scene 04: Frozen nitrogen & methane ice crust surface...")
s4_base = Image.open("assets/eris_reel/images/scene-05-atmospheric-collapse.png").convert("RGB")
s4_enh = ImageEnhance.Color(s4_base).enhance(1.05)
s4_enh = ImageEnhance.Brightness(s4_enh).enhance(0.96) # deep cold tone
s4_enh.save(os.path.join(out_dir, "scene-04-frozen-world-surface.png"), quality=98)

# Scene 05: Life Under Ice (Subsurface geothermal ocean & hydrothermal vents)
print("5. Scene 05: Geothermal ocean under ice...")
s5_base = Image.open("assets/ice-cold-earth/scene-08-subsurface-ocean.png").convert("RGB")
s5_fit = s5_base.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
s5_final = apply_logo(s5_fit)
s5_final.save(os.path.join(out_dir, "scene-05-subsurface-ocean-life.png"), quality=98)

# Scene 06: Detection (Gravitational Microlensing space observation)
print("6. Scene 06: Gravitational microlensing detection...")
s6_base = Image.open("assets/roman_dark_universe_reel/images/scene-08-exoplanets.png").convert("RGB")
s6_final = apply_logo(s6_base)
s6_final.save(os.path.join(out_dir, "scene-06-gravitational-microlensing.png"), quality=98)

# Scene 07: Cosmic Meaning (Solitary planet drifting past cosmic nebula)
print("7. Scene 07: Philosophical cosmic wonder...")
s7_base = Image.open("assets/edge_of_universe_reel/images/scene-08-philosophical-climax.png").convert("RGB")
s7_final = apply_logo(s7_base)
s7_final.save(os.path.join(out_dir, "scene-07-cosmic-drift-mystery.png"), quality=98)

# Scene 08: Locked Official Mamase Outro
print("8. Scene 08: Locked official Mamase outro...")
outro_src = "assets/branding/mamase/reels-end-scene.png"
outro_img = Image.open(outro_src).convert("RGB").resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
outro_img.save(os.path.join(out_dir, "scene-08-brand-outro.png"), quality=98)

print("All 8 scenes successfully assembled and saved in:", out_dir)
