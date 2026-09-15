import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUTPUT_DIR = "assets/pluto_demoted_reel"
W, H = 1080, 1920

def apply_safe_area_vignette(img, dark_start=1330):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(dark_start, H):
        factor = (y - dark_start) / (H - dark_start)
        alpha = int(245 * (factor ** 1.3))
        draw.line([(0, y), (W, y)], fill=(2, 4, 10, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def add_film_grain(img, intensity=7):
    arr = np.array(img).astype(np.float32)
    grain = np.random.normal(0, intensity, arr.shape)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

# ==============================================================================
# SCENE 02: THE 1930 DISCOVERY - ZEISS BLINK COMPARATOR
# ==============================================================================
def perfect_scene_02():
    print("--- Perfecting Scene 02: Zeiss Blink Comparator ---")
    base = Image.new("RGBA", (W, H), (8, 10, 16, 255))
    draw = ImageDraw.Draw(base)
    
    # 1. Background: Warm vintage Lowell Observatory interior (dark wood & soft amber glow)
    for y in range(H):
        t = y / H
        # Deep vintage wooden tones with soft warm ambient illumination in the center
        ambient = math.exp(-((y - 700)/500)**2)
        r = int(10 + 12 * (1 - t) + 16 * ambient)
        g = int(8 + 8 * (1 - t) + 10 * ambient)
        b = int(14 + 14 * (1 - t) + 8 * ambient)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    # Vertical tongue-and-groove dark oak wall slats in background
    for x in range(0, W, 45):
        draw.line([(x, 0), (x, 1100)], fill=(5, 6, 9, 90), width=2)
        draw.line([(x+1, 0), (x+1, 1100)], fill=(25, 20, 15, 60), width=1)
        
    # 2. Main Hero Subject: The Zeiss Blink Comparator (lowell_blink_comparator.jpg)
    comp = Image.open("scratch/pluto_raw/lowell_blink_comparator.jpg").convert("RGBA")
    cw, ch = comp.size
    
    # Clean crop: remove museum table placards completely (crop out bottom 36%)
    # x: 40 to 1900, y: 10 to 1420
    crop_m = comp.crop((int(cw * 0.02), int(ch * 0.01), int(cw * 0.98), int(ch * 0.64)))
    
    # Scale to fill width with slight border
    scale = (W * 1.04) / crop_m.width
    target_w = int(crop_m.width * scale)
    target_h = int(crop_m.height * scale)
    crop_res = crop_m.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Enrich colors: warm glowing amber, deep cast iron blacks, rich brass
    cr, cg, cb, ca = crop_res.split()
    cr = cr.point(lambda p: min(255, int(p * 1.15)))
    cg = cg.point(lambda p: min(255, int(p * 1.02)))
    cb = cb.point(lambda p: min(255, int(p * 0.88)))
    comp_graded = Image.merge("RGBA", (cr, cg, cb, ca))
    
    # Feather top and bottom
    m_mask = Image.new("L", comp_graded.size, 255)
    md = ImageDraw.Draw(m_mask)
    for y in range(90):
        md.line([(0, y), (target_w, y)], fill=int(255 * (y / 90.0)))
    for y in range(target_h - 110, target_h):
        md.line([(0, y), (target_w, y)], fill=int(255 * ((target_h - y) / 110.0)))
        
    paste_x = (W - target_w) // 2
    paste_y = 160
    base.paste(comp_graded, (paste_x, paste_y), m_mask)
    
    # 3. Superimpose authentic discovery starfield negative into the illuminated aperture!
    # The glowing circle is at x: 330, y: 160 + 580 = 740, radius ~ 150px
    plates_raw = Image.open("scratch/pluto_raw/pluto_discovery_plates.png").convert("RGBA")
    pw, ph = plates_raw.size
    p_star = plates_raw.crop((int(pw * 0.08), int(ph * 0.12), int(pw * 0.42), int(ph * 0.88))).resize((280, 280))
    ap_mask = Image.new("L", (280, 280), 0)
    ImageDraw.Draw(ap_mask).ellipse([10, 10, 270, 270], fill=210)
    ap_mask = ap_mask.filter(ImageFilter.GaussianBlur(6))
    
    sr, sg, sb, sa = p_star.split()
    sr = sr.point(lambda p: min(255, int(p * 1.35)))
    sg = sg.point(lambda p: min(255, int(p * 1.10)))
    sb = sb.point(lambda p: min(255, int(p * 0.75)))
    p_star_warm = Image.merge("RGBA", (sr, sg, sb, sa))
    base.paste(p_star_warm, (330 - 140, 740 - 140), ap_mask)
    
    # Amber volumetric light halo
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for gr in range(350, 40, -18):
        alpha = int(50 * (1.0 - gr / 350.0) ** 1.6)
        gd.ellipse([330 - gr, 740 - gr, 330 + gr, 740 + gr], fill=(255, 195, 75, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    base.paste(glow, (0, 0), glow)
    
    # 4. Foreground: Dark Polished Mahogany Observatory Desk (y: 1050 to 1920)
    desk = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(desk)
    for y in range(1050, H):
        t = (y - 1050) / (H - 1050)
        mr = int((50 + 15 * math.sin(y * 0.03)) * (1.0 - t * 0.92))
        mg = int((28 + 9 * math.sin(y * 0.03)) * (1.0 - t * 0.92))
        mb = int((16 + 5 * math.sin(y * 0.03)) * (1.0 - t * 0.92))
        dd.line([(0, y), (W, y)], fill=(mr, mg, mb, 255))
        
    # Polished brass desk rail
    dd.line([(0, 1052), (W, 1052)], fill=(190, 150, 70, 230), width=3)
    dd.line([(0, 1055), (W, 1055)], fill=(80, 55, 25, 250), width=2)
    
    # Authentic vintage astronomical tools on desk (Zero text! Pure visual instruments)
    # Brass magnifying glass / loupe on the right desk
    loupe = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    ld = ImageDraw.Draw(loupe)
    # Glass lens with warm reflection
    ld.ellipse([20, 20, 140, 140], fill=(255, 240, 200, 35))
    ld.ellipse([20, 20, 140, 140], outline=(200, 160, 75, 220), width=5)
    ld.ellipse([23, 23, 137, 137], outline=(255, 220, 110, 180), width=2)
    # Brass handle
    ld.line([(135, 135), (200, 200)], fill=(180, 140, 60, 240), width=10)
    ld.line([(137, 137), (202, 202)], fill=(255, 220, 100, 180), width=3)
    loupe = loupe.filter(ImageFilter.GaussianBlur(1))
    
    # Shadow under loupe
    l_shadow = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    ImageDraw.Draw(l_shadow).ellipse([30, 30, 160, 160], fill=(0, 0, 0, 120))
    l_shadow = l_shadow.filter(ImageFilter.GaussianBlur(8))
    desk.paste(l_shadow, (720, 1100), l_shadow)
    desk.paste(loupe, (730, 1090), loupe)
    
    # Glass photographic plate negative resting on desk (left side, y: 1090)
    plate_desk = Image.new("RGBA", (320, 240), (0, 0, 0, 0))
    pdd = ImageDraw.Draw(plate_desk)
    # Glass plate bevel
    pdd.rectangle([10, 10, 310, 230], fill=(15, 18, 25, 220))
    pdd.rectangle([10, 10, 310, 230], outline=(140, 160, 190, 150), width=2)
    # Star dots on negative
    np.random.seed(1930)
    for _ in range(80):
        nx = np.random.randint(25, 295)
        ny = np.random.randint(25, 215)
        pdd.point((nx, ny), fill=(240, 240, 240, 200))
    plate_desk = plate_desk.filter(ImageFilter.GaussianBlur(1))
    
    # Rotate plate slightly
    plate_desk_rot = plate_desk.rotate(8, expand=True, resample=Image.Resampling.BICUBIC)
    desk.paste(plate_desk_rot, (110, 1090), plate_desk_rot)
    
    # Atmospheric warm light pool on desk
    desk_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dgd = ImageDraw.Draw(desk_glow)
    for r in range(500, 40, -20):
        alpha = int(35 * (1.0 - r / 500.0) ** 1.4)
        dgd.ellipse([540 - r, int(1220 - r * 0.5), 540 + r, int(1220 + r * 0.5)], fill=(255, 185, 75, alpha))
    desk_glow = desk_glow.filter(ImageFilter.GaussianBlur(28))
    desk.paste(desk_glow, (0, 0), desk_glow)
    base.paste(desk, (0, 0), desk)
    
    # 5. Safe Area Vignette & Final Touches
    final = apply_safe_area_vignette(base.convert("RGB"), dark_start=1330)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-02-discovery.png")
    final.save(out_path, "PNG")
    print(f"Scene 02 perfected: {out_path} ({os.path.getsize(out_path):,} bytes)")

# ==============================================================================
# SCENE 03: THE STRANGE ANOMALY (Unified Cinematic Solar System)
# ==============================================================================
def perfect_scene_03():
    print("--- Perfecting Scene 03: Unified Cinematic Solar System ---")
    canvas = Image.new("RGBA", (W, H), (2, 4, 10, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Cosmic Deep Space Background
    for y in range(H):
        t = y / H
        r = int(2 + 4 * (1 - t) + 8 * math.exp(-((y - 650)/450)**2))
        g = int(4 + 7 * (1 - t) + 12 * math.exp(-((y - 650)/450)**2))
        b = int(12 + 16 * (1 - t) + 26 * math.exp(-((y - 650)/450)**2))
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(1717)
    for _ in range(1000):
        sx = np.random.randint(0, W)
        sy = np.random.randint(0, 1450)
        bright = np.random.randint(80, 255)
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
            
    # Volumetric Cosmic Nebulae
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    for _ in range(120):
        nx = np.random.normal(W * 0.5, 280)
        ny = np.random.normal(680, 320)
        nr = np.random.randint(70, 240)
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(12, 24, 60, 14))
    nebula = nebula.filter(ImageFilter.GaussianBlur(35))
    canvas.paste(nebula, (0, 0), nebula)
    
    # 2. Distant Sun at (W // 2, 360)
    sun_x, sun_y = W // 2, 360
    sun_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sun_glow)
    for gr in range(350, 10, -10):
        alpha = int(75 * (1.0 - gr / 350.0) ** 1.8)
        sgd.ellipse([sun_x - gr, sun_y - gr, sun_x + gr, sun_y + gr], fill=(255, 225, 140, alpha))
    for deg in range(0, 360, 12):
        rad = math.radians(deg)
        rlen = np.random.randint(220, 420)
        ex = sun_x + rlen * math.cos(rad)
        ey = sun_y + rlen * math.sin(rad) * 0.65
        sgd.line([(sun_x, sun_y), (ex, ey)], fill=(255, 240, 180, 18), width=3)
    sun_glow = sun_glow.filter(ImageFilter.GaussianBlur(10))
    canvas.paste(sun_glow, (0, 0), sun_glow)
    draw.ellipse([sun_x - 15, sun_y - 15, sun_x + 15, sun_y + 15], fill=(255, 255, 255, 255))
    draw.ellipse([sun_x - 24, sun_y - 24, sun_x + 24, sun_y + 24], fill=(255, 245, 200, 170))
    
    # 3. 3D Solar System Orbits (Ecliptic Plane)
    cam_tilt = 0.36
    planet_orbits = [
        {"r": 140, "name": "Jupiter", "col": (180, 150, 110, 70), "w": 1},
        {"r": 220, "name": "Saturn",  "col": (200, 170, 120, 90), "w": 2},
        {"r": 310, "name": "Uranus",  "col": (90, 190, 220, 110), "w": 2},
        {"r": 420, "name": "Neptune", "col": (30, 140, 255, 240), "w": 3, "glow": True}
    ]
    
    ecliptic_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ecliptic_layer)
    for deg in range(0, 360, 20):
        rad = math.radians(deg)
        rx = sun_x + 480 * math.cos(rad)
        ry = sun_y + 480 * math.sin(rad) * cam_tilt + (480 * math.sin(rad) * 0.15)
        ed.line([(sun_x, sun_y), (rx, ry)], fill=(35, 65, 110, 35), width=1)
        
    for p in planet_orbits:
        pr = p["r"]
        pw = p["w"]
        pcol = p["col"]
        pts = []
        for deg in range(0, 361, 2):
            rad = math.radians(deg)
            px = sun_x + pr * math.cos(rad)
            py = sun_y + pr * math.sin(rad) * cam_tilt + (pr * math.sin(rad) * 0.15)
            pts.append((px, py))
            
        for i in range(len(pts) - 1):
            ed.line([pts[i], pts[i+1]], fill=pcol, width=pw)
        if p.get("glow"):
            for i in range(len(pts) - 1):
                ed.line([pts[i], pts[i+1]], fill=(20, 100, 255, 50), width=8)
                
    canvas.paste(ecliptic_layer, (0, 0), ecliptic_layer)
    
    # 4. Realistic Neptune on its Orbit (NASA Voyager 2)
    nep_deg = 210
    n_rad = math.radians(nep_deg)
    nep_x = int(sun_x + 420 * math.cos(n_rad))
    nep_y = int(sun_y + 420 * math.sin(n_rad) * cam_tilt + (420 * math.sin(n_rad) * 0.15))
    
    nep_raw = Image.open("scratch/pluto_raw/neptune_full.jpg").convert("RGBA")
    nep_sphere = nep_raw.resize((48, 48), Image.Resampling.LANCZOS)
    nep_mask = Image.new("L", (48, 48), 0)
    ImageDraw.Draw(nep_mask).ellipse([2, 2, 46, 46], fill=255)
    
    for r in range(45, 10, -4):
        draw.ellipse([nep_x - r, nep_y - r, nep_x + r, nep_y + r], fill=(20, 110, 255, int(45 * (1 - r/45))))
    canvas.paste(nep_sphere, (nep_x - 24, nep_y - 24), nep_mask)
    
    # 5. Pluto's Inclined 17° Golden Orbit
    pluto_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pld = ImageDraw.Draw(pluto_layer)
    
    a = 420
    b = 390
    e = 0.2488
    c = a * e
    tilt_rad = math.radians(28) # Pronounced 17° physical tilt projection
    arg_peri = math.radians(-32)
    
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
        sy = sun_y + y_3d * cam_tilt + (y_3d * 0.15) - (z_3d * 0.75)
        
        pl_pts.append((sx, sy))
        pl_z.append(z_3d)
        
    for i in range(len(pl_pts) - 1):
        pt1, pt2 = pl_pts[i], pl_pts[i+1]
        z = pl_z[i]
        if z >= 0:
            alpha = int(min(255, 175 + z * 0.65))
            pld.line([pt1, pt2], fill=(255, 215, 90, alpha), width=4)
            pld.line([pt1, pt2], fill=(255, 180, 50, int(alpha * 0.45)), width=9)
        else:
            alpha = int(max(65, 160 + z * 0.8))
            pld.line([pt1, pt2], fill=(210, 140, 50, alpha), width=3)
            
    for idx in range(0, len(pl_pts), 10):
        pt = pl_pts[idx]
        z = pl_z[idx]
        if abs(z) > 30:
            plane_pt_y = pt[1] + (z * 0.75)
            pld.line([(pt[0], pt[1]), (pt[0], plane_pt_y)], fill=(255, 205, 110, 75), width=1)
            pld.ellipse([pt[0] - 2, plane_pt_y - 1, pt[0] + 2, plane_pt_y + 1], fill=(120, 170, 240, 110))
            
    canvas.paste(pluto_layer, (0, 0), pluto_layer)
    
    # 6. Photographic Celestial Juxtaposition: MOON VS PLUTO (y: 920 to 1280)
    # Both rendered as real worlds floating naturally in deep space!
    comp_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(comp_layer)
    
    # Earth's Moon: Diameter 3,474 km -> Size 310x310 (at x: 340, y: 1080)
    moon_raw = Image.open("scratch/pluto_raw/moon_full.jpg").convert("RGBA")
    moon_size = 310
    moon_sphere = moon_raw.resize((moon_size, moon_size), Image.Resampling.LANCZOS)
    moon_mask = Image.new("L", (moon_size, moon_size), 0)
    ImageDraw.Draw(moon_mask).ellipse([4, 4, moon_size - 4, moon_size - 4], fill=255)
    moon_mask = moon_mask.filter(ImageFilter.GaussianBlur(1))
    
    # Directional shadow on Moon (sun is at upper center)
    moon_shadow = Image.new("RGBA", (moon_size, moon_size), (0, 0, 0, 0))
    msd = ImageDraw.Draw(moon_shadow)
    for r in range(moon_size, 0, -2):
        pass # The photo already has authentic lunar lighting!
        
    for gr in range(moon_size//2 + 30, moon_size//2, -3):
        cd.ellipse([340 - gr, 1080 - gr, 340 + gr, 1080 + gr], fill=(180, 200, 235, int(25 * (1 - (gr - moon_size//2)/30))))
    comp_layer.paste(moon_sphere, (340 - moon_size//2, 1080 - moon_size//2), moon_mask)
    
    # Pluto: Diameter 2,376 km -> Accurately 2376/3474 * 310 = 212px! (at x: 740, y: 1080)
    pluto_raw = Image.open("scratch/pluto_raw/pluto_color_8k.jpg").convert("RGBA")
    pluto_size = 212
    pluto_sphere = pluto_raw.resize((pluto_size, pluto_size), Image.Resampling.LANCZOS)
    pluto_mask = Image.new("L", (pluto_size, pluto_size), 0)
    ImageDraw.Draw(pluto_mask).ellipse([3, 3, pluto_size - 3, pluto_size - 3], fill=255)
    pluto_mask = pluto_mask.filter(ImageFilter.GaussianBlur(1))
    
    for gr in range(pluto_size//2 + 30, pluto_size//2, -3):
        cd.ellipse([740 - gr, 1080 - gr, 740 + gr, 1080 + gr], fill=(240, 180, 100, int(30 * (1 - (gr - pluto_size//2)/30))))
    comp_layer.paste(pluto_sphere, (740 - pluto_size//2, 1080 - pluto_size//2), pluto_mask)
    
    canvas.paste(comp_layer, (0, 0), comp_layer)
    
    # 7. Safe Area Vignette (y: 1380 - 1920)
    final = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1330)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-03-strange-orbit.png")
    final.save(out_path, "PNG")
    print(f"Scene 03 perfected: {out_path} ({os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    perfect_scene_02()
    perfect_scene_03()
    print("Scenes 02 and 03 perfected successfully!")
