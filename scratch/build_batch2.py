import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUTPUT_DIR = "assets/pluto_demoted_reel"
W, H = 1080, 1920

def apply_safe_area_vignette(img, dark_start=1360):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(dark_start, H):
        factor = (y - dark_start) / (H - dark_start)
        alpha = int(220 * (factor ** 1.3))
        draw.line([(0, y), (W, y)], fill=(2, 4, 10, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def add_film_grain(img, intensity=5):
    arr = np.array(img).astype(np.float32)
    grain = np.random.normal(0, intensity, arr.shape)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

# ==============================================================================
# SCENE 05: THE PRAGUE VOTE (2006) - IAU GENERAL ASSEMBLY
# ==============================================================================
def make_scene_05():
    print("--- Generating Scene 05: The Prague Vote (2006) ---")
    # Load authentic 3872x2592 photo of 2006 IAU voting hall in Prague
    iau_raw = Image.open("scratch/pluto_raw/iau_vote_prague.jpg").convert("RGB")
    iw, ih = iau_raw.size # 3872, 2592
    
    # 9:16 vertical crop:
    # Height = 2592, Width = 2592 * 9 / 16 = 1458
    crop_h = ih
    crop_w = int(ih * 9 / 16) # 1458
    
    # Crop to capture the dramatic sweep of astronomers holding up yellow voting cards
    # Center on the audience holding cards, with the illuminated stage in upper-midground
    crop_x1 = int(iw * 0.22) # Captures sea of yellow cards and stage
    crop_y1 = 0
    iau_crop = iau_raw.crop((crop_x1, crop_y1, crop_x1 + crop_w, crop_h))
    
    # Resize to 1080x1920
    res = iau_crop.resize((W, H), Image.Resampling.LANCZOS).convert("RGBA")
    
    # Soften the stage presentation screen so slide text is not distracting/baked English text
    # In the crop, the screen is roughly at x: 480-1020, y: 150-520
    screen_blur = res.crop((460, 140, 1040, 540)).filter(ImageFilter.GaussianBlur(12))
    res.paste(screen_blur, (460, 140))
    
    # Enhance the iconic yellow voting cards (warm yellow pop)
    # The yellow cards held up by astronomers are the emotional & historical core!
    r, g, b, a = res.split()
    r = r.point(lambda p: min(255, int(p * 1.10)))
    g = g.point(lambda p: min(255, int(p * 1.05)))
    b = b.point(lambda p: min(255, int(p * 0.95)))
    res_graded = Image.merge("RGBA", (r, g, b, a))
    
    # Subtle warm auditorium lighting gradient
    hall_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hgd = ImageDraw.Draw(hall_glow)
    for gr in range(450, 40, -25):
        alpha = int(30 * (1.0 - gr / 450.0) ** 1.5)
        hgd.ellipse([W//2 - gr, 450 - int(gr * 0.6), W//2 + gr, 450 + int(gr * 0.6)], fill=(255, 210, 120, alpha))
    hall_glow = hall_glow.filter(ImageFilter.GaussianBlur(30))
    res_graded = Image.alpha_composite(res_graded, hall_glow)
    
    final = res_graded.convert("RGB")
    final = apply_safe_area_vignette(final, dark_start=1360)
    final = ImageEnhance.Contrast(final).enhance(1.12)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-05-prague-vote.png")
    final.save(out_path, "PNG")
    print(f"Scene 05 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

# ==============================================================================
# SCENE 06: THE 3 CRITERIA - ORBIT CLEARING VS KUIPER SWARM
# ==============================================================================
def make_scene_06():
    print("--- Generating Scene 06: Orbit Clearing vs Kuiper Swarm ---")
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
    for _ in range(1100):
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
            
    # Volumetric nebular clouds
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
    
    # 3. TOP HALF: TRUE PLANET'S CLEARED ORBIT CORRIDOR (Neptune)
    # y: 220 to 650
    # Shows Neptune sweeping a clean, vacuum orbital corridor with glowing gravitational boundary!
    top_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tld = ImageDraw.Draw(top_layer)
    
    # Pristine cleared orbital corridor (translucent glowing cyan/blue lane)
    for x in range(W):
        cy = 440 + 60 * math.sin((x - 200) / 360.0)
        # Cleared vacuum corridor
        tld.line([(x, cy - 80), (x, cy + 80)], fill=(10, 35, 75, 25), width=2)
        # Gravitational clearing boundary lines
        tld.line([(x, cy - 80), (x+1, cy - 80)], fill=(40, 140, 255, 80), width=1)
        tld.line([(x, cy + 80), (x+1, cy + 80)], fill=(40, 140, 255, 80), width=1)
        # Center orbital trajectory
        tld.line([(x, cy), (x+1, cy)], fill=(60, 180, 255, 220), width=3)
        tld.line([(x, cy), (x+1, cy)], fill=(20, 100, 255, 60), width=10)
        
    # Neptune on its cleared path (x: 740, y: 460)
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
    
    # 4. BOTTOM HALF: PLUTO'S UNCLEARED KUIPER SWARM CORRIDOR
    # y: 780 to 1340
    # Shows Pluto traveling right through a dense, chaotic swarm of frozen Kuiper Belt objects!
    bot_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bld = ImageDraw.Draw(bot_layer)
    
    # Pluto's golden orbit cutting through the asteroid field
    for x in range(W):
        py = 1040 - 70 * math.sin((x - 180) / 340.0)
        bld.line([(x, py), (x+1, py)], fill=(255, 215, 90, 220), width=3)
        bld.line([(x, py), (x+1, py)], fill=(255, 175, 45, 65), width=9)
        
    # Swarm of hundreds of icy Kuiper Belt asteroids, planetesimals, and frozen fragments!
    # Surrounding Pluto's path, proving it HAS NOT cleared its neighborhood!
    np.random.seed(2006)
    for _ in range(320):
        ax = np.random.randint(40, W - 40)
        # Concentrated along y: 880 to 1250
        ay = int(np.random.normal(1040, 110))
        # Distance to Pluto center (we will place Pluto at x: 380, y: 1040)
        dist = math.hypot(ax - 380, ay - 1040)
        if dist < 120:
            continue # Don't overlap Pluto's body
            
        aw = np.random.randint(6, 26)
        ah = int(aw * np.random.uniform(0.6, 0.9))
        angle = np.random.randint(0, 180)
        
        # Draw realistic frozen asteroid with sunlit facet and shadow
        ast_img = Image.new("RGBA", (aw * 2, ah * 2), (0, 0, 0, 0))
        ad = ImageDraw.Draw(ast_img)
        ad.ellipse([2, 2, aw * 2 - 4, ah * 2 - 4], fill=(35, 45, 65, 230))
        # Sunlit crescent rim (facing top-left sun)
        ad.arc([2, 2, aw * 2 - 4, ah * 2 - 4], start=160, end=300, fill=(200, 230, 255, 220), width=2)
        # Specular glint
        ad.point((int(aw * 0.8), int(ah * 0.7)), fill=(255, 255, 255, 255))
        
        ast_rot = ast_img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
        bot_layer.paste(ast_rot, (ax - ast_rot.width//2, ay - ast_rot.height//2), ast_rot)
        
    # Pluto in the middle of the swarm (x: 380, y: 1040)
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
    
    # 5. Clean Safe Area Vignette & Polish
    final = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1360)
    final = ImageEnhance.Contrast(final).enhance(1.12)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-06-three-criteria.png")
    final.save(out_path, "PNG")
    print(f"Scene 06 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

# ==============================================================================
# SCENE 07: RECLASSIFIED - KING OF THE DWARF PLANETS (PLUTO & CHARON BINARY)
# ==============================================================================
def make_scene_07():
    print("--- Generating Scene 07: Pluto & Charon Binary World ---")
    canvas = Image.new("RGBA", (W, H), (2, 4, 10, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Deep Space Background with Kuiper Belt Distant Realm
    for y in range(H):
        t = y / H
        ambient = math.exp(-((y - 800)/500)**2)
        r = int(2 + 4 * (1 - t) + 12 * ambient)
        g = int(4 + 6 * (1 - t) + 16 * ambient)
        b = int(12 + 16 * (1 - t) + 30 * ambient)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(2015)
    for _ in range(1300):
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
            
    # Rich deep space dust
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    for _ in range(140):
        nx = np.random.normal(W * 0.5, 300)
        ny = np.random.normal(700, 350)
        nr = np.random.randint(90, 280)
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(16, 28, 75, 14))
    nebula = nebula.filter(ImageFilter.GaussianBlur(40))
    canvas.paste(nebula, (0, 0), nebula)
    
    # 2. Distant Sun: At 40 AU, needle-sharp pinpoint of light in upper-right (x: 880, y: 220)
    sun_x, sun_y = 880, 220
    sun_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sod = ImageDraw.Draw(sun_overlay)
    spike_l = 190
    for l in range(spike_l, 0, -4):
        alpha = int(160 * (1 - l / spike_l))
        sod.line([(sun_x - l, sun_y), (sun_x + l, sun_y)], fill=(240, 248, 255, alpha), width=1)
        sod.line([(sun_x, sun_y - l), (sun_x, sun_y + l)], fill=(240, 248, 255, alpha), width=1)
    for l in range(int(spike_l * 0.5), 0, -4):
        alpha = int(80 * (1 - l / (spike_l * 0.5)))
        sod.line([(sun_x - l, sun_y - l), (sun_x + l, sun_y + l)], fill=(210, 235, 255, alpha), width=1)
        sod.line([(sun_x - l, sun_y + l), (sun_x + l, sun_y - l)], fill=(210, 235, 255, alpha), width=1)
    for gr in range(45, 3, -3):
        sod.ellipse([sun_x - gr, sun_y - gr, sun_x + gr, sun_y + gr], fill=(225, 245, 255, int(45 * (1 - gr/45))))
    sod.ellipse([sun_x - 4, sun_y - 4, sun_x + 4, sun_y + 4], fill=(255, 255, 255, 255))
    sun_overlay = sun_overlay.filter(ImageFilter.GaussianBlur(1))
    canvas.paste(sun_overlay, (0, 0), sun_overlay)
    
    # 3. BINARY DWARF PLANET PORTRAIT: PLUTO & CHARON
    # Both orbiting their mutual barycenter in empty space!
    system_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sld = ImageDraw.Draw(system_layer)
    
    # Mutual barycenter orbit ellipses (glowing delicate cyan paths)
    bary_x, bary_y = 540, 780
    # Dotted/faint barycentric circular tracks
    for deg in range(0, 360, 4):
        rad = math.radians(deg)
        # Pluto orbit track (radius ~ 90px around barycenter)
        p_track_x = bary_x + 90 * math.cos(rad)
        p_track_y = bary_y + 90 * math.sin(rad) * 0.55
        sld.point((p_track_x, p_track_y), fill=(255, 215, 100, 110))
        # Charon orbit track (radius ~ 240px around barycenter)
        c_track_x = bary_x - 240 * math.cos(rad)
        c_track_y = bary_y - 240 * math.sin(rad) * 0.55
        sld.point((c_track_x, c_track_y), fill=(180, 210, 255, 90))
        
    # Luminous Barycenter marker (+) in empty space
    sld.line([(bary_x - 12, bary_y), (bary_x + 12, bary_y)], fill=(255, 235, 180, 180), width=1)
    sld.line([(bary_x, bary_y - 12), (bary_x, bary_y + 12)], fill=(255, 235, 180, 180), width=1)
    
    # HERO PLUTO (Dominating the left, y: 720)
    # Diameter ~ 480px!
    pluto_raw = Image.open("scratch/pluto_raw/pluto_color_8k.jpg").convert("RGBA")
    pw, ph = pluto_raw.size
    pcx, pcy, prad = pw // 2, ph // 2, int(min(pw, ph) * 0.38)
    pluto_crop = pluto_raw.crop((pcx - prad, pcy - prad, pcx + prad, pcy + prad))
    
    pluto_sz = 460
    pluto_sp = pluto_crop.resize((pluto_sz, pluto_sz), Image.Resampling.LANCZOS)
    pluto_m = Image.new("L", (pluto_sz, pluto_sz), 0)
    ImageDraw.Draw(pluto_m).ellipse([3, 3, pluto_sz - 3, pluto_sz - 3], fill=255)
    pluto_m = pluto_m.filter(ImageFilter.GaussianBlur(1))
    
    # Golden atmospheric haze halo
    for gr in range(pluto_sz//2 + 40, pluto_sz//2, -3):
        sld.ellipse([420 - gr, 780 - gr, 420 + gr, 780 + gr], fill=(240, 180, 95, int(35 * (1 - (gr - pluto_sz//2)/40))))
    system_layer.paste(pluto_sp, (420 - pluto_sz//2, 780 - pluto_sz//2), pluto_m)
    
    # HERO CHARON (Orbiting on the right, y: 620)
    # Diameter ~ 240px (accurately ~ half of Pluto)!
    charon_raw = Image.open("scratch/pluto_raw/charon_true_color.jpg").convert("RGBA")
    cw, ch = charon_raw.size
    charon_crop = charon_raw.crop((int(cw * 0.15), int(ch * 0.15), int(cw * 0.85), int(ch * 0.85)))
    
    charon_sz = 240
    charon_sp = charon_crop.resize((charon_sz, charon_sz), Image.Resampling.LANCZOS)
    charon_m = Image.new("L", (charon_sz, charon_sz), 0)
    ImageDraw.Draw(charon_m).ellipse([2, 2, charon_sz - 2, charon_sz - 2], fill=255)
    charon_m = charon_m.filter(ImageFilter.GaussianBlur(1))
    
    # Charon halo
    for gr in range(charon_sz//2 + 25, charon_sz//2, -3):
        sld.ellipse([820 - gr, 620 - gr, 820 + gr, 620 + gr], fill=(180, 205, 235, int(25 * (1 - (gr - charon_sz//2)/25))))
    system_layer.paste(charon_sp, (820 - charon_sz//2, 620 - charon_sz//2), charon_m)
    
    canvas.paste(system_layer, (0, 0), system_layer)
    
    # 4. Safe Area Vignette & Polish
    final = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1360)
    final = ImageEnhance.Contrast(final).enhance(1.12)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-07-dwarf-planet-king.png")
    final.save(out_path, "PNG")
    print(f"Scene 07 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    make_scene_05()
    make_scene_06()
    make_scene_07()
    print("Batch 2 completed successfully!")
