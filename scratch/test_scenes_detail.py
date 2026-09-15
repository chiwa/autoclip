import os
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np

def create_starfield(w, h, seed=42, num_stars=300):
    np.random.seed(seed)
    star_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(star_img)
    for _ in range(num_stars):
        x = np.random.randint(0, w)
        y = np.random.randint(0, h)
        b = np.random.randint(90, 255)
        r = np.random.choice([1, 1, 1, 2])
        col = (b, int(b * 0.95), int(b * 1.1), np.random.randint(180, 255))
        draw.ellipse([x, y, x + r, y + r], fill=col)
    return star_img

def test_scene_04():
    # Hubble Decagon Discovery
    w, h = 1080, 1920
    canvas = Image.new("RGBA", (w, h), (3, 5, 14, 255))
    
    # 1. Hubble telescope in upper portion
    ht = Image.open("scratch/saturn_downloads/hubble_telescope.jpg").convert("RGBA")
    scale_ht = 680 / ht.width
    nh_ht = int(ht.height * scale_ht)
    ht_fit = ht.resize((680, nh_ht), Image.Resampling.LANCZOS)
    # feather edges of ht
    ht_arr = np.array(ht_fit, dtype=np.float32)
    fade = 60
    ht_arr[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    ht_arr[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    ht_arr[:, :fade, 3] *= np.linspace(0.0, 1.0, fade)[None, :]
    ht_arr[:, -fade:, 3] *= np.linspace(1.0, 0.0, fade)[None, :]
    ht_faded = Image.fromarray(np.clip(ht_arr, 0, 255).astype(np.uint8))
    canvas.paste(ht_faded, (40, 120), ht_faded)
    
    # 2. Decagon South Pole in center/lower-mid portion
    dec = Image.open("scratch/saturn_downloads/decagon_right_panel.png").convert("RGBA")
    # scale to 880x880
    dec_fit = dec.resize((880, 880), Image.Resampling.LANCZOS)
    dec_enh = ImageEnhance.Contrast(dec_fit).enhance(1.2)
    
    # Radial mask for decagon disc
    mask = Image.new("L", (880, 880), 0)
    draw_m = ImageDraw.Draw(mask)
    draw_m.ellipse([40, 40, 840, 840], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(35))
    
    canvas.paste(dec_enh, (100, 680), mask)
    
    # Starfield
    canvas.alpha_composite(create_starfield(w, h, seed=404))
    canvas.convert("RGB").save("scratch/saturn_preview/scene-04-hubble-decagon.png")
    print("Scene 04 OK")

def test_scene_05():
    # Fluid Dynamics & Rossby Waves (10-sided standing wave)
    w, h = 1080, 1920
    canvas = Image.new("RGB", (w, h), (4, 6, 18))
    draw = ImageDraw.Draw(canvas)
    
    # Starfield
    np.random.seed(505)
    for _ in range(400):
        sx = np.random.randint(0, w)
        sy = np.random.randint(0, h)
        sb = np.random.randint(90, 255)
        r = np.random.choice([1, 1, 1, 2])
        draw.ellipse([sx, sy, sx+r, sy+r], fill=(sb, int(sb*0.95), int(sb*1.1)))
    
    cx, cy = 540, 820
    
    # 1. Background rotating zonal shear streamlines
    for rad_base in range(120, 480, 24):
        pts = []
        for deg in range(0, 360, 3):
            th = math.radians(deg)
            # Add subtle Rossby perturbation
            r = rad_base + 8 * math.sin(10 * th + rad_base * 0.05)
            x = cx + r * math.cos(th)
            y = cy + r * math.sin(th)
            pts.append((x, y))
        intensity = max(30, min(180, int(220 - rad_base * 0.35)))
        draw.line(pts + [pts[0]], fill=(20, int(intensity*0.6), intensity), width=1)
    
    # 2. Hero 10-sided Rossby Wave Jet Stream (The Decagon Jet)
    r_decagon = 320
    decagon_pts = []
    for deg in range(0, 360, 1):
        th = math.radians(deg)
        # Decagon radial formula: r = r0 + A*cos(10*th)
        r = r_decagon + 28 * math.cos(10 * th)
        x = cx + r * math.cos(th)
        y = cy + r * math.sin(th)
        decagon_pts.append((x, y))
    
    # Glow layers for the 10-sided jet stream
    draw.line(decagon_pts + [decagon_pts[0]], fill=(40, 180, 255), width=6)
    draw.line(decagon_pts + [decagon_pts[0]], fill=(180, 240, 255), width=2)
    
    # 3. Highlight the 10 vertices/nodes of the Decagon
    for k in range(10):
        th = k * (2 * math.pi / 10)
        r = r_decagon + 28
        vx = cx + r * math.cos(th)
        vy = cy + r * math.sin(th)
        # Vertex glow
        draw.ellipse([vx-12, vy-12, vx+12, vy+12], fill=(255, 220, 120), outline=(255, 255, 200), width=2)
        # Small counter-rotating eddy next to each vertex
        ex = cx + (r - 45) * math.cos(th + 0.15)
        ey = cy + (r - 45) * math.sin(th + 0.15)
        draw.arc([ex-18, ey-18, ex+18, ey+18], start=0, end=300, fill=(255, 170, 80), width=2)
    
    # 4. Central polar hurricane vortex
    for r in range(90, 0, -4):
        val = int(255 * (1 - r/90))
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(int(val*0.1), int(val*0.4), int(val*0.7)))
    draw.ellipse([cx-18, cy-18, cx+18, cy+18], fill=(5, 10, 25))
    
    canvas.save("scratch/saturn_preview/scene-05-fluid-dynamics.png")
    print("Scene 05 OK")

def test_scene_07():
    # Cosmic Dual Geometry (North Hexagon vs South Decagon)
    w, h = 1080, 1920
    canvas = Image.new("RGBA", (w, h), (4, 6, 16, 255))
    
    # Top half: North Hexagon
    hex_src = Image.open("dist/mamase-cassini-saturn-wan-v2/images/scene-06-hexagon.png").convert("RGBA")
    # crop center square of hexagon
    hw, hh = hex_src.size
    hex_crop = hex_src.crop((0, 300, 1080, 1180)) # 1080x880
    # feather bottom
    arr_h = np.array(hex_crop, dtype=np.float32)
    fade = 140
    arr_h[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    hex_faded = Image.fromarray(np.clip(arr_h, 0, 255).astype(np.uint8))
    canvas.paste(hex_faded, (0, 60), hex_faded)
    
    # Bottom half: South Decagon
    dec_src = Image.open("scratch/saturn_downloads/decagon_right_panel.png").convert("RGBA")
    dec_fit = dec_src.resize((840, 840), Image.Resampling.LANCZOS)
    dec_enh = ImageEnhance.Contrast(dec_fit).enhance(1.25)
    mask = Image.new("L", (840, 840), 0)
    draw_m = ImageDraw.Draw(mask)
    draw_m.ellipse([30, 30, 810, 810], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(30))
    canvas.paste(dec_enh, (120, 800), mask)
    
    # Subtle dividers & Starfield
    canvas.alpha_composite(create_starfield(w, h, seed=707))
    canvas.convert("RGB").save("scratch/saturn_preview/scene-07-cosmic-dual-geometry.png")
    print("Scene 07 OK")

if __name__ == "__main__":
    test_scene_04()
    test_scene_05()
    test_scene_07()
