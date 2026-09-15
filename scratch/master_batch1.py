import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUTPUT_DIR = "assets/pluto_demoted_reel"
W, H = 1080, 1920

def apply_safe_area_vignette(img, dark_start=1360):
    """Clean dark vignette for subtitle legibility while preserving background depth."""
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

# ==============================================================================
# SCENE 02: HEROIC 1930 DISCOVERY AT LOWELL OBSERVATORY
# ==============================================================================
def make_heroic_scene_02():
    print("--- Generating Heroic Scene 02: 1930 Discovery ---")
    base = Image.new("RGBA", (W, H), (10, 12, 18, 255))
    draw = ImageDraw.Draw(base)
    
    # 1. Background: Warm vintage Lowell Observatory dome interior
    for y in range(H):
        t = y / H
        ambient = math.exp(-((y - 750)/550)**2)
        r = int(12 + 10 * (1 - t) + 18 * ambient)
        g = int(10 + 8 * (1 - t) + 12 * ambient)
        b = int(16 + 14 * (1 - t) + 10 * ambient)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    # Vertical dark wood slats
    for x in range(0, W, 40):
        draw.line([(x, 0), (x, 1200)], fill=(6, 8, 12, 80), width=2)
        draw.line([(x+1, 0), (x+1, 1200)], fill=(28, 24, 18, 50), width=1)
        
    # Observatory dome arch at the very top (y: 0 - 280) with starry Arizona sky
    dome_arch = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    dad = ImageDraw.Draw(dome_arch)
    # Slit to night sky
    dad.polygon([(W//2 - 160, 0), (W//2 + 160, 0), (W//2 + 130, 240), (W//2 - 130, 240)], fill=(8, 14, 30, 240))
    # Stars in slit
    np.random.seed(1930)
    for _ in range(120):
        sx = np.random.randint(W//2 - 140, W//2 + 140)
        sy = np.random.randint(10, 220)
        b = np.random.randint(140, 255)
        dad.point((sx, sy), fill=(b, int(b*0.95), int(b*0.9), 230))
    # Curved arch frame
    dad.arc([W//2 - 180, -50, W//2 + 180, 280], start=0, end=180, fill=(35, 40, 55, 200), width=6)
    dome_arch = dome_arch.filter(ImageFilter.GaussianBlur(2))
    base.paste(dome_arch, (0, 0), dome_arch)
    
    # 2. Main Hero: The Zeiss Blink Comparator (lowell_blink_comparator.jpg)
    comp = Image.open("scratch/pluto_raw/lowell_blink_comparator.jpg").convert("RGBA")
    cw, ch = comp.size
    
    # Crop to focus on the magnificent machine without bottom museum cards
    # x: 20 to 1920, y: 20 to 1420
    crop_m = comp.crop((int(cw * 0.01), int(ch * 0.01), int(cw * 0.99), int(ch * 0.65)))
    
    # Scale to fill width 1080 heroically
    scale = (W * 1.08) / crop_m.width
    target_w = int(crop_m.width * scale)
    target_h = int(crop_m.height * scale)
    comp_res = crop_m.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Enhance color: warm amber glow on the circular light, deep cast iron blacks, rich brass
    cr, cg, cb, ca = comp_res.split()
    cr = cr.point(lambda p: min(255, int(p * 1.15)))
    cg = cg.point(lambda p: min(255, int(p * 1.02)))
    cb = cb.point(lambda p: min(255, int(p * 0.88)))
    comp_graded = Image.merge("RGBA", (cr, cg, cb, ca))
    
    # Soft vertical feathering
    m_mask = Image.new("L", comp_graded.size, 255)
    md = ImageDraw.Draw(m_mask)
    for y in range(80):
        md.line([(0, y), (target_w, y)], fill=int(255 * (y / 80.0)))
    for y in range(target_h - 120, target_h):
        md.line([(0, y), (target_w, y)], fill=int(255 * ((target_h - y) / 120.0)))
        
    paste_x = (W - target_w) // 2
    paste_y = 130
    base.paste(comp_graded, (paste_x, paste_y), m_mask)
    
    # 3. Authentic discovery starfield photographic plate inside the glowing aperture
    # Center of illuminated aperture ~ (330, 720)
    plates_raw = Image.open("scratch/pluto_raw/pluto_discovery_plates.png").convert("RGBA")
    pw, ph = plates_raw.size
    p_star = plates_raw.crop((int(pw * 0.08), int(ph * 0.12), int(pw * 0.42), int(ph * 0.88))).resize((280, 280))
    
    ap_mask = Image.new("L", (280, 280), 0)
    ImageDraw.Draw(ap_mask).ellipse([12, 12, 268, 268], fill=210)
    ap_mask = ap_mask.filter(ImageFilter.GaussianBlur(5))
    
    sr, sg, sb, sa = p_star.split()
    sr = sr.point(lambda p: min(255, int(p * 1.35)))
    sg = sg.point(lambda p: min(255, int(p * 1.10)))
    sb = sb.point(lambda p: min(255, int(p * 0.75)))
    p_star_warm = Image.merge("RGBA", (sr, sg, sb, sa))
    base.paste(p_star_warm, (330 - 140, 720 - 140), ap_mask)
    
    # Volumetric warm light halo
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for gr in range(360, 40, -18):
        alpha = int(50 * (1.0 - gr / 360.0) ** 1.6)
        gd.ellipse([330 - gr, 720 - gr, 330 + gr, 720 + gr], fill=(255, 195, 75, alpha))
    # Shaft of warm light directed onto the brass ocular eyepiece
    for bw in range(140, 10, -10):
        alpha = int(22 * (1.0 - bw / 140.0))
        gd.line([(330, 720), (810, 680)], fill=(255, 215, 120, alpha), width=bw)
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    base.paste(glow, (0, 0), glow)
    
    # 4. Foreground: Natural Solid Mahogany Observatory Desk (seamlessly supporting the machine)
    # y: 1020 to 1920
    desk = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(desk)
    for y in range(1020, H):
        t = (y - 1020) / (H - 1020)
        # Deep lustrous wood tones
        mr = int((52 + 14 * math.sin(y * 0.03)) * (1.0 - t * 0.92))
        mg = int((30 + 8 * math.sin(y * 0.03)) * (1.0 - t * 0.92))
        mb = int((18 + 5 * math.sin(y * 0.03)) * (1.0 - t * 0.92))
        dd.line([(0, y), (W, y)], fill=(mr, mg, mb, 255))
        
    # Soft warm lamp illumination on the mahogany table
    desk_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dgd = ImageDraw.Draw(desk_glow)
    for r in range(520, 40, -20):
        alpha = int(35 * (1.0 - r / 520.0) ** 1.4)
        dgd.ellipse([540 - r, int(1180 - r * 0.5), 540 + r, int(1180 + r * 0.5)], fill=(255, 185, 75, alpha))
    desk_glow = desk_glow.filter(ImageFilter.GaussianBlur(30))
    desk.paste(desk_glow, (0, 0), desk_glow)
    base.paste(desk, (0, 0), desk)
    
    # 5. Clean Safe Area Vignette & Polish
    final = apply_safe_area_vignette(base.convert("RGB"), dark_start=1340)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-02-discovery.png")
    final.save(out_path, "PNG")
    print(f"Heroic Scene 02 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

# ==============================================================================
# SCENE 03: HEROIC 3D SOLAR SYSTEM - 17° TILTED ORBIT & CELESTIAL SCALE
# ==============================================================================
def make_heroic_scene_03():
    print("--- Generating Heroic Scene 03: 17° Tilted Orbit & Scale ---")
    canvas = Image.new("RGBA", (W, H), (3, 5, 12, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Cosmic Deep Space Background with Nebular Dust & Milky Way
    for y in range(H):
        t = y / H
        ambient = math.exp(-((y - 700)/450)**2)
        r = int(3 + 5 * (1 - t) + 10 * ambient)
        g = int(5 + 8 * (1 - t) + 14 * ambient)
        b = int(14 + 18 * (1 - t) + 28 * ambient)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(1717)
    for _ in range(1100):
        sx = np.random.randint(0, W)
        sy = np.random.randint(0, 1500)
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
    for _ in range(130):
        nx = np.random.normal(W * 0.5, 290)
        ny = np.random.normal(700, 340)
        nr = np.random.randint(80, 260)
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(14, 26, 65, 14))
    nebula = nebula.filter(ImageFilter.GaussianBlur(38))
    canvas.paste(nebula, (0, 0), nebula)
    
    # 2. Distant Sun: Glorious source of directional light at (W // 2, 340)
    sun_x, sun_y = W // 2, 340
    sun_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sun_glow)
    for gr in range(380, 10, -10):
        alpha = int(80 * (1.0 - gr / 380.0) ** 1.8)
        sgd.ellipse([sun_x - gr, sun_y - gr, sun_x + gr, sun_y + gr], fill=(255, 225, 140, alpha))
    for deg in range(0, 360, 10):
        rad = math.radians(deg)
        rlen = np.random.randint(240, 460)
        ex = sun_x + rlen * math.cos(rad)
        ey = sun_y + rlen * math.sin(rad) * 0.65
        sgd.line([(sun_x, sun_y), (ex, ey)], fill=(255, 240, 180, 16), width=3)
    sun_glow = sun_glow.filter(ImageFilter.GaussianBlur(12))
    canvas.paste(sun_glow, (0, 0), sun_glow)
    draw.ellipse([sun_x - 16, sun_y - 16, sun_x + 16, sun_y + 16], fill=(255, 255, 255, 255))
    draw.ellipse([sun_x - 26, sun_y - 26, sun_x + 26, sun_y + 26], fill=(255, 245, 200, 170))
    
    # 3. 3D Solar System Ecliptic Orbits (Concentric planetary tracks)
    cam_tilt = 0.36
    planet_orbits = [
        {"r": 130, "name": "Jupiter", "col": (180, 150, 110, 70), "w": 1},
        {"r": 210, "name": "Saturn",  "col": (200, 170, 120, 90), "w": 2},
        {"r": 300, "name": "Uranus",  "col": (90, 190, 220, 110), "w": 2},
        {"r": 410, "name": "Neptune", "col": (30, 140, 255, 240), "w": 3, "glow": True}
    ]
    
    ecliptic_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ecliptic_layer)
    for deg in range(0, 360, 20):
        rad = math.radians(deg)
        rx = sun_x + 470 * math.cos(rad)
        ry = sun_y + 470 * math.sin(rad) * cam_tilt + (470 * math.sin(rad) * 0.15)
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
    
    # 4. Realistic Neptune on Orbit (NASA Voyager 2)
    nep_deg = 210
    n_rad = math.radians(nep_deg)
    nep_x = int(sun_x + 410 * math.cos(n_rad))
    nep_y = int(sun_y + 410 * math.sin(n_rad) * cam_tilt + (410 * math.sin(n_rad) * 0.15))
    
    nep_raw = Image.open("scratch/pluto_raw/neptune_full.jpg").convert("RGBA")
    nep_sphere = nep_raw.resize((50, 50), Image.Resampling.LANCZOS)
    nep_mask = Image.new("L", (50, 50), 0)
    ImageDraw.Draw(nep_mask).ellipse([2, 2, 48, 48], fill=255)
    
    for r in range(48, 10, -4):
        draw.ellipse([nep_x - r, nep_y - r, nep_x + r, nep_y + r], fill=(20, 110, 255, int(45 * (1 - r/48))))
    canvas.paste(nep_sphere, (nep_x - 25, nep_y - 25), nep_mask)
    
    # 5. Pluto's Inclined 17° Golden Orbit
    pluto_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pld = ImageDraw.Draw(pluto_layer)
    
    a = 410
    b = 380
    e = 0.2488
    c = a * e
    tilt_rad = math.radians(28)
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
    
    # 6. Hero Midground: SEAMLESS CELESTIAL COMPARISON (Earth's Moon vs Pluto)
    # y: 880 to 1260
    # Clean, beautiful photographic bodies without any black borders!
    celestial_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cld = ImageDraw.Draw(celestial_layer)
    
    # Subtle space dust glow behind the comparative bodies
    for gr in range(400, 40, -20):
        alpha = int(22 * (1.0 - gr / 400.0) ** 1.5)
        cld.ellipse([W//2 - gr, 1050 - int(gr * 0.45), W//2 + gr, 1050 + int(gr * 0.45)], fill=(25, 45, 95, alpha))
        
    # Earth's Moon: Diameter 3,474 km -> Size 320x320 at (x: 320, y: 1040)
    moon_raw = Image.open("scratch/pluto_raw/moon_full.jpg").convert("RGBA")
    moon_size = 320
    moon_sphere = moon_raw.resize((moon_size, moon_size), Image.Resampling.LANCZOS)
    
    # Soft feathered circular mask for seamless edge blending (no black borders!)
    m_mask = Image.new("L", (moon_size, moon_size), 0)
    ImageDraw.Draw(m_mask).ellipse([2, 2, moon_size - 2, moon_size - 2], fill=255)
    m_mask = m_mask.filter(ImageFilter.GaussianBlur(1))
    
    # Natural lunar atmospheric halo
    for gr in range(moon_size//2 + 25, moon_size//2, -3):
        cld.ellipse([320 - gr, 1040 - gr, 320 + gr, 1040 + gr], fill=(180, 205, 240, int(22 * (1 - (gr - moon_size//2)/25))))
    celestial_layer.paste(moon_sphere, (320 - moon_size//2, 1040 - moon_size//2), m_mask)
    
    # Pluto: Diameter 2,376 km -> Accurately 2376/3474 * 320 = 219px! at (x: 750, y: 1040)
    pluto_raw = Image.open("scratch/pluto_raw/pluto_color_8k.jpg").convert("RGBA")
    pluto_size = 219
    pluto_sphere = pluto_raw.resize((pluto_size, pluto_size), Image.Resampling.LANCZOS)
    
    # Clean feathered circular mask
    p_mask = Image.new("L", (pluto_size, pluto_size), 0)
    ImageDraw.Draw(p_mask).ellipse([2, 2, pluto_size - 2, pluto_size - 2], fill=255)
    p_mask = p_mask.filter(ImageFilter.GaussianBlur(1))
    
    # Warm golden/hazy halo around Pluto
    for gr in range(pluto_size//2 + 25, pluto_size//2, -3):
        cld.ellipse([750 - gr, 1040 - gr, 750 + gr, 1040 + gr], fill=(240, 180, 100, int(28 * (1 - (gr - pluto_size//2)/25))))
    celestial_layer.paste(pluto_sphere, (750 - pluto_size//2, 1040 - pluto_size//2), p_mask)
    
    canvas.paste(celestial_layer, (0, 0), celestial_layer)
    
    # 7. Safe Area Vignette & Polish
    final = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1340)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-03-strange-orbit.png")
    final.save(out_path, "PNG")
    print(f"Heroic Scene 03 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    make_heroic_scene_02()
    make_heroic_scene_03()
    print("Heroic Scenes 02 and 03 built successfully!")
