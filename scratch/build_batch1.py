"""
build_batch1.py - Compositing and generating Scenes 02, 03, and 04 for Pluto Demoted Reel.
Format: 1080x1920 portrait PNG (9:16).
Cinematic documentary standard matching Parker / Artemis II baseline.
Zero text, zero watermarks, dark subtitle safe area (y: 1380-1920).
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUTPUT_DIR = "assets/pluto_demoted_reel"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1080, 1920

def apply_safe_area_vignette(img, dark_start=1350):
    """Ensure lower subtitle safe area (y: 1380-1920) has dark cinematic background for subtitle contrast."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(dark_start, H):
        factor = (y - dark_start) / (H - dark_start)
        alpha = int(225 * (factor ** 1.3))
        draw.line([(0, y), (W, y)], fill=(2, 4, 10, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def add_film_grain(img, intensity=10):
    """Add subtle photographic film grain to eliminate digital banding."""
    arr = np.array(img).astype(np.float32)
    grain = np.random.normal(0, intensity, arr.shape)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def make_scene_02():
    print("--- Generating Scene 02: The Discovery (1930) Clyde Tombaugh & Blink Comparator ---")
    canvas = Image.new("RGBA", (W, H), (6, 8, 14, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Background: Observatory dome and slit with starry night sky (y: 0 - 750)
    for y in range(0, 750):
        t = y / 750.0
        r = int(4 + t * 6)
        g = int(7 + t * 8)
        b = int(18 + t * 12)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(1930)
    for _ in range(350):
        sx = np.random.randint(40, W - 40)
        sy = np.random.randint(20, 680)
        s_bright = np.random.randint(120, 255)
        s_size = np.random.choice([1, 1, 1, 2, 2, 3], p=[0.6, 0.2, 0.1, 0.05, 0.03, 0.02])
        col = (s_bright, int(s_bright * 0.95), int(s_bright * 0.9), 230)
        if s_size == 1:
            draw.point((sx, sy), fill=col)
        else:
            draw.ellipse([sx - s_size, sy - s_size, sx + s_size, sy + s_size], fill=col)
            
    dust = Image.new("RGBA", (W, 750), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(dust)
    for _ in range(120):
        dx = np.random.normal(W * 0.45, 180)
        dy = np.random.normal(300, 150)
        dr = np.random.randint(40, 120)
        d_draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=(30, 45, 75, 14))
    dust = dust.filter(ImageFilter.GaussianBlur(30))
    canvas.paste(dust, (0, 0), dust)
    
    dome_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dome_draw = ImageDraw.Draw(dome_overlay)
    dome_draw.polygon([(0, 0), (220, 0), (280, 700), (0, 750)], fill=(12, 14, 20, 245))
    dome_draw.polygon([(W - 220, 0), (W, 0), (W, 750), (W - 280, 700)], fill=(12, 14, 20, 245))
    for arch_y in [100, 260, 440, 620]:
        dome_draw.line([(0, arch_y), (W, arch_y + 30)], fill=(25, 28, 38, 180), width=8)
        dome_draw.line([(0, arch_y + 8), (W, arch_y + 38)], fill=(10, 12, 16, 200), width=4)
    dome_overlay = dome_overlay.filter(ImageFilter.GaussianBlur(3))
    canvas.paste(dome_overlay, (0, 0), dome_overlay)
    
    # 2. Midground: The Zeiss Blink Comparator machine
    zeiss_raw = Image.open("scratch/pluto_raw/zeiss_comparator_1930.jpg").convert("RGBA")
    zw, zh = zeiss_raw.size
    comp_crop = zeiss_raw.crop((int(zw * 0.08), int(zh * 0.05), int(zw * 0.92), int(zh * 0.95)))
    
    target_cw = int(W * 1.05)
    target_ch = int(comp_crop.height * (target_cw / comp_crop.width))
    comp_resized = comp_crop.resize((target_cw, target_ch), Image.Resampling.LANCZOS)
    
    r, g, b, a = comp_resized.split()
    r = r.point(lambda p: min(255, int(p * 1.08)))
    g = g.point(lambda p: min(255, int(p * 0.98)))
    b = b.point(lambda p: min(255, int(p * 0.88)))
    comp_graded = Image.merge("RGBA", (r, g, b, a))
    
    mask = Image.new("L", comp_graded.size, 255)
    m_draw = ImageDraw.Draw(mask)
    for y in range(80):
        val = int(255 * (y / 80.0))
        m_draw.line([(0, y), (target_cw, y)], fill=val)
    for y in range(target_ch - 120, target_ch):
        val = int(255 * ((target_ch - y) / 120.0))
        m_draw.line([(0, y), (target_cw, y)], fill=val)
    for x in range(60):
        val = int(255 * (x / 60.0))
        m_draw.line([(x, 0), (x, target_ch)], fill=val)
        m_draw.line([(target_cw - 1 - x, 0), (target_cw - 1 - x, target_ch)], fill=val)
    
    paste_x = (W - target_cw) // 2
    paste_y = 540
    canvas.paste(comp_graded, (paste_x, paste_y), mask)
    
    # 3. Add illuminated photographic glass plate details
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    for gr in range(160, 20, -10):
        alpha = int(45 * (1.0 - gr / 160.0))
        g_draw.ellipse([280 - gr, 840 - gr, 280 + gr, 840 + gr], fill=(255, 200, 100, alpha))
        g_draw.ellipse([800 - gr, 840 - gr, 800 + gr, 840 + gr], fill=(255, 200, 100, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(15))
    canvas.paste(glow, (0, 0), glow)
    
    # 4. Integrate Clyde Tombaugh in silhouette/profile operating the comparator
    clyde_crop = Image.open("scratch/clyde_operating_crop.jpg").convert("RGBA")
    c_gray = clyde_crop.convert("L")
    c_arr = np.array(c_gray).astype(np.float32)
    c_r = np.clip(c_arr * 1.1 + 15, 0, 255).astype(np.uint8)
    c_g = np.clip(c_arr * 0.95 + 10, 0, 255).astype(np.uint8)
    c_b = np.clip(c_arr * 0.75 + 5, 0, 255).astype(np.uint8)
    clyde_color = Image.fromarray(np.stack([c_r, c_g, c_b], axis=-1)).convert("RGBA")
    
    cw_orig, ch_orig = clyde_color.size
    clyde_person = clyde_color.crop((int(cw_orig * 0.05), int(ch_orig * 0.25), int(cw_orig * 0.45), int(ch_orig * 0.95)))
    scale_clyde = 2.2
    clyde_sized = clyde_person.resize((int(clyde_person.width * scale_clyde), int(clyde_person.height * scale_clyde)), Image.Resampling.LANCZOS)
    
    cm = Image.new("L", clyde_sized.size, 0)
    cm_draw = ImageDraw.Draw(cm)
    cm_draw.ellipse([20, 20, clyde_sized.width - 20, clyde_sized.height - 20], fill=230)
    cm = cm.filter(ImageFilter.GaussianBlur(15))
    canvas.paste(clyde_sized, (40, 780), cm)
    
    # 5. Foreground: Solid dark mahogany observatory workbench, warm tungsten lamp glow
    desk = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(desk)
    for y in range(1250, H):
        factor = (y - 1250) / (H - 1250)
        wood_r = int((28 + 15 * math.sin(y * 0.08)) * (1.0 - factor * 0.8))
        wood_g = int((16 + 8 * math.sin(y * 0.08)) * (1.0 - factor * 0.8))
        wood_b = int((10 + 4 * math.sin(y * 0.08)) * (1.0 - factor * 0.8))
        d_draw.line([(0, y), (W, y)], fill=(wood_r, wood_g, wood_b, 255))
        
    d_draw.line([(0, 1252), (W, 1252)], fill=(140, 105, 45, 160), width=3)
    d_draw.line([(0, 1255), (W, 1255)], fill=(60, 45, 20, 200), width=2)
    
    lamp_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lg_draw = ImageDraw.Draw(lamp_glow)
    for r in range(450, 40, -15):
        alpha = int(35 * (1.0 - r / 450.0))
        lg_draw.ellipse([120 - r, int(1340 - r * 0.6), 120 + r, int(1340 + r * 0.6)], fill=(255, 180, 70, alpha))
    lamp_glow = lamp_glow.filter(ImageFilter.GaussianBlur(35))
    desk.paste(lamp_glow, (0, 0), lamp_glow)
    canvas.paste(desk, (0, 0), desk)
    
    # 6. Apply safe area vignette (y: 1380 - 1920)
    final_s2 = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1320)
    final_s2 = ImageEnhance.Contrast(final_s2).enhance(1.12)
    final_s2 = ImageEnhance.Color(final_s2).enhance(1.08)
    final_s2 = add_film_grain(final_s2, intensity=9)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-02-discovery.png")
    final_s2.save(out_path, "PNG")
    print(f"Scene 02 saved to {out_path} ({os.path.getsize(out_path):,} bytes)")

def make_scene_03():
    print("--- Generating Scene 03: The Strange Anomaly (3D Solar System & Tilted 17° Orbit) ---")
    canvas = Image.new("RGBA", (W, H), (3, 5, 12, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Cosmic Background
    for y in range(H):
        t = y / H
        r = int(2 + 4 * (1.0 - t))
        g = int(4 + 6 * (1.0 - t))
        b = int(10 + 15 * (1.0 - t))
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(2006)
    for _ in range(700):
        sx = np.random.randint(0, W)
        sy = np.random.randint(0, 1400)
        bright = np.random.randint(90, 255)
        tint = np.random.choice(["blue", "gold", "white"], p=[0.3, 0.2, 0.5])
        if tint == "blue":
            col = (int(bright * 0.85), int(bright * 0.95), bright, 230)
        elif tint == "gold":
            col = (bright, int(bright * 0.9), int(bright * 0.7), 230)
        else:
            col = (bright, bright, bright, 240)
            
        size = np.random.choice([1, 1, 1, 1, 2, 2, 3], p=[0.7, 0.15, 0.05, 0.05, 0.03, 0.015, 0.005])
        if size == 1:
            draw.point((sx, sy), fill=col)
        else:
            draw.ellipse([sx - size, sy - size, sx + size, sy + size], fill=col)
            
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    n_draw = ImageDraw.Draw(nebula)
    for _ in range(80):
        nx = np.random.normal(W * 0.5, 300)
        ny = np.random.normal(600, 350)
        nr = np.random.randint(80, 260)
        n_draw.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(15, 28, 65, 12))
    nebula = nebula.filter(ImageFilter.GaussianBlur(40))
    canvas.paste(nebula, (0, 0), nebula)
    
    # 2. Distant Sun at (W//2, 420)
    sun_x, sun_y = W // 2, 420
    sun_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sg_draw = ImageDraw.Draw(sun_glow)
    
    for gr in range(300, 10, -10):
        alpha = int(70 * (1.0 - gr / 300.0) ** 1.8)
        sg_draw.ellipse([sun_x - gr, sun_y - gr, sun_x + gr, sun_y + gr], fill=(255, 220, 140, alpha))
    for angle_deg in range(0, 360, 15):
        rad = math.radians(angle_deg)
        ray_len = np.random.randint(180, 380)
        ex = sun_x + ray_len * math.cos(rad)
        ey = sun_y + ray_len * math.sin(rad) * 0.7
        sg_draw.line([(sun_x, sun_y), (ex, ey)], fill=(255, 240, 180, 16), width=3)
    sun_glow = sun_glow.filter(ImageFilter.GaussianBlur(8))
    canvas.paste(sun_glow, (0, 0), sun_glow)
    
    draw.ellipse([sun_x - 14, sun_y - 14, sun_x + 14, sun_y + 14], fill=(255, 255, 255, 255))
    draw.ellipse([sun_x - 22, sun_y - 22, sun_x + 22, sun_y + 22], fill=(255, 245, 210, 180))
    
    # 3. 3D Solar System Orbits
    aspect_ratio_ecliptic = 0.34
    planets_data = [
        {"name": "Jupiter", "radius": 130, "color": (180, 160, 130, 90), "width": 1},
        {"name": "Saturn",  "radius": 210, "color": (210, 190, 140, 110), "width": 2},
        {"name": "Uranus",  "radius": 310, "color": (100, 200, 220, 130), "width": 2},
        {"name": "Neptune", "radius": 420, "color": (40, 140, 255, 220), "width": 3, "has_planet": True}
    ]
    
    orbits_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o_draw = ImageDraw.Draw(orbits_layer)
    
    for angle_deg in range(0, 360, 30):
        rad = math.radians(angle_deg)
        rx = sun_x + 460 * math.cos(rad)
        ry = sun_y + 460 * math.sin(rad) * aspect_ratio_ecliptic + (460 * math.sin(rad) * 0.15)
        o_draw.line([(sun_x, sun_y), (rx, ry)], fill=(40, 70, 110, 35), width=1)
        
    for p in planets_data:
        r = p["radius"]
        w = p["width"]
        col = p["color"]
        pts = []
        for deg in range(0, 361, 2):
            rad = math.radians(deg)
            px = sun_x + r * math.cos(rad)
            py = sun_y + r * math.sin(rad) * aspect_ratio_ecliptic + (r * math.sin(rad) * 0.22)
            pts.append((px, py))
            
        for i in range(len(pts) - 1):
            o_draw.line([pts[i], pts[i+1]], fill=col, width=w)
            
        if p.get("has_planet"):
            nep_deg = 215
            n_rad = math.radians(nep_deg)
            nep_x = sun_x + r * math.cos(n_rad)
            nep_y = sun_y + r * math.sin(n_rad) * aspect_ratio_ecliptic + (r * math.sin(n_rad) * 0.22)
            for ng in range(25, 4, -4):
                o_draw.ellipse([nep_x - ng, nep_y - ng, nep_x + ng, nep_y + ng], fill=(30, 120, 255, int(40 * (1 - ng/25))))
            o_draw.ellipse([nep_x - 7, nep_y - 7, nep_x + 7, nep_y + 7], fill=(80, 170, 255, 255))
            o_draw.ellipse([nep_x - 3, nep_y - 3, nep_x + 3, nep_y + 3], fill=(210, 240, 255, 255))
            
    canvas.paste(orbits_layer, (0, 0), orbits_layer)
    
    # 4. Pluto's Inclined (17°) Orbit
    pluto_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pl_draw = ImageDraw.Draw(pluto_layer)
    
    a = 410
    b = 385
    e = 0.25
    c = a * e
    tilt_angle = math.radians(24)
    argument_perihelion = math.radians(-35)
    
    pluto_pts = []
    pluto_z = []
    
    for deg in range(0, 361, 2):
        rad = math.radians(deg)
        x_orb = a * math.cos(rad) - c
        y_orb = b * math.sin(rad)
        
        x_rot = x_orb * math.cos(argument_perihelion) - y_orb * math.sin(argument_perihelion)
        y_rot = x_orb * math.sin(argument_perihelion) + y_orb * math.cos(argument_perihelion)
        
        x_tilted = x_rot
        y_tilted = y_rot * math.cos(tilt_angle)
        z_tilted = y_rot * math.sin(tilt_angle)
        
        screen_x = sun_x + x_tilted * 1.15
        screen_y = sun_y + y_tilted * aspect_ratio_ecliptic + (y_tilted * 0.22) - (z_tilted * 0.65)
        
        pluto_pts.append((screen_x, screen_y))
        pluto_z.append(z_tilted)
        
    for i in range(len(pluto_pts) - 1):
        p1, p2 = pluto_pts[i], pluto_pts[i+1]
        z = pluto_z[i]
        if z >= 0:
            alpha = int(min(255, 180 + z * 0.5))
            gold_col = (255, 215, 100, alpha)
            pl_draw.line([p1, p2], fill=gold_col, width=4)
            pl_draw.line([p1, p2], fill=(255, 190, 60, int(alpha * 0.4)), width=8)
        else:
            alpha = int(max(70, 180 + z * 0.7))
            pl_draw.line([p1, p2], fill=(220, 150, 60, alpha), width=3)
            
    for idx in range(0, len(pluto_pts), 15):
        pt = pluto_pts[idx]
        z = pluto_z[idx]
        if abs(z) > 40:
            plane_y = pt[1] + (z * 0.65)
            pl_draw.line([(pt[0], pt[1]), (pt[0], plane_y)], fill=(255, 215, 120, 75), width=1)
            pl_draw.ellipse([pt[0] - 2, plane_y - 1, pt[0] + 2, plane_y + 1], fill=(120, 160, 220, 100))
            
    pluto_idx = 100
    pluto_pos = pluto_pts[pluto_idx]
    
    for pgr in range(35, 6, -3):
        pl_draw.ellipse([pluto_pos[0] - pgr, pluto_pos[1] - pgr, pluto_pos[0] + pgr, pluto_pos[1] + pgr],
                        fill=(255, 180, 80, int(50 * (1 - pgr/35))))
    pl_draw.ellipse([pluto_pos[0] - 12, pluto_pos[1] - 12, pluto_pos[0] + 12, pluto_pos[1] + 12],
                    fill=(210, 175, 140, 255))
    pl_draw.ellipse([pluto_pos[0] - 6, pluto_pos[1] - 4, pluto_pos[0] + 4, pluto_pos[1] + 6],
                    fill=(245, 235, 220, 255))
    pl_draw.arc([pluto_pos[0] - 12, pluto_pos[1] - 12, pluto_pos[0] + 12, pluto_pos[1] + 12],
                start=180, end=330, fill=(255, 250, 230, 255), width=3)
                
    charon_x = pluto_pos[0] + 28
    charon_y = pluto_pos[1] - 16
    pl_draw.ellipse([charon_x - 4, charon_y - 4, charon_x + 4, charon_y + 4], fill=(180, 180, 190, 255))
    canvas.paste(pluto_layer, (0, 0), pluto_layer)
    
    # 5. Moon vs Pluto Scale Comparison Vignette (y: 1100-1280)
    comp_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(comp_layer)
    
    moon_cx, moon_cy = 380, 1200
    moon_r = 72
    for r in range(moon_r, 0, -1):
        ratio = r / moon_r
        val = int(140 + 70 * (1 - ratio ** 0.5))
        c_draw.ellipse([moon_cx - r, moon_cy - r, moon_cx + r, moon_cy + r], fill=(val, val, int(val * 1.05), 240))
    c_draw.arc([moon_cx - moon_r, moon_cy - moon_r, moon_cx + moon_r, moon_cy + moon_r],
               start=190, end=350, fill=(240, 245, 255, 220), width=2)
               
    pluto_cx, pluto_cy = 680, 1215
    p_r = int(moon_r * (1188 / 1737))
    for r in range(p_r, 0, -1):
        ratio = r / p_r
        val_r = int(170 + 60 * (1 - ratio ** 0.5))
        val_g = int(140 + 50 * (1 - ratio ** 0.5))
        val_b = int(115 + 40 * (1 - ratio ** 0.5))
        c_draw.ellipse([pluto_cx - r, pluto_cy - r, pluto_cx + r, pluto_cy + r], fill=(val_r, val_g, val_b, 240))
    c_draw.ellipse([pluto_cx - 15, pluto_cy - 8, pluto_cx + 10, pluto_cy + 14], fill=(230, 220, 210, 220))
    c_draw.arc([pluto_cx - p_r, pluto_cy - p_r, pluto_cx + p_r, pluto_cy + p_r],
               start=190, end=350, fill=(255, 235, 200, 220), width=2)
               
    comp_layer = comp_layer.filter(ImageFilter.GaussianBlur(1))
    canvas.paste(comp_layer, (0, 0), comp_layer)
    
    # 6. Dark vignette for Subtitle Safe Area (y: 1380 - 1920)
    final_s3 = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1330)
    final_s3 = ImageEnhance.Contrast(final_s3).enhance(1.10)
    final_s3 = add_film_grain(final_s3, intensity=8)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-03-strange-orbit.png")
    final_s3.save(out_path, "PNG")
    print(f"Scene 03 saved to {out_path} ({os.path.getsize(out_path):,} bytes)")

def make_scene_04():
    print("--- Generating Scene 04: The Tipping Point (2005) Eris & Kuiper Belt ---")
    canvas = Image.new("RGBA", (W, H), (2, 3, 8, 255))
    
    # 1. Load authentic ESO artist impression of Eris & Dysnomia (4500x3000)
    eris_raw = Image.open("scratch/pluto_raw/real_eris_artist.jpg").convert("RGBA")
    ew, eh = eris_raw.size
    
    crop_size = int(eh * 0.95)
    crop_x1 = int((ew - crop_size) * 0.48)
    crop_y1 = int((eh - crop_size) * 0.5)
    eris_crop = eris_raw.crop((crop_x1, crop_y1, crop_x1 + crop_size, crop_y1 + crop_size))
    
    target_w = W
    target_h = int(crop_size * (target_w / crop_size))
    eris_resized = eris_crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    r, g, b, a = eris_resized.split()
    r = r.point(lambda p: min(255, int(p * 0.95)))
    g = g.point(lambda p: min(255, int(p * 1.02)))
    b = b.point(lambda p: min(255, int(p * 1.12)))
    eris_graded = Image.merge("RGBA", (r, g, b, a))
    
    feather_mask = Image.new("L", eris_graded.size, 255)
    fm_draw = ImageDraw.Draw(feather_mask)
    for y in range(120):
        val = int(255 * (y / 120.0))
        fm_draw.line([(0, y), (target_w, y)], fill=val)
    for y in range(target_h - 220, target_h):
        val = int(255 * ((target_h - y) / 220.0))
        fm_draw.line([(0, y), (target_w, y)], fill=val)
        
    canvas.paste(eris_graded, (0, 320), feather_mask)
    
    # 2. Add distant pin-prick needle Sun at 96 AU in top-left
    sun_x, sun_y = 190, 240
    sun_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sl_draw = ImageDraw.Draw(sun_layer)
    
    spike_len = 160
    for l in range(spike_len, 0, -5):
        alpha = int(140 * (1 - l / spike_len))
        sl_draw.line([(sun_x - l, sun_y), (sun_x + l, sun_y)], fill=(240, 248, 255, alpha), width=1)
        sl_draw.line([(sun_x, sun_y - l), (sun_x, sun_y + l)], fill=(240, 248, 255, alpha), width=1)
    for l in range(int(spike_len * 0.6), 0, -5):
        alpha = int(70 * (1 - l / (spike_len * 0.6)))
        sl_draw.line([(sun_x - l, sun_y - l), (sun_x + l, sun_y + l)], fill=(200, 230, 255, alpha), width=1)
        sl_draw.line([(sun_x - l, sun_y + l), (sun_x + l, sun_y - l)], fill=(200, 230, 255, alpha), width=1)
        
    for gr in range(60, 4, -4):
        sl_draw.ellipse([sun_x - gr, sun_y - gr, sun_x + gr, sun_y + gr], fill=(220, 240, 255, int(45 * (1 - gr/60))))
    sl_draw.ellipse([sun_x - 4, sun_y - 4, sun_x + 4, sun_y + 4], fill=(255, 255, 255, 255))
    sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(1))
    canvas.paste(sun_layer, (0, 0), sun_layer)
    
    # 3. Add Dysnomia (moon of Eris)
    dys_x, dys_y = 860, 520
    dys_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl_draw = ImageDraw.Draw(dys_layer)
    for dr in range(18, 2, -2):
        dl_draw.ellipse([dys_x - dr, dys_y - dr, dys_x + dr, dys_y + dr], fill=(180, 210, 240, int(35 * (1 - dr/18))))
    dl_draw.ellipse([dys_x - 6, dys_y - 6, dys_x + 6, dys_y + 6], fill=(200, 215, 230, 255))
    dl_draw.arc([dys_x - 6, dys_y - 6, dys_x + 6, dys_y + 6], start=160, end=310, fill=(255, 255, 255, 255), width=2)
    canvas.paste(dys_layer, (0, 0), dys_layer)
    
    # 4. Foreground: Floating Kuiper Belt frozen debris (y: 1180 - 1420)
    fg_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fg_draw = ImageDraw.Draw(fg_layer)
    
    debris_coords = [
        (160, 1260, 38, 28),
        (310, 1340, 22, 18),
        (820, 1280, 46, 34),
        (940, 1360, 26, 20),
        (620, 1380, 18, 14)
    ]
    for dx, dy, dw, dh in debris_coords:
        fg_draw.ellipse([dx - dw, dy - dh, dx + dw, dy + dh], fill=(18, 24, 36, 230))
        fg_draw.arc([dx - dw, dy - dh, dx + dw, dy + dh], start=150, end=290, fill=(190, 225, 255, 220), width=2)
        fg_draw.point((dx - int(dw * 0.5), dy - int(dh * 0.4)), fill=(255, 255, 255, 255))
        
    fg_layer = fg_layer.filter(ImageFilter.GaussianBlur(1))
    canvas.paste(fg_layer, (0, 0), fg_layer)
    
    # 5. Dark vignette for Subtitle Safe Area (y: 1380 - 1920)
    final_s4 = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1340)
    final_s4 = ImageEnhance.Contrast(final_s4).enhance(1.12)
    final_s4 = add_film_grain(final_s4, intensity=8)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-04-eris-kuiper-belt.png")
    final_s4.save(out_path, "PNG")
    print(f"Scene 04 saved to {out_path} ({os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    make_scene_02()
    make_scene_03()
    make_scene_04()
    print("Batch 1 completed successfully!")
