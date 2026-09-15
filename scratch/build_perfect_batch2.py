import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUTPUT_DIR = "assets/pluto_demoted_reel"
W, H = 1080, 1920

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
# PERFECT SCENE 05: THE PRAGUE VOTE (Audience Sea of Yellow Cards, Zero Text)
# ==============================================================================
def make_perfect_scene_05():
    print("--- Generating Perfect Scene 05: Prague Vote ---")
    iau_raw = Image.open("scratch/pluto_raw/iau_vote_prague.jpg").convert("RGB")
    iw, ih = iau_raw.size # 3872, 2592
    
    # 9:16 vertical crop focused on the audience of astronomers holding up yellow cards
    # Height = 2250, Width = 2250 * 9 / 16 = 1265
    crop_h = 2250
    crop_w = int(crop_h * 9 / 16) # 1265
    
    # x from 350 to 1615, y from 340 to 2590 (completely excludes the stage screens!)
    crop_x1 = 380
    crop_y1 = 340
    crop = iau_raw.crop((crop_x1, crop_y1, crop_x1 + crop_w, crop_y1 + crop_h))
    
    res = crop.resize((W, H), Image.Resampling.LANCZOS)
    
    # Color grade: Enhance the brilliant warm yellow cards and rich mahogany theater seats
    r, g, b = res.split()
    r = r.point(lambda p: min(255, int(p * 1.08)))
    g = g.point(lambda p: min(255, int(p * 1.04)))
    b = b.point(lambda p: min(255, int(p * 0.94)))
    res_graded = Image.merge("RGB", (r, g, b))
    
    # Safe area vignette at the bottom
    final = apply_safe_area_vignette(res_graded, dark_start=1380)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-05-prague-vote.png")
    final.save(out_path, "PNG")
    print(f"Perfect Scene 05 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

# ==============================================================================
# PERFECT SCENE 06: ORBIT CLEARING VS KUIPER BELT SWARM (Real Asteroids)
# ==============================================================================
def make_perfect_scene_06():
    print("--- Generating Perfect Scene 06: Orbit Clearing ---")
    canvas = Image.new("RGBA", (W, H), (2, 4, 10, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Cosmic Deep Space Background
    for y in range(H):
        t = y / H
        ambient = math.exp(-((y - 700)/450)**2)
        r = int(2 + 4 * (1 - t) + 10 * ambient)
        g = int(4 + 6 * (1 - t) + 14 * ambient)
        b = int(12 + 16 * (1 - t) + 28 * ambient)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(2006)
    for _ in range(1200):
        sx = np.random.randint(0, W)
        sy = np.random.randint(0, 1500)
        bright = np.random.randint(70, 255)
        color_type = np.random.choice(["blue", "gold", "white", "cyan"], p=[0.25, 0.2, 0.45, 0.1])
        if color_type == "blue":
            col = (int(bright * 0.8), int(bright * 0.9), bright, 240)
        elif color_type == "gold":
            col = (bright, int(bright * 0.9), int(bright * 0.65), 240)
        else:
            col = (bright, bright, bright, 250)
        sz = np.random.choice([1, 1, 1, 2, 2, 3], p=[0.75, 0.12, 0.08, 0.03, 0.015, 0.005])
        if sz == 1:
            draw.point((sx, sy), fill=col)
        else:
            draw.ellipse([sx-sz, sy-sz, sx+sz, sy+sz], fill=col)
            
    # Volumetric nebulae
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    for _ in range(120):
        nx = np.random.normal(W * 0.5, 280)
        ny = np.random.normal(680, 320)
        nr = np.random.randint(80, 260)
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(16, 28, 70, 14))
    nebula = nebula.filter(ImageFilter.GaussianBlur(38))
    canvas.paste(nebula, (0, 0), nebula)
    
    # 2. Distant Sun: Directional light from upper-left (x: 180, y: 160)
    sun_x, sun_y = 180, 160
    sun_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sun_glow)
    for gr in range(320, 10, -10):
        alpha = int(75 * (1.0 - gr / 320.0) ** 1.8)
        sgd.ellipse([sun_x - gr, sun_y - gr, sun_x + gr, sun_y + gr], fill=(255, 225, 140, alpha))
    for deg in range(0, 360, 12):
        rad = math.radians(deg)
        rlen = np.random.randint(200, 420)
        ex = sun_x + rlen * math.cos(rad)
        ey = sun_y + rlen * math.sin(rad) * 0.7
        sgd.line([(sun_x, sun_y), (ex, ey)], fill=(255, 240, 180, 16), width=3)
    sun_glow = sun_glow.filter(ImageFilter.GaussianBlur(10))
    canvas.paste(sun_glow, (0, 0), sun_glow)
    draw.ellipse([sun_x - 14, sun_y - 14, sun_x + 14, sun_y + 14], fill=(255, 255, 255, 255))
    
    # 3. TOP HALF: NEPTUNE'S PRISTINE CLEARED ORBIT CORRIDOR (y: 260 to 620)
    top_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tld = ImageDraw.Draw(top_layer)
    
    for x in range(W):
        cy = 440 + 60 * math.sin((x - 200) / 360.0)
        tld.line([(x, cy - 75), (x, cy + 75)], fill=(12, 38, 85, 30), width=2)
        tld.line([(x, cy - 75), (x+1, cy - 75)], fill=(50, 150, 255, 75), width=1)
        tld.line([(x, cy + 75), (x+1, cy + 75)], fill=(50, 150, 255, 75), width=1)
        tld.line([(x, cy), (x+1, cy)], fill=(60, 180, 255, 220), width=3)
        tld.line([(x, cy), (x+1, cy)], fill=(20, 100, 255, 60), width=10)
        
    nep_raw = Image.open("scratch/pluto_raw/neptune_full.jpg").convert("RGBA")
    nep_sz = 160
    nep_sp = nep_raw.resize((nep_sz, nep_sz), Image.Resampling.LANCZOS)
    nep_m = Image.new("L", (nep_sz, nep_sz), 0)
    ImageDraw.Draw(nep_m).ellipse([3, 3, nep_sz - 3, nep_sz - 3], fill=255)
    nep_m = nep_m.filter(ImageFilter.GaussianBlur(1))
    
    for gr in range(nep_sz//2 + 30, nep_sz//2, -3):
        tld.ellipse([740 - gr, 460 - gr, 740 + gr, 460 + gr], fill=(30, 140, 255, int(40 * (1 - (gr - nep_sz//2)/30))))
    top_layer.paste(nep_sp, (740 - nep_sz//2, 460 - nep_sz//2), nep_m)
    canvas.paste(top_layer, (0, 0), top_layer)
    
    # 4. BOTTOM HALF: PLUTO'S UNCLEARED KUIPER SWARM (Real NASA Asteroids!)
    # y: 760 to 1340
    bot_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bld = ImageDraw.Draw(bot_layer)
    
    # Golden orbit path
    for x in range(W):
        py = 1040 - 70 * math.sin((x - 180) / 340.0)
        bld.line([(x, py), (x+1, py)], fill=(255, 215, 90, 220), width=3)
        bld.line([(x, py), (x+1, py)], fill=(255, 175, 45, 65), width=9)
        
    # Load authentic NASA asteroid texture (asteroid_eros.jpg)
    eros_raw = Image.open("scratch/pluto_raw/asteroid_eros.jpg").convert("RGBA")
    ew, eh = eros_raw.size
    # Crop central asteroid body
    eros_crop = eros_raw.crop((int(ew * 0.15), int(eh * 0.15), int(ew * 0.85), int(eh * 0.85)))
    
    # Scatter 180 realistic NASA asteroids around Pluto's path
    np.random.seed(2006)
    for i in range(180):
        ax = np.random.randint(30, W - 30)
        ay = int(np.random.normal(1040, 110))
        # Distance to Pluto (at x: 380, y: 1040)
        dist = math.hypot(ax - 380, ay - 1040)
        if dist < 125:
            continue
            
        # Varied asteroid sizes (8px to 45px)
        asz = np.random.randint(10, 42)
        ast_resized = eros_crop.resize((asz, asz), Image.Resampling.LANCZOS)
        
        # Random rotation & alpha
        rot_angle = np.random.randint(0, 360)
        ast_rot = ast_resized.rotate(rot_angle, expand=True, resample=Image.Resampling.BICUBIC)
        
        # Mask for clean edges
        ast_mask = Image.new("L", ast_rot.size, 0)
        ImageDraw.Draw(ast_mask).ellipse([2, 2, ast_rot.width - 2, ast_rot.height - 2], fill=220)
        ast_mask = ast_mask.filter(ImageFilter.GaussianBlur(1))
        
        bot_layer.paste(ast_rot, (ax - ast_rot.width//2, ay - ast_rot.height//2), ast_mask)
        
    # Pluto in center of swarm (x: 380, y: 1040)
    pluto_raw = Image.open("scratch/pluto_raw/pluto_color_8k.jpg").convert("RGBA")
    pw, ph = pluto_raw.size
    pcx, pcy, prad = pw // 2, ph // 2, int(min(pw, ph) * 0.38)
    pluto_crop = pluto_raw.crop((pcx - prad, pcy - prad, pcx + prad, pcy + prad))
    
    pluto_sz = 210
    pluto_sp = pluto_crop.resize((pluto_sz, pluto_sz), Image.Resampling.LANCZOS)
    pluto_m = Image.new("L", (pluto_sz, pluto_sz), 0)
    ImageDraw.Draw(pluto_m).ellipse([3, 3, pluto_sz - 3, pluto_sz - 3], fill=255)
    pluto_m = pluto_m.filter(ImageFilter.GaussianBlur(1))
    
    for gr in range(pluto_sz//2 + 35, pluto_sz//2, -3):
        bld.ellipse([380 - gr, 1040 - gr, 380 + gr, 1040 + gr], fill=(240, 185, 100, int(35 * (1 - (gr - pluto_sz//2)/35))))
    bot_layer.paste(pluto_sp, (380 - pluto_sz//2, 1040 - pluto_sz//2), pluto_m)
    
    canvas.paste(bot_layer, (0, 0), bot_layer)
    
    # Safe area vignette
    final = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1360)
    final = ImageEnhance.Contrast(final).enhance(1.12)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-06-three-criteria.png")
    final.save(out_path, "PNG")
    print(f"Perfect Scene 06 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

# ==============================================================================
# PERFECT SCENE 07: PLUTO & CHARON BINARY SYSTEM WITH KUIPER REALM DEPTH
# ==============================================================================
def make_perfect_scene_07():
    print("--- Generating Perfect Scene 07: Binary System ---")
    canvas = Image.new("RGBA", (W, H), (2, 4, 10, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Deep Space Background with Kuiper Belt Plane Dust
    for y in range(H):
        t = y / H
        ambient = math.exp(-((y - 850)/550)**2)
        r = int(2 + 4 * (1 - t) + 12 * ambient)
        g = int(4 + 6 * (1 - t) + 16 * ambient)
        b = int(12 + 16 * (1 - t) + 30 * ambient)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(2015)
    for _ in range(1400):
        sx = np.random.randint(0, W)
        sy = np.random.randint(0, 1550)
        bright = np.random.randint(70, 255)
        color_type = np.random.choice(["blue", "gold", "white", "cyan"], p=[0.25, 0.2, 0.45, 0.1])
        if color_type == "blue":
            col = (int(bright * 0.8), int(bright * 0.9), bright, 240)
        elif color_type == "gold":
            col = (bright, int(bright * 0.9), int(bright * 0.65), 240)
        else:
            col = (bright, bright, bright, 250)
        sz = np.random.choice([1, 1, 1, 2, 2, 3], p=[0.75, 0.12, 0.08, 0.03, 0.015, 0.005])
        if sz == 1:
            draw.point((sx, sy), fill=col)
        else:
            draw.ellipse([sx-sz, sy-sz, sx+sz, sy+sz], fill=col)
            
    # Glowing plane of the Kuiper Belt stretching across lower midground (y: 1000 to 1420)
    kuiper_dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kdd = ImageDraw.Draw(kuiper_dust)
    for i in range(180):
        t = i / 180.0
        nx = np.random.normal(W * t, 120)
        ny = np.random.normal(1180 + 80 * math.sin(t * math.pi), 70)
        nr = np.random.randint(60, 200)
        kdd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(22, 38, 85, 16))
    kuiper_dust = kuiper_dust.filter(ImageFilter.GaussianBlur(35))
    canvas.paste(kuiper_dust, (0, 0), kuiper_dust)
    
    # Distant Kuiper Belt planetesimals floating in background depth (y: 1100 to 1380)
    for _ in range(60):
        kx = np.random.randint(40, W - 40)
        ky = np.random.randint(1120, 1360)
        kr = np.random.randint(2, 6)
        draw.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(180, 210, 245, np.random.randint(120, 220)))
        
    # 2. Distant Sun: Needle-sharp star at 40 AU (upper-right: 880, 220)
    sun_x, sun_y = 880, 220
    sun_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sod = ImageDraw.Draw(sun_overlay)
    spike_l = 190
    for l in range(spike_l, 0, -4):
        alpha = int(160 * (1 - l / spike_l))
        sod.line([(sun_x - l, sun_y), (sun_x + l, sun_y)], fill=(240, 248, 255, alpha), width=1)
        sod.line([(sun_x, sun_y - l), (sun_x, sun_y + l)], fill=(240, 248, 255, alpha), width=1)
    for gr in range(45, 3, -3):
        sod.ellipse([sun_x - gr, sun_y - gr, sun_x + gr, sun_y + gr], fill=(225, 245, 255, int(45 * (1 - gr/45))))
    sod.ellipse([sun_x - 4, sun_y - 4, sun_x + 4, sun_y + 4], fill=(255, 255, 255, 255))
    sun_overlay = sun_overlay.filter(ImageFilter.GaussianBlur(1))
    canvas.paste(sun_overlay, (0, 0), sun_overlay)
    
    # 3. HERO BINARY SYSTEM: PLUTO & CHARON (Dominating the central frame heroically!)
    system_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sld = ImageDraw.Draw(system_layer)
    
    # Mutual barycenter orbit paths
    bary_x, bary_y = 540, 780
    for deg in range(0, 360, 3):
        rad = math.radians(deg)
        pt_x = bary_x + 100 * math.cos(rad)
        pt_y = bary_y + 100 * math.sin(rad) * 0.55
        sld.point((pt_x, pt_y), fill=(255, 215, 100, 110))
        ct_x = bary_x - 260 * math.cos(rad)
        ct_y = bary_y - 260 * math.sin(rad) * 0.55
        sld.point((ct_x, ct_y), fill=(180, 210, 255, 90))
        
    # Barycenter cross in empty space
    sld.line([(bary_x - 10, bary_y), (bary_x + 10, bary_y)], fill=(255, 235, 180, 180), width=1)
    sld.line([(bary_x, bary_y - 10), (bary_x, bary_y + 10)], fill=(255, 235, 180, 180), width=1)
    
    # HERO PLUTO (Diameter ~ 520px!)
    pluto_raw = Image.open("scratch/pluto_raw/pluto_color_8k.jpg").convert("RGBA")
    pw, ph = pluto_raw.size
    pcx, pcy, prad = pw // 2, ph // 2, int(min(pw, ph) * 0.38)
    pluto_crop = pluto_raw.crop((pcx - prad, pcy - prad, pcx + prad, pcy + prad))
    
    pluto_sz = 520
    pluto_sp = pluto_crop.resize((pluto_sz, pluto_sz), Image.Resampling.LANCZOS)
    pluto_m = Image.new("L", (pluto_sz, pluto_sz), 0)
    ImageDraw.Draw(pluto_m).ellipse([3, 3, pluto_sz - 3, pluto_sz - 3], fill=255)
    pluto_m = pluto_m.filter(ImageFilter.GaussianBlur(1))
    
    # Warm golden/hazy halo around Pluto
    for gr in range(pluto_sz//2 + 40, pluto_sz//2, -3):
        sld.ellipse([410 - gr, 780 - gr, 410 + gr, 780 + gr], fill=(240, 180, 95, int(35 * (1 - (gr - pluto_sz//2)/40))))
    system_layer.paste(pluto_sp, (410 - pluto_sz//2, 780 - pluto_sz//2), pluto_m)
    
    # HERO CHARON (Diameter ~ 270px)
    charon_raw = Image.open("scratch/pluto_raw/charon_true_color.jpg").convert("RGBA")
    cw, ch = charon_raw.size
    charon_crop = charon_raw.crop((int(cw * 0.15), int(ch * 0.15), int(cw * 0.85), int(ch * 0.85)))
    
    charon_sz = 270
    charon_sp = charon_crop.resize((charon_sz, charon_sz), Image.Resampling.LANCZOS)
    charon_m = Image.new("L", (charon_sz, charon_sz), 0)
    ImageDraw.Draw(charon_m).ellipse([2, 2, charon_sz - 2, charon_sz - 2], fill=255)
    charon_m = charon_m.filter(ImageFilter.GaussianBlur(1))
    
    for gr in range(charon_sz//2 + 25, charon_sz//2, -3):
        sld.ellipse([830 - gr, 590 - gr, 830 + gr, 590 + gr], fill=(180, 205, 235, int(25 * (1 - (gr - charon_sz//2)/25))))
    system_layer.paste(charon_sp, (830 - charon_sz//2, 590 - charon_sz//2), charon_m)
    
    canvas.paste(system_layer, (0, 0), system_layer)
    
    # Safe area vignette
    final = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1380)
    final = ImageEnhance.Contrast(final).enhance(1.12)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-07-dwarf-planet-king.png")
    final.save(out_path, "PNG")
    print(f"Perfect Scene 07 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    make_perfect_scene_05()
    make_perfect_scene_06()
    make_perfect_scene_07()
    print("Batch 2 perfected!")
