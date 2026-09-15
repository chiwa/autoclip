import os
OUTPUT_DIR = "assets/pluto_demoted_reel"
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H = 1080, 1920

def build_scene_03():
    print("--- Building Heroic Scene 03 ---")
    canvas = Image.new("RGBA", (W, H), (2, 4, 10, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Volumetric Deep Space Background
    for y in range(H):
        t = y / H
        ambient = math.exp(-((y - 650)/450)**2)
        r = int(2 + 4 * (1 - t) + 10 * ambient)
        g = int(4 + 6 * (1 - t) + 14 * ambient)
        b = int(12 + 16 * (1 - t) + 28 * ambient)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(1717)
    for _ in range(1200):
        sx = np.random.randint(0, W)
        sy = np.random.randint(0, 1450)
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
            
    # Rich cosmic nebular clouds
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    for _ in range(140):
        nx = np.random.normal(W * 0.5, 300)
        ny = np.random.normal(600, 320)
        nr = np.random.randint(90, 280)
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(14, 28, 70, 14))
    nebula = nebula.filter(ImageFilter.GaussianBlur(40))
    canvas.paste(nebula, (0, 0), nebula)
    
    # 2. Distant Sun: Glorious solar beacon at (320, 240)
    sun_x, sun_y = 320, 240
    sun_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sun_glow)
    for gr in range(400, 10, -10):
        alpha = int(80 * (1.0 - gr / 400.0) ** 1.8)
        sgd.ellipse([sun_x - gr, sun_y - gr, sun_x + gr, sun_y + gr], fill=(255, 225, 140, alpha))
    for deg in range(0, 360, 10):
        rad = math.radians(deg)
        rlen = np.random.randint(280, 550)
        ex = sun_x + rlen * math.cos(rad)
        ey = sun_y + rlen * math.sin(rad) * 0.7
        sgd.line([(sun_x, sun_y), (ex, ey)], fill=(255, 240, 180, 18), width=3)
    sun_glow = sun_glow.filter(ImageFilter.GaussianBlur(12))
    canvas.paste(sun_glow, (0, 0), sun_glow)
    draw.ellipse([sun_x - 18, sun_y - 18, sun_x + 18, sun_y + 18], fill=(255, 255, 255, 255))
    draw.ellipse([sun_x - 28, sun_y - 28, sun_x + 28, sun_y + 28], fill=(255, 245, 200, 170))
    
    # 3. 3D Solar System Plane (Expansive perspective)
    cam_tilt = 0.42
    planet_orbits = [
        {"r": 180, "col": (180, 150, 110, 60), "w": 1},
        {"r": 290, "col": (200, 170, 120, 80), "w": 2},
        {"r": 420, "col": (90, 190, 220, 100), "w": 2},
        {"r": 560, "col": (30, 140, 255, 240), "w": 4, "glow": True} # Neptune
    ]
    
    ecliptic_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ecliptic_layer)
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        rx = sun_x + 650 * math.cos(rad)
        ry = sun_y + 650 * math.sin(rad) * cam_tilt + (650 * math.sin(rad) * 0.18)
        ed.line([(sun_x, sun_y), (rx, ry)], fill=(35, 65, 110, 30), width=1)
        
    for p in planet_orbits:
        pr = p["r"]
        pw = p["w"]
        pcol = p["col"]
        pts = []
        for deg in range(0, 361, 2):
            rad = math.radians(deg)
            px = sun_x + pr * math.cos(rad) * 1.05
            py = sun_y + pr * math.sin(rad) * cam_tilt + (pr * math.sin(rad) * 0.18)
            pts.append((px, py))
            
        for i in range(len(pts) - 1):
            ed.line([pts[i], pts[i+1]], fill=pcol, width=pw)
        if p.get("glow"):
            for i in range(len(pts) - 1):
                ed.line([pts[i], pts[i+1]], fill=(20, 100, 255, 55), width=9)
                
    canvas.paste(ecliptic_layer, (0, 0), ecliptic_layer)
    
    # 4. Realistic Voyager 2 Neptune on Orbit
    nep_deg = 205
    n_rad = math.radians(nep_deg)
    nep_x = int(sun_x + 560 * math.cos(n_rad) * 1.05)
    nep_y = int(sun_y + 560 * math.sin(n_rad) * cam_tilt + (560 * math.sin(n_rad) * 0.18))
    
    nep_raw = Image.open("scratch/pluto_raw/neptune_full.jpg").convert("RGBA")
    nep_sphere = nep_raw.resize((64, 64), Image.Resampling.LANCZOS)
    nep_mask = Image.new("L", (64, 64), 0)
    ImageDraw.Draw(nep_mask).ellipse([2, 2, 62, 62], fill=255)
    
    for r in range(60, 15, -5):
        draw.ellipse([nep_x - r, nep_y - r, nep_x + r, nep_y + r], fill=(20, 110, 255, int(45 * (1 - r/60))))
    canvas.paste(nep_sphere, (nep_x - 32, nep_y - 32), nep_mask)
    
    # 5. Pluto's Inclined 17° Golden Orbit Ribbon
    pluto_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pld = ImageDraw.Draw(pluto_layer)
    
    a = 540
    b = 500
    e = 0.2488
    c = a * e
    tilt_rad = math.radians(28) # 17° tilt in 3D projection
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
        sy = sun_y + y_3d * cam_tilt + (y_3d * 0.18) - (z_3d * 0.82)
        
        pl_pts.append((sx, sy))
        pl_z.append(z_3d)
        
    for i in range(len(pl_pts) - 1):
        pt1, pt2 = pl_pts[i], pl_pts[i+1]
        z = pl_z[i]
        if z >= 0:
            alpha = int(min(255, 180 + z * 0.65))
            pld.line([pt1, pt2], fill=(255, 215, 90, alpha), width=4)
            pld.line([pt1, pt2], fill=(255, 180, 50, int(alpha * 0.45)), width=10)
        else:
            alpha = int(max(65, 160 + z * 0.8))
            pld.line([pt1, pt2], fill=(210, 140, 50, alpha), width=3)
            
    # Vertical drop indicators
    for idx in range(0, len(pl_pts), 8):
        pt = pl_pts[idx]
        z = pl_z[idx]
        if abs(z) > 25:
            plane_pt_y = pt[1] + (z * 0.82)
            pld.line([(pt[0], pt[1]), (pt[0], plane_pt_y)], fill=(255, 205, 110, 70), width=1)
            pld.ellipse([pt[0] - 2, plane_pt_y - 1, pt[0] + 2, plane_pt_y + 1], fill=(120, 170, 240, 100))
            
    canvas.paste(pluto_layer, (0, 0), pluto_layer)
    
    # 6. Hero Midground Celestial Juxtaposition: Earth's Moon vs Pluto
    # Real photographic bodies, cleanly cropped from authentic image centers!
    # Earth's Moon: 3474 km -> 260px wide at (x: 340, y: 1040)
    moon_raw = Image.open("scratch/pluto_raw/moon_full.jpg").convert("RGBA")
    # In moon_full.jpg, the moon is centered at (705, 712) with radius ~ 585px
    mw, mh = moon_raw.size
    mcx, mcy, mrad = mw // 2, mh // 2, int(min(mw, mh) * 0.42)
    moon_crop = moon_raw.crop((mcx - mrad, mcy - mrad, mcx + mrad, mcy + mrad))
    
    moon_size = 260
    moon_sphere = moon_crop.resize((moon_size, moon_size), Image.Resampling.LANCZOS)
    moon_mask = Image.new("L", (moon_size, moon_size), 0)
    ImageDraw.Draw(moon_mask).ellipse([3, 3, moon_size - 3, moon_size - 3], fill=255)
    moon_mask = moon_mask.filter(ImageFilter.GaussianBlur(1))
    
    # Soft lunar halo
    for gr in range(moon_size//2 + 30, moon_size//2, -3):
        draw.ellipse([340 - gr, 1040 - gr, 340 + gr, 1040 + gr], fill=(180, 205, 240, int(25 * (1 - (gr - moon_size//2)/30))))
    canvas.paste(moon_sphere, (340 - moon_size//2, 1040 - moon_size//2), moon_mask)
    
    # Pluto: 2376 km -> Accurately 2376/3474 * 260 = 178px wide at (x: 740, y: 1040)
    pluto_raw = Image.open("scratch/pluto_raw/pluto_color_8k.jpg").convert("RGBA")
    pw, ph = pluto_raw.size
    # In pluto_color_8k.jpg, Pluto is centered with black space around it
    # Pluto disk is roughly in center with radius ~ 2800px
    pcx, pcy, prad = pw // 2, ph // 2, int(min(pw, ph) * 0.38)
    pluto_crop = pluto_raw.crop((pcx - prad, pcy - prad, pcx + prad, pcy + prad))
    
    pluto_size = 178
    pluto_sphere = pluto_crop.resize((pluto_size, pluto_size), Image.Resampling.LANCZOS)
    pluto_mask = Image.new("L", (pluto_size, pluto_size), 0)
    ImageDraw.Draw(pluto_mask).ellipse([3, 3, pluto_size - 3, pluto_size - 3], fill=255)
    pluto_mask = pluto_mask.filter(ImageFilter.GaussianBlur(1))
    
    for gr in range(pluto_size//2 + 30, pluto_size//2, -3):
        draw.ellipse([740 - gr, 1040 - gr, 740 + gr, 1040 + gr], fill=(240, 180, 100, int(30 * (1 - (gr - pluto_size//2)/30))))
    canvas.paste(pluto_sphere, (740 - pluto_size//2, 1040 - pluto_size//2), pluto_mask)
    
    # 7. Safe Area Vignette & Polish
    final = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1340)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-03-strange-orbit.png")
    final.save(out_path, "PNG")
    print(f"Heroic Scene 03 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

def apply_safe_area_vignette(img, dark_start=1360):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(dark_start, H):
        factor = (y - dark_start) / (H - dark_start)
        alpha = int(210 * (factor ** 1.4))
        draw.line([(0, y), (W, y)], fill=(3, 5, 12, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def add_film_grain(img, intensity=6):
    arr = np.array(img).astype(np.float32)
    grain = np.random.normal(0, intensity, arr.shape)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

build_scene_03()
