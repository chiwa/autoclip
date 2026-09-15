import os
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np

def test_all():
    w, h = 1080, 1920
    
    # Scene 02: Ocean Paradox
    c2 = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    im2 = Image.open("scratch/europa_downloads/Enceladus_interior.jpg").convert("RGBA")
    s2 = 1080 / im2.width
    nh2 = int(im2.height * s2)
    im2_fit = im2.resize((1080, nh2), Image.Resampling.LANCZOS)
    arr2 = np.array(im2_fit, dtype=np.float32)
    fade = 120
    arr2[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr2[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    f2 = Image.fromarray(np.clip(arr2, 0, 255).astype(np.uint8))
    c2.paste(f2, (0, 420), f2)
    c2.convert("RGB").save("scratch/europa_preview/scene-02-ocean-paradox.png")
    print("Scene 02 OK")

    # Scene 03: Tidal Heating
    c3 = Image.new("RGBA", (w, h), (3, 5, 14, 255))
    im3 = Image.open("scratch/europa_downloads/Juice_flyby_of_Europa_artist_s_impression.jpg").convert("RGBA")
    s3 = 1080 / im3.width
    nh3 = int(im3.height * s3)
    im3_fit = im3.resize((1080, nh3), Image.Resampling.LANCZOS)
    arr3 = np.array(im3_fit, dtype=np.float32)
    arr3[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr3[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    f3 = Image.fromarray(np.clip(arr3, 0, 255).astype(np.uint8))
    c3.paste(f3, (0, 360), f3)
    # Gravitational tidal lines
    draw3 = ImageDraw.Draw(c3)
    cx, cy = 540, 720
    for r in range(240, 440, 40):
        draw3.arc([cx - r, cy - int(r*0.6), cx + r, cy + int(r*0.6)], start=30, end=150, fill=(255, 200, 100, 120), width=2)
    c3.convert("RGB").save("scratch/europa_preview/scene-03-tidal-heating.png")
    print("Scene 03 OK")

    # Scene 04: Hydrothermal Vents
    c4 = Image.new("RGBA", (w, h), (2, 3, 10, 255))
    im4 = Image.open("scratch/europa_downloads/Hydrothermal_activity_on_Enceladus.jpg").convert("RGBA")
    s4 = 1080 / im4.width
    nh4 = int(im4.height * s4)
    im4_fit = im4.resize((1080, nh4), Image.Resampling.LANCZOS)
    arr4 = np.array(im4_fit, dtype=np.float32)
    arr4[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr4[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    f4 = Image.fromarray(np.clip(arr4, 0, 255).astype(np.uint8))
    c4.paste(f4, (0, 440), f4)
    c4.convert("RGB").save("scratch/europa_preview/scene-04-hydrothermal-vents.png")
    print("Scene 04 OK")

    # Scene 05: Water Plumes
    im5 = Image.open("scratch/europa_downloads/New_evidence_of_watery_plumes_on_Jupiter_s_moon_Europa.jpg").convert("RGB")
    s5 = 1920 / im5.height
    nw5 = int(im5.width * s5)
    im5_scaled = im5.resize((nw5, 1920), Image.Resampling.LANCZOS)
    x0_5 = (nw5 - 1080) // 2
    crop5 = im5_scaled.crop((x0_5, 0, x0_5 + 1080, 1920))
    # Safe area dimming
    arr5 = np.array(crop5, dtype=np.float32)
    safe_fade = 320
    arr5[-safe_fade:, :] *= np.linspace(1.0, 0.15, safe_fade)[:, None, None]
    Image.fromarray(np.clip(arr5, 0, 255).astype(np.uint8)).save("scratch/europa_preview/scene-05-water-plumes.png")
    print("Scene 05 OK")

    # Scene 06: Europa Clipper Spacecraft
    c6 = Image.new("RGBA", (w, h), (3, 5, 14, 255))
    im6 = Image.open("scratch/europa_downloads/Europa_Clipper_artist_s_concept.jpg").convert("RGBA")
    s6 = 1080 / im6.width
    nh6 = int(im6.height * s6)
    im6_fit = im6.resize((1080, nh6), Image.Resampling.LANCZOS)
    arr6 = np.array(im6_fit, dtype=np.float32)
    arr6[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr6[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    f6 = Image.fromarray(np.clip(arr6, 0, 255).astype(np.uint8))
    c6.paste(f6, (0, 420), f6)
    c6.convert("RGB").save("scratch/europa_preview/scene-06-europa-clipper.png")
    print("Scene 06 OK")

    # Scene 07: Tasting the Plumes
    c7 = Image.new("RGBA", (w, h), (3, 5, 15, 255))
    # Base plume background
    im7_bg = Image.open("scratch/europa_downloads/New_evidence_of_watery_plumes_on_Jupiter_s_moon_Europa.jpg").convert("RGBA")
    s7 = 1080 / im7_bg.width
    nh7 = int(im7_bg.height * s7)
    im7_bg_fit = im7_bg.resize((1080, nh7), Image.Resampling.LANCZOS)
    arr7 = np.array(im7_bg_fit, dtype=np.float32)
    arr7[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr7[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    f7 = Image.fromarray(np.clip(arr7, 0, 255).astype(np.uint8))
    c7.paste(f7, (0, 380), f7)
    c7.convert("RGB").save("scratch/europa_preview/scene-07-tasting-plumes.png")
    print("Scene 07 OK")

    # Scene 08: Philosophical Climax
    im8 = Image.open("scratch/europa_downloads/Hubble_finds_evidence_of_persistent_water_vapour_atmosphere_on_Europa.jpg").convert("RGB")
    x0_8 = (im8.width - 1080) // 2
    crop8 = im8.crop((x0_8, 0, x0_8 + 1080, 1920))
    enh8 = ImageEnhance.Contrast(crop8).enhance(1.15)
    arr8 = np.array(enh8, dtype=np.float32)
    arr8[-safe_fade:, :] *= np.linspace(1.0, 0.2, safe_fade)[:, None, None]
    Image.fromarray(np.clip(arr8, 0, 255).astype(np.uint8)).save("scratch/europa_preview/scene-08-philosophical-climax.png")
    print("Scene 08 OK")

if __name__ == "__main__":
    test_all()
