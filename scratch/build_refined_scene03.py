import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H = 1080, 1920

def create_scene_03():
    # 1. Base canvas: Deep outer solar system space
    canvas = Image.new("RGBA", (W, H), (2, 4, 10, 255))
    draw = ImageDraw.Draw(canvas)
    
    # Gradient sky with subtle nebular dust
    for y in range(H):
        t = y / H
        r = int(2 + 5 * (1 - t) + 8 * math.exp(-((y - 600)/400)**2))
        g = int(4 + 8 * (1 - t) + 12 * math.exp(-((y - 600)/400)**2))
        b = int(12 + 18 * (1 - t) + 25 * math.exp(-((y - 600)/400)**2))
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    # Multi-layered Starfield (Milky Way richness)
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
            
    # Volumetric Cosmic Nebulae
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    for _ in range(110):
        nx = np.random.normal(W * 0.5, 280)
        ny = np.random.normal(650, 320)
        nr = np.random.randint(70, 240)
        # Deep blue/indigo dust
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(12, 24, 60, 14))
    nebula = nebula.filter(ImageFilter.GaussianBlur(35))
    canvas.paste(nebula, (0, 0), nebula)
    
    # 2. Distant Sun: Glowing celestial light source at (W // 2, 480)
    sun_x, sun_y = W // 2, 480
    sun_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sun_glow)
    for gr in range(350, 10, -10):
        alpha = int(80 * (1.0 - gr / 350.0) ** 1.8)
        sgd.ellipse([sun_x - gr, sun_y - gr, sun_x + gr, sun_y + gr], fill=(255, 225, 140, alpha))
    for deg in range(0, 360, 12):
        rad = math.radians(deg)
        rlen = np.random.randint(220, 420)
        ex = sun_x + rlen * math.cos(rad)
        ey = sun_y + rlen * math.sin(rad) * 0.65
        sgd.line([(sun_x, sun_y), (ex, ey)], fill=(255, 240, 180, 18), width=3)
    sun_glow = sun_glow.filter(ImageFilter.GaussianBlur(10))
    canvas.paste(sun_glow, (0, 0), sun_glow)
    draw.ellipse([sun_x - 16, sun_y - 16, sun_x + 16, sun_y + 16], fill=(255, 255, 255, 255))
    draw.ellipse([sun_x - 26, sun_y - 26, sun_x + 26, sun_y + 26], fill=(255, 245, 200, 170))
    
    # 3. 3D Solar System:
    # We create a gorgeous perspective view across the outer solar system!
    # Camera: Elevation ~ 22°, looking across the ecliptic plane toward the distant Sun.
    cam_tilt = 0.38
    
    # Orbits of Jupiter, Saturn, Uranus, Neptune
    planet_orbits = [
        {"r": 160, "name": "Jupiter", "col": (180, 150, 110, 80), "w": 1},
        {"r": 250, "name": "Saturn",  "col": (200, 170, 120, 110), "w": 2},
        {"r": 360, "name": "Uranus",  "col": (90, 190, 220, 130), "w": 2},
        {"r": 480, "name": "Neptune", "col": (30, 140, 255, 240), "w": 4, "glow": True}
    ]
    
    ecliptic_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ecliptic_layer)
    
    # Glowing translucent plane disc / radial grid lines
    for deg in range(0, 360, 20):
        rad = math.radians(deg)
        rx = sun_x + 520 * math.cos(rad)
        ry = sun_y + 520 * math.sin(rad) * cam_tilt + (520 * math.sin(rad) * 0.16)
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
            # Outer glow for Neptune's orbit
            for i in range(len(pts) - 1):
                ed.line([pts[i], pts[i+1]], fill=(20, 100, 255, 50), width=8)
                
    canvas.paste(ecliptic_layer, (0, 0), ecliptic_layer)
    
    # 4. NEPTUNE SPHERE (Realistic textured gas giant)
    nep_deg = 205
    n_rad = math.radians(nep_deg)
    nep_x = sun_x + 480 * math.cos(n_rad)
    nep_y = sun_y + 480 * math.sin(n_rad) * cam_tilt + (480 * math.sin(n_rad) * 0.16)
    
    nep_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nep_layer)
    # Neptune halo
    for r in range(45, 10, -4):
        nd.ellipse([nep_x - r, nep_y - r, nep_x + r, nep_y + r], fill=(20, 110, 255, int(45 * (1 - r/45))))
    # Neptune body (radius 22px)
    for r in range(22, 0, -1):
        ratio = r / 22.0
        val_b = int(180 + 75 * (1 - ratio**0.6))
        val_g = int(80 + 70 * (1 - ratio**0.6))
        val_r = int(20 + 40 * (1 - ratio**0.6))
        nd.ellipse([nep_x - r, nep_y - r, nep_x + r, nep_y + r], fill=(val_r, val_g, val_b, 255))
    # Sunlit crescent rim on Neptune
    nd.arc([nep_x - 22, nep_y - 22, nep_x + 22, nep_y + 22], start=210, end=360, fill=(200, 235, 255, 255), width=3)
    nep_layer = nep_layer.filter(ImageFilter.GaussianBlur(1))
    canvas.paste(nep_layer, (0, 0), nep_layer)
    
    # 5. PLUTO'S INCLINED 17° ORBIT (Bold golden ribbon rising out of plane!)
    pluto_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pld = ImageDraw.Draw(pluto_layer)
    
    # Mathematical orbit with 17-degree physical tilt
    a = 460
    b = 430
    e = 0.2488
    c = a * e
    tilt_rad = math.radians(26) # Visual tilt
    arg_peri = math.radians(-30)
    
    pl_pts = []
    pl_z = []
    
    for deg in range(0, 361, 2):
        rad = math.radians(deg)
        x_raw = a * math.cos(rad) - c
        y_raw = b * math.sin(rad)
        
        # In-plane rotation
        x_rot = x_raw * math.cos(arg_peri) - y_raw * math.sin(arg_peri)
        y_rot = x_raw * math.sin(arg_peri) + y_raw * math.cos(arg_peri)
        
        # 17-deg vertical inclination
        x_3d = x_rot
        y_3d = y_rot * math.cos(tilt_rad)
        z_3d = y_rot * math.sin(tilt_rad) # Height above/below plane
        
        # Camera projection
        sx = sun_x + x_3d * 1.12
        sy = sun_y + y_3d * cam_tilt + (y_3d * 0.16) - (z_3d * 0.72)
        
        pl_pts.append((sx, sy))
        pl_z.append(z_3d)
        
    # Render golden/amber orbit ribbon
    for i in range(len(pl_pts) - 1):
        pt1, pt2 = pl_pts[i], pl_pts[i+1]
        z = pl_z[i]
        
        if z >= 0: # Above ecliptic (closer to camera / rising high)
            alpha = int(min(255, 170 + z * 0.65))
            # Golden amber core
            pld.line([pt1, pt2], fill=(255, 215, 90, alpha), width=4)
            # Volumetric golden aura
            pld.line([pt1, pt2], fill=(255, 180, 50, int(alpha * 0.45)), width=9)
        else: # Below ecliptic (diving down)
            alpha = int(max(65, 160 + z * 0.8))
            pld.line([pt1, pt2], fill=(210, 140, 50, alpha), width=3)
            
    # Vertical drop indicators showing 3D altitude above ecliptic plane
    for idx in range(0, len(pl_pts), 12):
        pt = pl_pts[idx]
        z = pl_z[idx]
        if abs(z) > 35:
            plane_pt_y = pt[1] + (z * 0.72)
            # Vertical drop line
            pld.line([(pt[0], pt[1]), (pt[0], plane_pt_y)], fill=(255, 205, 110, 80), width=1)
            # Plane intersection dot
            pld.ellipse([pt[0] - 2, plane_pt_y - 1, pt[0] + 2, plane_pt_y + 1], fill=(120, 170, 240, 120))
            
    # Position Pluto at high prominent position (Aphelion arch)
    p_idx = 105
    pluto_center = pl_pts[p_idx]
    
    # 6. PLUTO HERO SPHERE (Detailed textured 3D sphere)
    # Pluto body radius 28px
    pr = 28
    # Outer atmospheric haze glow
    for r in range(pr + 25, pr, -3):
        pld.ellipse([pluto_center[0] - r, pluto_center[1] - r, pluto_center[0] + r, pluto_center[1] + r],
                    fill=(255, 190, 90, int(45 * (1 - (r - pr)/25))))
    # Spherical Pluto shading (rich tan/reddish tholins & white heart)
    for r in range(pr, 0, -1):
        ratio = r / pr
        vr = int(220 + 35 * (1 - ratio**0.5))
        vg = int(170 + 30 * (1 - ratio**0.5))
        vb = int(130 + 25 * (1 - ratio**0.5))
        pld.ellipse([pluto_center[0] - r, pluto_center[1] - r, pluto_center[0] + r, pluto_center[1] + r],
                    fill=(vr, vg, vb, 255))
    # Sputnik Planitia heart feature highlight
    pld.ellipse([pluto_center[0] - 12, pluto_center[1] - 8, pluto_center[0] + 8, pluto_center[1] + 10],
                fill=(245, 238, 228, 255))
    # Sunlit crescent rim
    pld.arc([pluto_center[0] - pr, pluto_center[1] - pr, pluto_center[0] + pr, pluto_center[1] + pr],
            start=180, end=330, fill=(255, 250, 235, 255), width=3)
            
    # Charon orbiting Pluto
    charon_x = pluto_center[0] + 52
    charon_y = pluto_center[1] - 26
    for r in range(12, 0, -1):
        pld.ellipse([charon_x - r, charon_y - r, charon_x + r, charon_y + r], fill=(160, 160, 170, 255))
    pld.arc([charon_x - 12, charon_y - 12, charon_x + 12, charon_y + 12], start=180, end=330, fill=(240, 240, 250, 255), width=2)
    
    canvas.paste(pluto_layer, (0, 0), pluto_layer)
    
    # 7. Midground/Lower-Center: MOON VS PLUTO SCALE COMPARISON (Rich textured bodies)
    # Place at y: 1020 - 1250, fully integrated into space with volumetric glow!
    scale_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scale_layer)
    
    # Atmospheric backdrop aura for comparison
    sd.ellipse([W//2 - 280, 1020, W//2 + 280, 1260], fill=(15, 25, 55, 70))
    
    # Earth's Moon: Radius = 85px (at x: 360, y: 1140)
    # Textured lunar mare and highlands
    mc_x, mc_y, mr = 360, 1140, 85
    # Lunar glow
    for r in range(mr + 20, mr, -3):
        sd.ellipse([mc_x - r, mc_y - r, mc_x + r, mc_y + r], fill=(180, 200, 230, int(30 * (1 - (r - mr)/20))))
    for r in range(mr, 0, -1):
        ratio = r / mr
        lv = int(150 + 65 * (1 - ratio**0.6))
        sd.ellipse([mc_x - r, mc_y - r, mc_x + r, mc_y + r], fill=(lv, lv, int(lv * 1.06), 255))
    # Distinct lunar dark maria patches
    sd.ellipse([mc_x - 35, mc_y - 40, mc_x + 10, mc_y - 5], fill=(100, 102, 110, 160)) # Mare Imbrium
    sd.ellipse([mc_x - 10, mc_y + 5, mc_x + 40, mc_y + 45], fill=(105, 107, 115, 150)) # Mare Tranquillitatis
    sd.ellipse([mc_x - 45, mc_y + 10, mc_x - 15, mc_y + 35], fill=(110, 112, 120, 140)) # Oceanus Procellarum
    sd.arc([mc_x - mr, mc_y - mr, mc_x + mr, mc_y + mr], start=170, end=330, fill=(245, 250, 255, 230), width=3)
    
    # Pluto: Radius = 58px (Accurately 1188/1737 = 0.684 of Moon!) at (x: 700, y: 1140)
    pc_x, pc_y, pr_comp = 700, 1140, 58
    # Pluto glow
    for r in range(pr_comp + 20, pr_comp, -3):
        sd.ellipse([pc_x - r, pc_y - r, pc_x + r, pc_y + r], fill=(240, 180, 110, int(35 * (1 - (r - pr_comp)/20))))
    for r in range(pr_comp, 0, -1):
        ratio = r / pr_comp
        pvr = int(210 + 40 * (1 - ratio**0.6))
        pvg = int(160 + 35 * (1 - ratio**0.6))
        pvb = int(120 + 30 * (1 - ratio**0.6))
        sd.ellipse([pc_x - r, pc_y - r, pc_x + r, pc_y + r], fill=(pvr, pvg, pvb, 255))
    # Sputnik Planitia Heart on Pluto
    sd.ellipse([pc_x - 18, pc_y - 12, pc_x + 12, pc_y + 16], fill=(248, 240, 232, 230))
    # Red-brown tholin equatorial belt
    sd.arc([pc_x - pr_comp, pc_y - pr_comp, pc_x + pr_comp, pc_y + pr_comp], start=30, end=150, fill=(150, 80, 45, 220), width=5)
    # Bright sunlight rim
    sd.arc([pc_x - pr_comp, pc_y - pr_comp, pc_x + pr_comp, pc_y + pr_comp], start=170, end=330, fill=(255, 245, 225, 230), width=3)
    
    scale_layer = scale_layer.filter(ImageFilter.GaussianBlur(1))
    canvas.paste(scale_layer, (0, 0), scale_layer)
    
    # 8. Dark vignette for Subtitle Safe Area (y: 1380 - 1920)
    final_img = canvas.convert("RGB")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(1320, H):
        factor = (y - 1320) / (H - 1320)
        alpha = int(235 * (factor ** 1.3))
        od.line([(0, y), (W, y)], fill=(2, 4, 10, alpha))
    final_v = Image.alpha_composite(final_img.convert("RGBA"), overlay).convert("RGB")
    
    # 9. Photographic film grain & enhancement
    final_v = ImageEnhance.Contrast(final_v).enhance(1.10)
    final_v = ImageEnhance.Color(final_v).enhance(1.08)
    
    arr = np.array(final_v).astype(np.float32)
    grain = np.random.normal(0, 7, arr.shape)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    res = Image.fromarray(arr)
    
    res.save("assets/pluto_demoted_reel/scene-03-strange-orbit.png", "PNG")
    print("Scene 03 refined and saved!")

create_scene_03()
