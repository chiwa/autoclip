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
        alpha = int(240 * (factor ** 1.3))
        draw.line([(0, y), (W, y)], fill=(2, 4, 10, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def add_film_grain(img, intensity=7):
    arr = np.array(img).astype(np.float32)
    grain = np.random.normal(0, intensity, arr.shape)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

# ==============================================================================
# SCENE 02: THE DISCOVERY (1930)
# Clyde Tombaugh's Blink Comparator & Journal at Lowell Observatory
# ==============================================================================
def make_scene_02():
    print("--- Building Scene 02: The Discovery (1930) ---")
    base = Image.new("RGBA", (W, H), (6, 8, 14, 255))
    draw = ImageDraw.Draw(base)
    
    # 1. Background: Observatory interior wall & slit to starlit sky (y: 0 - 450)
    for y in range(480):
        t = y / 480.0
        r = int(5 + 10 * (1 - t))
        g = int(7 + 12 * (1 - t))
        b = int(18 + 25 * (1 - t))
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(1930)
    for _ in range(350):
        sx = np.random.randint(120, W - 120)
        sy = np.random.randint(10, 420)
        bright = np.random.randint(120, 255)
        sz = np.random.choice([1, 1, 2, 2, 3], p=[0.75, 0.15, 0.06, 0.03, 0.01])
        draw.ellipse([sx-sz, sy-sz, sx+sz, sy+sz], fill=(bright, int(bright*0.95), int(bright*0.9), 240))
        
    # Subtle dome ribs
    arch = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(arch)
    ad.polygon([(0, 0), (140, 0), (100, 480), (0, 500)], fill=(12, 14, 20, 255))
    ad.polygon([(W - 140, 0), (W, 0), (W, 500), (W - 100, 480)], fill=(12, 14, 20, 255))
    for y in [120, 260, 400]:
        ad.line([(100, y), (W - 100, y)], fill=(40, 45, 60, 100), width=4)
    arch = arch.filter(ImageFilter.GaussianBlur(3))
    base.paste(arch, (0, 0), arch)
    
    # 2. Main Hero Subject: The Zeiss Blink Comparator (Lowell Observatory)
    comp = Image.open("scratch/pluto_raw/lowell_blink_comparator.jpg").convert("RGBA")
    cw, ch = comp.size
    # Crop machine from top down to just above museum table placards (crop out bottom 32%)
    crop_m = comp.crop((int(cw * 0.02), int(ch * 0.01), int(cw * 0.98), int(ch * 0.68)))
    
    # Scale to fill width 1080
    scale = W / crop_m.width
    target_h = int(crop_m.height * scale)
    crop_res = crop_m.resize((W, target_h), Image.Resampling.LANCZOS)
    
    # Rich vintage color grading: warm tungsten glow, deep cast iron blacks
    cr, cg, cb, ca = crop_res.split()
    cr = cr.point(lambda p: min(255, int(p * 1.15)))
    cg = cg.point(lambda p: min(255, int(p * 1.02)))
    cb = cb.point(lambda p: min(255, int(p * 0.88)))
    comp_graded = Image.merge("RGBA", (cr, cg, cb, ca))
    
    m_mask = Image.new("L", comp_graded.size, 255)
    md = ImageDraw.Draw(m_mask)
    for y in range(80):
        md.line([(0, y), (W, y)], fill=int(255 * (y / 80.0)))
    for y in range(target_h - 100, target_h):
        md.line([(0, y), (W, y)], fill=int(255 * ((target_h - y) / 100.0)))
        
    paste_y = 250
    base.paste(comp_graded, (0, paste_y), m_mask)
    
    # 3. Superimpose authentic discovery starfield negative into the illuminated aperture!
    # The glowing circle is at x: 330, y: 250 + 580 = 830, radius ~ 150px
    plates_raw = Image.open("scratch/pluto_raw/pluto_discovery_plates.png").convert("RGBA")
    pw, ph = plates_raw.size
    p_star = plates_raw.crop((int(pw * 0.08), int(ph * 0.12), int(pw * 0.42), int(ph * 0.88))).resize((280, 280))
    # Circular mask
    ap_mask = Image.new("L", (280, 280), 0)
    ImageDraw.Draw(ap_mask).ellipse([10, 10, 270, 270], fill=210)
    ap_mask = ap_mask.filter(ImageFilter.GaussianBlur(6))
    
    # Warm amber tint for the star plate
    sr, sg, sb, sa = p_star.split()
    sr = sr.point(lambda p: min(255, int(p * 1.35)))
    sg = sg.point(lambda p: min(255, int(p * 1.10)))
    sb = sb.point(lambda p: min(255, int(p * 0.75)))
    p_star_warm = Image.merge("RGBA", (sr, sg, sb, sa))
    base.paste(p_star_warm, (330 - 140, 830 - 140), ap_mask)
    
    # Amber volumetric light halo
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for gr in range(320, 40, -18):
        alpha = int(45 * (1.0 - gr / 320.0) ** 1.6)
        gd.ellipse([330 - gr, 830 - gr, 330 + gr, 830 + gr], fill=(255, 195, 75, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    base.paste(glow, (0, 0), glow)
    
    # 4. Foreground: Mahogany Workbench with Clyde's actual Observation Journal (y: 1100 to 1920)
    desk = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(desk)
    for y in range(1100, H):
        t = (y - 1100) / (H - 1100)
        mr = int((45 + 12 * math.sin(y * 0.04)) * (1.0 - t * 0.9))
        mg = int((26 + 8 * math.sin(y * 0.04)) * (1.0 - t * 0.9))
        mb = int((15 + 4 * math.sin(y * 0.04)) * (1.0 - t * 0.9))
        dd.line([(0, y), (W, y)], fill=(mr, mg, mb, 255))
        
    dd.line([(0, 1102), (W, 1102)], fill=(185, 145, 65, 220), width=3)
    dd.line([(0, 1105), (W, 1105)], fill=(75, 50, 20, 240), width=2)
    
    # Overlay Clyde's actual 1930 Observation Logbook on the desk (tilted, authentic)
    logbook_raw = Image.open("scratch/pluto_raw/clyde_records_1.jpg").convert("RGBA")
    lw, lh = logbook_raw.size
    # Crop the handwritten lines: "Object: δ Geminorum Date: 1930 Jan 23... Jan 29..."
    log_crop = logbook_raw.crop((int(lw * 0.08), int(lh * 0.15), int(lw * 0.85), int(lh * 0.85)))
    log_w = 780
    log_h = int(log_crop.height * (log_w / log_crop.width))
    log_res = log_crop.resize((log_w, log_h), Image.Resampling.LANCZOS)
    
    # Warm vintage tone for paper
    lr, lg, lb, la = log_res.split()
    lr = lr.point(lambda p: min(255, int(p * 1.05)))
    lg = lg.point(lambda p: min(255, int(p * 0.95)))
    lb = lb.point(lambda p: min(255, int(p * 0.80)))
    log_warm = Image.merge("RGBA", (lr, lg, lb, la))
    
    # Feathered edges for book
    log_mask = Image.new("L", log_warm.size, 230)
    lmd = ImageDraw.Draw(log_mask)
    for y in range(40):
        lmd.line([(0, y), (log_w, y)], fill=int(230 * (y / 40.0)))
    for y in range(log_h - 60, log_h):
        lmd.line([(0, y), (log_w, y)], fill=int(230 * ((log_h - y) / 60.0)))
    for x in range(40):
        lmd.line([(x, 0), (x, log_h)], fill=int(230 * (x / 40.0)))
        lmd.line([(log_w - 1 - x, 0), (log_w - 1 - x, log_h)], fill=int(230 * (x / 40.0)))
        
    # Rotate slightly (-4 deg) for natural desk angle
    log_rot = log_warm.rotate(-4, expand=True, resample=Image.Resampling.BICUBIC)
    mask_rot = log_mask.rotate(-4, expand=True, resample=Image.Resampling.BICUBIC)
    
    # Soft drop shadow under book
    shadow = Image.new("RGBA", log_rot.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle([10, 10, log_rot.width - 10, log_rot.height - 10], fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    
    desk.paste(shadow, (150, 1140), shadow)
    desk.paste(log_rot, (140, 1130), mask_rot)
    
    # Warm desk lamp lighting cone
    lamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lamp)
    for lr in range(500, 40, -20):
        alpha = int(35 * (1.0 - lr / 500.0) ** 1.4)
        ld.ellipse([540 - lr, int(1280 - lr * 0.5), 540 + lr, int(1280 + lr * 0.5)], fill=(255, 185, 75, alpha))
    lamp = lamp.filter(ImageFilter.GaussianBlur(25))
    desk.paste(lamp, (0, 0), lamp)
    base.paste(desk, (0, 0), desk)
    
    # 5. Safe Area Vignette & Final Touches
    final = apply_safe_area_vignette(base.convert("RGB"), dark_start=1330)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=7)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-02-discovery.png")
    final.save(out_path, "PNG")
    print(f"Scene 02 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

# ==============================================================================
# SCENE 03: THE STRANGE ANOMALY (3D Solar System & Photographic Scale)
# ==============================================================================
def make_scene_03():
    print("--- Building Scene 03: The Strange Anomaly ---")
    canvas = Image.new("RGBA", (W, H), (2, 4, 10, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Cosmic Background with Nebular Dust
    for y in range(H):
        t = y / H
        r = int(2 + 5 * (1 - t) + 8 * math.exp(-((y - 550)/380)**2))
        g = int(4 + 8 * (1 - t) + 12 * math.exp(-((y - 550)/380)**2))
        b = int(12 + 18 * (1 - t) + 25 * math.exp(-((y - 550)/380)**2))
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(1717)
    for _ in range(950):
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
            
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    for _ in range(110):
        nx = np.random.normal(W * 0.5, 280)
        ny = np.random.normal(600, 320)
        nr = np.random.randint(70, 240)
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(12, 24, 60, 14))
    nebula = nebula.filter(ImageFilter.GaussianBlur(35))
    canvas.paste(nebula, (0, 0), nebula)
    
    # 2. Distant Sun at (W // 2, 420)
    sun_x, sun_y = W // 2, 420
    sun_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sun_glow)
    for gr in range(320, 10, -10):
        alpha = int(75 * (1.0 - gr / 320.0) ** 1.8)
        sgd.ellipse([sun_x - gr, sun_y - gr, sun_x + gr, sun_y + gr], fill=(255, 225, 140, alpha))
    for deg in range(0, 360, 12):
        rad = math.radians(deg)
        rlen = np.random.randint(200, 380)
        ex = sun_x + rlen * math.cos(rad)
        ey = sun_y + rlen * math.sin(rad) * 0.65
        sgd.line([(sun_x, sun_y), (ex, ey)], fill=(255, 240, 180, 18), width=3)
    sun_glow = sun_glow.filter(ImageFilter.GaussianBlur(10))
    canvas.paste(sun_glow, (0, 0), sun_glow)
    draw.ellipse([sun_x - 15, sun_y - 15, sun_x + 15, sun_y + 15], fill=(255, 255, 255, 255))
    draw.ellipse([sun_x - 24, sun_y - 24, sun_x + 24, sun_y + 24], fill=(255, 245, 200, 170))
    
    # 3. 3D Solar System Perspective
    cam_tilt = 0.38
    planet_orbits = [
        {"r": 150, "name": "Jupiter", "col": (180, 150, 110, 80), "w": 1},
        {"r": 230, "name": "Saturn",  "col": (200, 170, 120, 100), "w": 2},
        {"r": 330, "name": "Uranus",  "col": (90, 190, 220, 120), "w": 2},
        {"r": 450, "name": "Neptune", "col": (30, 140, 255, 240), "w": 3, "glow": True}
    ]
    
    ecliptic_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ecliptic_layer)
    for deg in range(0, 360, 20):
        rad = math.radians(deg)
        rx = sun_x + 500 * math.cos(rad)
        ry = sun_y + 500 * math.sin(rad) * cam_tilt + (500 * math.sin(rad) * 0.16)
        ed.line([(sun_x, sun_y), (rx, ry)], fill=(35, 65, 110, 40), width=1)
        
    for p in planet_orbits:
        pr = p["r"]
        pw = p["w"]
        pcol = p["col"]
        pts = []
        for deg in range(0, 361, 2):
            rad = math.radians(deg)
            px = sun_x + pr * math.cos(rad)
            py = sun_y + pr * math.sin(rad) * cam_tilt + (pr * math.sin(rad) * 0.16)
            pts.append((px, py))
            
        for i in range(len(pts) - 1):
            ed.line([pts[i], pts[i+1]], fill=pcol, width=pw)
        if p.get("glow"):
            for i in range(len(pts) - 1):
                ed.line([pts[i], pts[i+1]], fill=(20, 100, 255, 50), width=8)
                
    canvas.paste(ecliptic_layer, (0, 0), ecliptic_layer)
    
    # 4. Realistic Voyager 2 Neptune Orb on its Orbit
    nep_deg = 205
    n_rad = math.radians(nep_deg)
    nep_x = int(sun_x + 450 * math.cos(n_rad))
    nep_y = int(sun_y + 450 * math.sin(n_rad) * cam_tilt + (450 * math.sin(n_rad) * 0.16))
    
    nep_raw = Image.open("scratch/pluto_raw/neptune_full.jpg").convert("RGBA")
    nep_sphere = nep_raw.resize((44, 44), Image.Resampling.LANCZOS)
    nep_mask = Image.new("L", (44, 44), 0)
    ImageDraw.Draw(nep_mask).ellipse([2, 2, 42, 42], fill=255)
    
    # Neptune glow
    for r in range(40, 10, -4):
        draw.ellipse([nep_x - r, nep_y - r, nep_x + r, nep_y + r], fill=(20, 110, 255, int(45 * (1 - r/40))))
    canvas.paste(nep_sphere, (nep_x - 22, nep_y - 22), nep_mask)
    
    # 5. Pluto's Inclined 17° Orbit
    pluto_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pld = ImageDraw.Draw(pluto_layer)
    
    a = 440
    b = 410
    e = 0.2488
    c = a * e
    tilt_rad = math.radians(26)
    arg_peri = math.radians(-30)
    
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
        
        sx = sun_x + x_3d * 1.12
        sy = sun_y + y_3d * cam_tilt + (y_3d * 0.16) - (z_3d * 0.72)
        
        pl_pts.append((sx, sy))
        pl_z.append(z_3d)
        
    for i in range(len(pl_pts) - 1):
        pt1, pt2 = pl_pts[i], pl_pts[i+1]
        z = pl_z[i]
        if z >= 0:
            alpha = int(min(255, 170 + z * 0.65))
            pld.line([pt1, pt2], fill=(255, 215, 90, alpha), width=4)
            pld.line([pt1, pt2], fill=(255, 180, 50, int(alpha * 0.45)), width=9)
        else:
            alpha = int(max(65, 160 + z * 0.8))
            pld.line([pt1, pt2], fill=(210, 140, 50, alpha), width=3)
            
    for idx in range(0, len(pl_pts), 12):
        pt = pl_pts[idx]
        z = pl_z[idx]
        if abs(z) > 35:
            plane_pt_y = pt[1] + (z * 0.72)
            pld.line([(pt[0], pt[1]), (pt[0], plane_pt_y)], fill=(255, 205, 110, 80), width=1)
            pld.ellipse([pt[0] - 2, plane_pt_y - 1, pt[0] + 2, plane_pt_y + 1], fill=(120, 170, 240, 120))
            
    # Small Pluto on orbit at aphelion
    p_idx = 105
    pluto_center = (int(pl_pts[p_idx][0]), int(pl_pts[p_idx][1]))
    
    # Miniature 8k Pluto orb on track
    pluto_raw = Image.open("scratch/pluto_raw/pluto_color_8k.jpg").convert("RGBA")
    p_mini = pluto_raw.resize((36, 36), Image.Resampling.LANCZOS)
    p_mini_mask = Image.new("L", (36, 36), 0)
    ImageDraw.Draw(p_mini_mask).ellipse([2, 2, 34, 34], fill=255)
    
    for r in range(35, 10, -4):
        pld.ellipse([pluto_center[0] - r, pluto_center[1] - r, pluto_center[0] + r, pluto_center[1] + r],
                    fill=(255, 190, 90, int(45 * (1 - r/35))))
    canvas.paste(pluto_layer, (0, 0), pluto_layer)
    canvas.paste(p_mini, (pluto_center[0] - 18, pluto_center[1] - 18), p_mini_mask)
    
    # 6. PHOTOGRAPHIC SCALE COMPARISON: MOON VS PLUTO (y: 980 to 1280)
    # Using authentic NASA Moon (Luc Viatour) and New Horizons Pluto (8k)!
    comp_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(comp_layer)
    
    # Atmospheric backdrop glow
    cd.ellipse([W//2 - 320, 960, W//2 + 320, 1280], fill=(15, 25, 55, 80))
    
    # Earth's Moon: Diameter 3,474 km -> Size 240x240 (at x: 330, y: 1120)
    moon_raw = Image.open("scratch/pluto_raw/moon_full.jpg").convert("RGBA")
    moon_size = 240
    moon_sphere = moon_raw.resize((moon_size, moon_size), Image.Resampling.LANCZOS)
    moon_mask = Image.new("L", (moon_size, moon_size), 0)
    ImageDraw.Draw(moon_mask).ellipse([4, 4, moon_size - 4, moon_size - 4], fill=255)
    moon_mask = moon_mask.filter(ImageFilter.GaussianBlur(1))
    
    # Directional sunlight shading on Moon (lit from top-left)
    moon_shaded = moon_sphere.copy()
    ms_draw = ImageDraw.Draw(moon_shaded)
    for r in range(moon_size//2, 0, -5):
        pass # The authentic photo already has real lunar maria & illumination!
        
    # Moon glow
    for gr in range(moon_size//2 + 25, moon_size//2, -3):
        cd.ellipse([330 - gr, 1120 - gr, 330 + gr, 1120 + gr], fill=(180, 200, 235, int(30 * (1 - (gr - moon_size//2)/25))))
    comp_layer.paste(moon_shaded, (330 - moon_size//2, 1120 - moon_size//2), moon_mask)
    
    # Pluto: Diameter 2,376 km -> Accurately 2376/3474 * 240 = 164px! (at x: 720, y: 1120)
    pluto_size = 164
    pluto_sphere = pluto_raw.resize((pluto_size, pluto_size), Image.Resampling.LANCZOS)
    pluto_mask = Image.new("L", (pluto_size, pluto_size), 0)
    ImageDraw.Draw(pluto_mask).ellipse([3, 3, pluto_size - 3, pluto_size - 3], fill=255)
    pluto_mask = pluto_mask.filter(ImageFilter.GaussianBlur(1))
    
    # Pluto golden glow
    for gr in range(pluto_size//2 + 25, pluto_size//2, -3):
        cd.ellipse([720 - gr, 1120 - gr, 720 + gr, 1120 + gr], fill=(240, 180, 100, int(35 * (1 - (gr - pluto_size//2)/25))))
    comp_layer.paste(pluto_sphere, (720 - pluto_size//2, 1120 - pluto_size//2), pluto_mask)
    
    canvas.paste(comp_layer, (0, 0), comp_layer)
    
    # 7. Safe Area Vignette (y: 1380 - 1920)
    final = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1330)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=7)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-03-strange-orbit.png")
    final.save(out_path, "PNG")
    print(f"Scene 03 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

# ==============================================================================
# SCENE 04: THE TIPPING POINT (2005) - ERIS IN KUIPER BELT
# ==============================================================================
def make_scene_04():
    print("--- Building Scene 04: The Tipping Point (2005) Eris ---")
    # Base: Clean 9:16 crop directly from ESO 4500x3000 master artwork!
    eris_raw = Image.open("scratch/pluto_raw/real_eris_artist.jpg").convert("RGB")
    ew, eh = eris_raw.size # 4500, 3000
    
    # Exact 9:16 vertical crop:
    # Height = 3000, Width = 3000 * 9 / 16 = 1687.5 -> 1688
    crop_h = eh
    crop_w = int(eh * 9 / 16) # 1687
    
    # Center x around Eris: Eris is roughly at x=2250.
    # Let's frame Eris slightly in upper-middle so the cold methane ice and horizon shine
    crop_x1 = int(ew * 0.28) # gives x from 1260 to 2947 (centers Eris at ~2100)
    crop_y1 = 0
    eris_crop = eris_raw.crop((crop_x1, crop_y1, crop_x1 + crop_w, crop_y1 + crop_h))
    
    # Resize losslessly to 1080x1920
    final_eris = eris_crop.resize((W, H), Image.Resampling.LANCZOS)
    
    # Color grade: Enhance outer solar system cold cyan highlights and deep space blacks
    er, eg, eb = final_eris.split()
    er = er.point(lambda p: min(255, int(p * 0.96)))
    eg = eg.point(lambda p: min(255, int(p * 1.02)))
    eb = eb.point(lambda p: min(255, int(p * 1.10)))
    final_graded = Image.merge("RGB", (er, eg, eb))
    
    # Distant pinpoint needle-sharp Sun at 96 AU in upper-left (x: 180, y: 220)
    sun_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sod = ImageDraw.Draw(sun_overlay)
    sx, sy = 180, 220
    
    # Cross diffraction spikes
    spike_l = 180
    for l in range(spike_l, 0, -4):
        alpha = int(160 * (1 - l / spike_l))
        sod.line([(sx - l, sy), (sx + l, sy)], fill=(240, 248, 255, alpha), width=1)
        sod.line([(sx, sy - l), (sx, sy + l)], fill=(240, 248, 255, alpha), width=1)
    for l in range(int(spike_l * 0.5), 0, -4):
        alpha = int(80 * (1 - l / (spike_l * 0.5)))
        sod.line([(sx - l, sy - l), (sx + l, sy + l)], fill=(210, 235, 255, alpha), width=1)
        sod.line([(sx - l, sy + l), (sx + l, sy - l)], fill=(210, 235, 255, alpha), width=1)
        
    for gr in range(45, 3, -3):
        sod.ellipse([sx - gr, sy - gr, sx + gr, sy + gr], fill=(225, 245, 255, int(45 * (1 - gr/45))))
    sod.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 255, 255, 255))
    sun_overlay = sun_overlay.filter(ImageFilter.GaussianBlur(1))
    
    final_comp = Image.alpha_composite(final_graded.convert("RGBA"), sun_overlay).convert("RGB")
    
    # Safe Area Vignette (y: 1380 - 1920)
    final = apply_safe_area_vignette(final_comp, dark_start=1340)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-04-eris-kuiper-belt.png")
    final.save(out_path, "PNG")
    print(f"Scene 04 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    make_scene_02()
    make_scene_03()
    make_scene_04()
    print("Batch 1 v2 completed successfully!")
