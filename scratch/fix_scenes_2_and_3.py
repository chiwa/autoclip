import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H = 1080, 1920
OUTPUT_DIR = "assets/pluto_demoted_reel"

def apply_safe_area_vignette(img, dark_start=1380):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(dark_start, H):
        factor = (y - dark_start) / (H - dark_start)
        alpha = int(215 * (factor ** 1.3))
        draw.line([(0, y), (W, y)], fill=(2, 4, 10, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def add_film_grain(img, intensity=5):
    arr = np.array(img).astype(np.float32)
    grain = np.random.normal(0, intensity, arr.shape)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

# ==============================================================================
# PERFECT SCENE 02: FULL VERTICAL ZEISS COMPARATOR
# ==============================================================================
def build_scene_02():
    print("--- Building Perfect Scene 02 ---")
    # In lowell_blink_comparator.jpg (1941x2226):
    # The comparator is tall!
    # Let's crop x: 20 to 1920, y: 10 to 1850 (taking almost the full height, masking out only the small paper card)
    comp = Image.open("scratch/pluto_raw/lowell_blink_comparator.jpg").convert("RGB")
    cw, ch = comp.size
    
    # Crop to 9:16 aspect ratio directly from the high-res authentic photograph!
    # In 1941x2226, 9:16 crop width = ch * 9 / 16 = 2226 * 9 / 16 = 1252!
    crop_w = int(ch * 9 / 16) # 1252
    crop_x1 = int((cw - crop_w) * 0.46) # center on the machine and illuminated aperture
    crop_y1 = 0
    crop = comp.crop((crop_x1, crop_y1, crop_x1 + crop_w, ch))
    
    # Resize to 1080x1920!
    res = crop.resize((W, H), Image.Resampling.LANCZOS)
    
    # On the bottom right desk area of this crop, there's a museum paper card.
    # Let's cleanly blend dark mahogany wood over that card!
    # In 1080x1920, the paper card is at roughly x: 620-1040, y: 1280-1650.
    res_rgba = res.convert("RGBA")
    wood_patch = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wpd = ImageDraw.Draw(wood_patch)
    for y in range(1200, H):
        t = (y - 1200) / (H - 1200)
        alpha = int(min(255, 30 + 225 * (t ** 0.8)))
        # Match the dark mahogany table tone
        wpd.line([(0, y), (W, y)], fill=(35, 22, 14, alpha))
        
    # Soft mask so it only covers the lower desk and museum cards
    wood_patch = wood_patch.filter(ImageFilter.GaussianBlur(15))
    res_rgba = Image.alpha_composite(res_rgba, wood_patch)
    
    # Now, superimpose the REAL Pluto discovery starfield negative into the illuminated aperture!
    # In the 9:16 crop, where is the glowing aperture?
    # Original aperture center in 1941x2226 was roughly x: 620, y: 1080.
    # After crop (crop_x1 ~ 316) and scale (1080/1252 = 0.8626):
    # ap_x = (620 - 316) * 0.8626 ≈ 262
    # ap_y = 1080 * (1920 / 2226) ≈ 931
    ap_x, ap_y = 265, 930
    
    plates_raw = Image.open("scratch/pluto_raw/pluto_discovery_plates.png").convert("RGBA")
    pw, ph = plates_raw.size
    p_star = plates_raw.crop((int(pw * 0.08), int(ph * 0.12), int(pw * 0.42), int(ph * 0.88))).resize((270, 270))
    
    ap_mask = Image.new("L", (270, 270), 0)
    ImageDraw.Draw(ap_mask).ellipse([10, 10, 260, 260], fill=215)
    ap_mask = ap_mask.filter(ImageFilter.GaussianBlur(6))
    
    sr, sg, sb, sa = p_star.split()
    sr = sr.point(lambda p: min(255, int(p * 1.35)))
    sg = sg.point(lambda p: min(255, int(p * 1.10)))
    sb = sb.point(lambda p: min(255, int(p * 0.75)))
    p_star_warm = Image.merge("RGBA", (sr, sg, sb, sa))
    res_rgba.paste(p_star_warm, (ap_x - 135, ap_y - 135), ap_mask)
    
    # Warm volumetric amber backlight
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for gr in range(320, 30, -15):
        alpha = int(45 * (1.0 - gr / 320.0) ** 1.6)
        gd.ellipse([ap_x - gr, ap_y - gr, ap_x + gr, ap_y + gr], fill=(255, 195, 75, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    res_rgba = Image.alpha_composite(res_rgba, glow)
    
    # Enrich color grading: warm tungsten lamp glow, deep cast iron blacks, rich brass
    final = res_rgba.convert("RGB")
    final = apply_safe_area_vignette(final, dark_start=1360)
    final = ImageEnhance.Contrast(final).enhance(1.12)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-02-discovery.png")
    final.save(out_path, "PNG")
    print(f"Perfect Scene 02 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

# ==============================================================================
# PERFECT SCENE 03: FULL-FRAME 3D CELESTIAL MECHANICS & INCLINATION
# ==============================================================================
def build_scene_03():
    print("--- Building Perfect Scene 03 ---")
    canvas = Image.new("RGBA", (W, H), (3, 5, 12, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Deep Space Cosmic Background
    for y in range(H):
        t = y / H
        ambient = math.exp(-((y - 750)/500)**2)
        r = int(3 + 5 * (1 - t) + 12 * ambient)
        g = int(5 + 8 * (1 - t) + 16 * ambient)
        b = int(14 + 18 * (1 - t) + 30 * ambient)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(1717)
    for _ in range(1200):
        sx = np.random.randint(0, W)
        sy = np.random.randint(0, 1500)
        bright = np.random.randint(70, 255)
        color_type = np.random.choice(["blue", "gold", "white", "cyan"], p=[0.25, 0.2, 0.45, 0.1])
        if color_type == "blue":
            col = (int(bright * 0.8), int(bright * 0.9), bright, 240)
        elif color_type == "gold":
            col = (bright, int(bright * 0.9), int(bright * 0.65), 240)
        elif color_type == "cyan":
            col = (int(bright * 0.8), bright, bright, 240)
        else:
            col = (bright, bright, bright, 250)
            
        sz = np.random.choice([1, 1, 1, 2, 2, 3], p=[0.75, 0.12, 0.08, 0.03, 0.015, 0.005])
        if sz == 1:
            draw.point((sx, sy), fill=col)
        else:
            draw.ellipse([sx-sz, sy-sz, sx+sz, sy+sz], fill=col)
            
    # Cosmic nebulae
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    for _ in range(140):
        nx = np.random.normal(W * 0.5, 300)
        ny = np.random.normal(700, 350)
        nr = np.random.randint(90, 280)
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(16, 28, 75, 15))
    nebula = nebula.filter(ImageFilter.GaussianBlur(40))
    canvas.paste(nebula, (0, 0), nebula)
    
    # 2. Distant Sun: Glorious solar beacon at (W // 2, 280)
    sun_x, sun_y = W // 2, 280
    sun_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sun_glow)
    for gr in range(400, 10, -10):
        alpha = int(80 * (1.0 - gr / 400.0) ** 1.8)
        sgd.ellipse([sun_x - gr, sun_y - gr, sun_x + gr, sun_y + gr], fill=(255, 225, 140, alpha))
    for deg in range(0, 360, 10):
        rad = math.radians(deg)
        rlen = np.random.randint(280, 560)
        ex = sun_x + rlen * math.cos(rad)
        ey = sun_y + rlen * math.sin(rad) * 0.7
        sgd.line([(sun_x, sun_y), (ex, ey)], fill=(255, 240, 180, 18), width=3)
    sun_glow = sun_glow.filter(ImageFilter.GaussianBlur(12))
    canvas.paste(sun_glow, (0, 0), sun_glow)
    draw.ellipse([sun_x - 18, sun_y - 18, sun_x + 18, sun_y + 18], fill=(255, 255, 255, 255))
    draw.ellipse([sun_x - 28, sun_y - 28, sun_x + 28, sun_y + 28], fill=(255, 245, 200, 170))
    
    # 3. 3D Solar System Plane - Fills the central 60% of the screen!
    # Camera perspective: steep 3D oblique angle
    cam_tilt = 0.55 # Expansive vertical depth!
    
    planet_orbits = [
        {"r": 180, "col": (180, 150, 110, 60), "w": 1},
        {"r": 300, "col": (200, 170, 120, 80), "w": 2},
        {"r": 440, "col": (90, 190, 220, 100), "w": 2},
        {"r": 600, "col": (30, 140, 255, 240), "w": 4, "glow": True} # Neptune's grand orbit
    ]
    
    ecliptic_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ecliptic_layer)
    # Radial grid lines
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        rx = sun_x + 680 * math.cos(rad)
        ry = sun_y + 680 * math.sin(rad) * cam_tilt
        ed.line([(sun_x, sun_y), (rx, ry)], fill=(35, 65, 110, 30), width=1)
        
    for p in planet_orbits:
        pr = p["r"]
        pw = p["w"]
        pcol = p["col"]
        pts = []
        for deg in range(0, 361, 2):
            rad = math.radians(deg)
            px = sun_x + pr * math.cos(rad) * 1.05
            py = sun_y + pr * math.sin(rad) * cam_tilt
            pts.append((px, py))
            
        for i in range(len(pts) - 1):
            ed.line([pts[i], pts[i+1]], fill=pcol, width=pw)
        if p.get("glow"):
            for i in range(len(pts) - 1):
                ed.line([pts[i], pts[i+1]], fill=(20, 100, 255, 60), width=10)
                
    canvas.paste(ecliptic_layer, (0, 0), ecliptic_layer)
    
    # 4. Realistic Voyager 2 Neptune on Orbit (Prominently placed at left, y: 640)
    nep_deg = 215
    n_rad = math.radians(nep_deg)
    nep_x = int(sun_x + 600 * math.cos(n_rad) * 1.05)
    nep_y = int(sun_y + 600 * math.sin(n_rad) * cam_tilt)
    
    nep_raw = Image.open("scratch/pluto_raw/neptune_full.jpg").convert("RGBA")
    nep_sphere = nep_raw.resize((72, 72), Image.Resampling.LANCZOS)
    nep_mask = Image.new("L", (72, 72), 0)
    ImageDraw.Draw(nep_mask).ellipse([2, 2, 70, 70], fill=255)
    
    for r in range(65, 15, -5):
        draw.ellipse([nep_x - r, nep_y - r, nep_x + r, nep_y + r], fill=(20, 110, 255, int(50 * (1 - r/65))))
    canvas.paste(nep_sphere, (nep_x - 36, nep_y - 36), nep_mask)
    
    # 5. Pluto's Inclined 17° Golden Orbit Ribbon
    # This orbit SWOOPS across the screen, rising high above the plane and plunging down!
    pluto_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pld = ImageDraw.Draw(pluto_layer)
    
    a = 580
    b = 530
    e = 0.2488
    c = a * e
    tilt_rad = math.radians(30) # Dynamic 3D inclination
    arg_peri = math.radians(-35)
    
    pl_pts = []
    pl_z = []
    
    for deg in range(0, 361, 2):
        rad = math.radians(deg)
        x_raw = a * math.cos(rad) - c
        y_raw = b * math.sin(rad)
        
        x_rot = x_raw * math.cos(arg_peri) - y_raw * math.sin(arg_peri)
        y_rot = x_raw * math.sin(arg_peri) + y_raw * math.cos(arg_peri)
        
        x_3d = x_rot
        y_3d = y_rot * math.cos(tilt_rad)
        z_3d = y_rot * math.sin(tilt_rad)
        
        sx = sun_x + x_3d * 1.15
        sy = sun_y + y_3d * cam_tilt - (z_3d * 0.95) # 3D height above plane!
        
        pl_pts.append((sx, sy))
        pl_z.append(z_3d)
        
    for i in range(len(pl_pts) - 1):
        pt1, pt2 = pl_pts[i], pl_pts[i+1]
        z = pl_z[i]
        if z >= 0:
            alpha = int(min(255, 180 + z * 0.65))
            pld.line([pt1, pt2], fill=(255, 215, 90, alpha), width=5)
            pld.line([pt1, pt2], fill=(255, 180, 50, int(alpha * 0.45)), width=12)
        else:
            alpha = int(max(70, 160 + z * 0.8))
            pld.line([pt1, pt2], fill=(215, 145, 55, alpha), width=3)
            
    # Vertical altitude lines connecting Pluto's tilted orbit down to the ecliptic plane
    for idx in range(0, len(pl_pts), 8):
        pt = pl_pts[idx]
        z = pl_z[idx]
        if abs(z) > 25:
            plane_pt_y = pt[1] + (z * 0.95)
            pld.line([(pt[0], pt[1]), (pt[0], plane_pt_y)], fill=(255, 210, 110, 75), width=1)
            pld.ellipse([pt[0] - 2, plane_pt_y - 1, pt[0] + 2, plane_pt_y + 1], fill=(120, 170, 240, 100))
            
    # Position Pluto heroically on its high arc at (x: 820, y: 760)
    p_idx = 108
    pluto_center = (int(pl_pts[p_idx][0]), int(pl_pts[p_idx][1]))
    
    # 6. HERO PLUTO SPHERE ON TRACK (Photographic 8k Pluto!)
    pluto_raw = Image.open("scratch/pluto_raw/pluto_color_8k.jpg").convert("RGBA")
    pw, ph = pluto_raw.size
    pcx, pcy, prad = pw // 2, ph // 2, int(min(pw, ph) * 0.38)
    pluto_crop = pluto_raw.crop((pcx - prad, pcy - prad, pcx + prad, pcy + prad))
    
    hero_pluto_sz = 140
    pluto_sphere = pluto_crop.resize((hero_pluto_sz, hero_pluto_sz), Image.Resampling.LANCZOS)
    pluto_mask = Image.new("L", (hero_pluto_sz, hero_pluto_sz), 0)
    ImageDraw.Draw(pluto_mask).ellipse([3, 3, hero_pluto_sz - 3, hero_pluto_sz - 3], fill=255)
    pluto_mask = pluto_mask.filter(ImageFilter.GaussianBlur(1))
    
    # Atmospheric golden haze around Pluto
    for gr in range(hero_pluto_sz//2 + 35, hero_pluto_sz//2, -4):
        pld.ellipse([pluto_center[0] - gr, pluto_center[1] - gr, pluto_center[0] + gr, pluto_center[1] + gr],
                    fill=(240, 180, 90, int(35 * (1 - (gr - hero_pluto_sz//2)/35))))
                    
    canvas.paste(pluto_layer, (0, 0), pluto_layer)
    canvas.paste(pluto_sphere, (pluto_center[0] - hero_pluto_sz//2, pluto_center[1] - hero_pluto_sz//2), pluto_mask)
    
    # 7. SCALE INSET: EARTH'S MOON VS PLUTO (y: 1100 to 1340)
    # Clean, organic, beautiful celestial comparison floating seamlessly in space!
    # No artificial colored rings!
    scale_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sld = ImageDraw.Draw(scale_layer)
    
    # Soft celestial dust aura behind comparison
    for gr in range(350, 40, -25):
        alpha = int(18 * (1.0 - gr / 350.0) ** 1.5)
        sld.ellipse([W//2 - gr, 1220 - int(gr * 0.4), W//2 + gr, 1220 + int(gr * 0.4)], fill=(20, 35, 75, alpha))
        
    # Earth's Moon: 3474 km -> 210px at (x: 360, y: 1220)
    moon_raw = Image.open("scratch/pluto_raw/moon_full.jpg").convert("RGBA")
    mw, mh = moon_raw.size
    mcx, mcy, mrad = mw // 2, mh // 2, int(min(mw, mh) * 0.42)
    moon_crop = moon_raw.crop((mcx - mrad, mcy - mrad, mcx + mrad, mcy + mrad))
    
    moon_sz = 210
    moon_sp = moon_crop.resize((moon_sz, moon_sz), Image.Resampling.LANCZOS)
    moon_m = Image.new("L", (moon_sz, moon_sz), 0)
    ImageDraw.Draw(moon_m).ellipse([2, 2, moon_sz - 2, moon_sz - 2], fill=255)
    moon_m = moon_m.filter(ImageFilter.GaussianBlur(1))
    
    # Soft natural lunar glow
    for gr in range(moon_sz//2 + 20, moon_sz//2, -3):
        sld.ellipse([360 - gr, 1220 - gr, 360 + gr, 1220 + gr], fill=(180, 205, 240, int(16 * (1 - (gr - moon_sz//2)/20))))
    scale_layer.paste(moon_sp, (360 - moon_sz//2, 1220 - moon_sz//2), moon_m)
    
    # Pluto: 2376 km -> Accurately 2376/3474 * 210 = 144px at (x: 700, y: 1220)
    p_comp_sz = 144
    pluto_sp = pluto_crop.resize((p_comp_sz, p_comp_sz), Image.Resampling.LANCZOS)
    pluto_m = Image.new("L", (p_comp_sz, p_comp_sz), 0)
    ImageDraw.Draw(pluto_m).ellipse([2, 2, p_comp_sz - 2, p_comp_sz - 2], fill=255)
    pluto_m = pluto_m.filter(ImageFilter.GaussianBlur(1))
    
    for gr in range(p_comp_sz//2 + 20, p_comp_sz//2, -3):
        sld.ellipse([700 - gr, 1220 - gr, 700 + gr, 1220 + gr], fill=(240, 180, 100, int(20 * (1 - (gr - p_comp_sz//2)/20))))
    scale_layer.paste(pluto_sp, (700 - p_comp_sz//2, 1220 - p_comp_sz//2), pluto_m)
    
    canvas.paste(scale_layer, (0, 0), scale_layer)
    
    # 8. Safe Area Vignette & Polish
    final = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1380)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-03-strange-orbit.png")
    final.save(out_path, "PNG")
    print(f"Perfect Scene 03 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    build_scene_02()
    build_scene_03()
    print("Batch 1 refined!")
