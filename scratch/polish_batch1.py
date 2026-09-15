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
        alpha = int(220 * (factor ** 1.3))
        draw.line([(0, y), (W, y)], fill=(2, 4, 10, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def add_film_grain(img, intensity=5):
    arr = np.array(img).astype(np.float32)
    grain = np.random.normal(0, intensity, arr.shape)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

# 1. Polish Scene 02: Fully cover the tiny bottom-right card as well
def polish_scene_02():
    comp = Image.open("scratch/pluto_raw/lowell_blink_comparator.jpg").convert("RGB")
    cw, ch = comp.size
    crop_w = int(ch * 9 / 16)
    crop_x1 = int((cw - crop_w) * 0.46)
    crop = comp.crop((crop_x1, 0, crop_x1 + crop_w, ch))
    res = crop.resize((W, H), Image.Resampling.LANCZOS).convert("RGBA")
    
    # Discovery star plate in aperture
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
    res.paste(p_star_warm, (ap_x - 135, ap_y - 135), ap_mask)
    
    # Glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for gr in range(320, 30, -15):
        alpha = int(45 * (1.0 - gr / 320.0) ** 1.6)
        gd.ellipse([ap_x - gr, ap_y - gr, ap_x + gr, ap_y + gr], fill=(255, 195, 75, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    res = Image.alpha_composite(res, glow)
    
    # Desk wood cover covering BOTH left card and right card completely!
    desk_cover = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dcd = ImageDraw.Draw(desk_cover)
    for y in range(1200, H):
        t = (y - 1200) / (H - 1200)
        mr = int(26 * (1.0 - t * 0.75))
        mg = int(16 * (1.0 - t * 0.75))
        mb = int(10 * (1.0 - t * 0.75))
        # Left area (x: 0 to 480, y > 1300)
        if y >= 1300:
            for x in range(0, 480):
                edge_f = max(0.0, min(1.0, (480 - x) / 50.0))
                a = int(255 * edge_f * min(1.0, (y - 1300) / 40.0))
                dcd.point((x, y), fill=(mr, mg, mb, a))
        # Right area (x: 840 to W, y > 1200)
        for x in range(840, W):
            edge_f = max(0.0, min(1.0, (x - 840) / 40.0))
            a = int(255 * edge_f * min(1.0, (y - 1200) / 30.0))
            dcd.point((x, y), fill=(mr, mg, mb, a))
            
    desk_cover = desk_cover.filter(ImageFilter.GaussianBlur(6))
    res = Image.alpha_composite(res, desk_cover)
    
    final = res.convert("RGB")
    final = apply_safe_area_vignette(final, dark_start=1380)
    final = ImageEnhance.Contrast(final).enhance(1.12)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-02-discovery.png")
    final.save(out_path, "PNG")
    print("Scene 02 polished!")

# 2. Polish Scene 03: Soften Neptune halo & enhance golden orbit glow
def polish_scene_03():
    canvas = Image.new("RGBA", (W, H), (3, 5, 12, 255))
    draw = ImageDraw.Draw(canvas)
    
    for y in range(H):
        t = y / H
        ambient = math.exp(-((y - 850)/550)**2)
        r = int(2 + 4 * (1 - t) + 12 * ambient)
        g = int(4 + 7 * (1 - t) + 16 * ambient)
        b = int(12 + 16 * (1 - t) + 30 * ambient)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(1717)
    for _ in range(1400):
        sx = np.random.randint(0, W)
        sy = np.random.randint(0, 1550)
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
            
    # Volumetric Milky Way dust
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    for i in range(160):
        t = i / 160.0
        nx = np.random.normal(W * (0.8 - 0.6 * t), 180)
        ny = np.random.normal(H * t, 220)
        nr = np.random.randint(80, 260)
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(16, 28, 75, 14))
    nebula = nebula.filter(ImageFilter.GaussianBlur(40))
    canvas.paste(nebula, (0, 0), nebula)
    
    # Distant Sun
    sun_x, sun_y = 880, 180
    sun_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sun_glow)
    for gr in range(350, 10, -10):
        alpha = int(75 * (1.0 - gr / 350.0) ** 1.8)
        sgd.ellipse([sun_x - gr, sun_y - gr, sun_x + gr, sun_y + gr], fill=(255, 225, 140, alpha))
    for deg in range(0, 360, 10):
        rad = math.radians(deg)
        rlen = np.random.randint(240, 520)
        ex = sun_x + rlen * math.cos(rad)
        ey = sun_y + rlen * math.sin(rad) * 0.7
        sgd.line([(sun_x, sun_y), (ex, ey)], fill=(255, 240, 180, 16), width=3)
    sun_glow = sun_glow.filter(ImageFilter.GaussianBlur(10))
    canvas.paste(sun_glow, (0, 0), sun_glow)
    draw.ellipse([sun_x - 14, sun_y - 14, sun_x + 14, sun_y + 14], fill=(255, 255, 255, 255))
    draw.ellipse([sun_x - 22, sun_y - 22, sun_x + 22, sun_y + 22], fill=(255, 245, 200, 170))
    
    # Orbits layer
    nep_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nld = ImageDraw.Draw(nep_layer)
    
    # Neptune's orbit
    for i in range(W):
        curv_y = 1260 + 80 * math.sin((i - 200) / 380.0)
        nld.line([(i, curv_y), (i+1, curv_y)], fill=(40, 150, 255, 200), width=3)
        nld.line([(i, curv_y), (i+1, curv_y)], fill=(15, 90, 255, 50), width=10)
        
    # Pluto's 17° tilted golden orbit ribbon
    for i in range(W):
        t_x = (i - 540) / 450.0
        orbit_y = 1080 + 360 * t_x - 110 * (t_x ** 2)
        nld.line([(i, orbit_y), (i+1, orbit_y)], fill=(255, 220, 100, 240), width=4)
        nld.line([(i, orbit_y), (i+1, orbit_y)], fill=(255, 185, 50, 80), width=12)
        nld.line([(i, orbit_y), (i+1, orbit_y)], fill=(255, 160, 30, 35), width=22)
        
    # Neptune sphere with soft atmospheric glow (no hard circle!)
    nep_x, nep_y = 240, 1260
    nep_raw = Image.open("scratch/pluto_raw/neptune_full.jpg").convert("RGBA")
    nep_sz = 140
    nep_sp = nep_raw.resize((nep_sz, nep_sz), Image.Resampling.LANCZOS)
    nep_m = Image.new("L", (nep_sz, nep_sz), 0)
    ImageDraw.Draw(nep_m).ellipse([3, 3, nep_sz - 3, nep_sz - 3], fill=255)
    nep_m = nep_m.filter(ImageFilter.GaussianBlur(1))
    
    # Soft, blended azure halo
    nep_halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nhd = ImageDraw.Draw(nep_halo)
    for gr in range(nep_sz//2 + 25, nep_sz//2, -3):
        alpha = int(35 * (1.0 - (gr - nep_sz//2)/25.0) ** 1.5)
        nhd.ellipse([nep_x - gr, nep_y - gr, nep_x + gr, nep_y + gr], fill=(30, 140, 255, alpha))
    nep_halo = nep_halo.filter(ImageFilter.GaussianBlur(6))
    nep_layer.paste(nep_halo, (0, 0), nep_halo)
    nep_layer.paste(nep_sp, (nep_x - nep_sz//2, nep_y - nep_sz//2), nep_m)
    canvas.paste(nep_layer, (0, 0), nep_layer)
    
    # Moon in upper frame
    moon_raw = Image.open("scratch/pluto_raw/moon_full.jpg").convert("RGBA")
    mw, mh = moon_raw.size
    mcx, mcy, mrad = mw // 2, mh // 2, int(min(mw, mh) * 0.42)
    moon_crop = moon_raw.crop((mcx - mrad, mcy - mrad, mcx + mrad, mcy + mrad))
    moon_sz = 460
    moon_sp = moon_crop.resize((moon_sz, moon_sz), Image.Resampling.LANCZOS)
    moon_m = Image.new("L", (moon_sz, moon_sz), 0)
    ImageDraw.Draw(moon_m).ellipse([2, 2, moon_sz - 2, moon_sz - 2], fill=255)
    moon_m = moon_m.filter(ImageFilter.GaussianBlur(1))
    
    moon_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mld = ImageDraw.Draw(moon_layer)
    for gr in range(moon_sz//2 + 30, moon_sz//2, -3):
        mld.ellipse([460 - gr, 360 - gr, 460 + gr, 360 + gr], fill=(180, 205, 240, int(20 * (1 - (gr - moon_sz//2)/30))))
    moon_layer.paste(moon_sp, (460 - moon_sz//2, 360 - moon_sz//2), moon_m)
    canvas.paste(moon_layer, (0, 0), moon_layer)
    
    # Pluto in midground (314px)
    pluto_raw = Image.open("scratch/pluto_raw/pluto_color_8k.jpg").convert("RGBA")
    pw, ph = pluto_raw.size
    pcx, pcy, prad = pw // 2, ph // 2, int(min(pw, ph) * 0.38)
    pluto_crop = pluto_raw.crop((pcx - prad, pcy - prad, pcx + prad, pcy + prad))
    pluto_sz = 314
    pluto_sp = pluto_crop.resize((pluto_sz, pluto_sz), Image.Resampling.LANCZOS)
    pluto_m = Image.new("L", (pluto_sz, pluto_sz), 0)
    ImageDraw.Draw(pluto_m).ellipse([2, 2, pluto_sz - 2, pluto_sz - 2], fill=255)
    pluto_m = pluto_m.filter(ImageFilter.GaussianBlur(1))
    
    pluto_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pld = ImageDraw.Draw(pluto_layer)
    for gr in range(pluto_sz//2 + 35, pluto_sz//2, -3):
        pld.ellipse([640 - gr, 820 - gr, 640 + gr, 820 + gr], fill=(240, 185, 100, int(26 * (1 - (gr - pluto_sz//2)/35))))
    pluto_layer.paste(pluto_sp, (640 - pluto_sz//2, 820 - pluto_sz//2), pluto_m)
    canvas.paste(pluto_layer, (0, 0), pluto_layer)
    
    # Charon (90px)
    charon_raw = Image.open("scratch/pluto_raw/charon_true_color.jpg").convert("RGBA")
    cw, ch = charon_raw.size
    charon_crop = charon_raw.crop((int(cw * 0.15), int(ch * 0.15), int(cw * 0.85), int(ch * 0.85)))
    charon_sz = 90
    charon_sp = charon_crop.resize((charon_sz, charon_sz), Image.Resampling.LANCZOS)
    charon_m = Image.new("L", (charon_sz, charon_sz), 0)
    ImageDraw.Draw(charon_m).ellipse([2, 2, charon_sz - 2, charon_sz - 2], fill=255)
    charon_m = charon_m.filter(ImageFilter.GaussianBlur(1))
    canvas.paste(charon_sp, (870 - charon_sz//2, 720 - charon_sz//2), charon_m)
    
    final = apply_safe_area_vignette(canvas.convert("RGB"), dark_start=1380)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = ImageEnhance.Color(final).enhance(1.08)
    final = add_film_grain(final, intensity=6)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-03-strange-orbit.png")
    final.save(out_path, "PNG")
    print("Scene 03 polished!")

if __name__ == "__main__":
    polish_scene_02()
    polish_scene_03()
    print("Polishing done!")
