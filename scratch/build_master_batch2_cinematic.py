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
        alpha = int(225 * (factor ** 1.35))
        draw.line([(0, y), (W, y)], fill=(2, 4, 10, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def add_film_grain(img, intensity=4):
    arr = np.array(img).astype(np.float32)
    grain = np.random.normal(0, intensity, arr.shape)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def render_3d_sphere(texture_crop, size, light_dir=(0.7, 0.4, 0.5), ambient=0.22, limb_color=(120, 180, 255), limb_strength=0.35):
    """
    Renders a sphere with true 3D surface normals and directional lighting.
    light_dir: (lx, ly, lz) normalized vector towards light source
    """
    lx, ly, lz = light_dir
    length = math.sqrt(lx*lx + ly*ly + lz*lz)
    lx, ly, lz = lx/length, ly/length, lz/length
    
    R = size // 2
    tex = texture_crop.resize((size, size), Image.Resampling.LANCZOS).convert("RGBA")
    tex_arr = np.array(tex).astype(np.float32)
    
    yy, xx = np.meshgrid(np.arange(size), np.arange(size), indexing='ij')
    dx = (xx - R) / float(R)
    dy = (yy - R) / float(R)
    r2 = dx*dx + dy*dy
    mask = r2 <= 1.0
    
    dz = np.zeros_like(r2)
    dz[mask] = np.sqrt(1.0 - r2[mask])
    
    dot = np.zeros_like(r2)
    dot[mask] = dx[mask] * lx + dy[mask] * ly + dz[mask] * lz
    diffuse = np.clip(dot, 0.0, 1.0)
    
    # Warm fill on unlit side from interplanetary dust scattering
    fill = np.clip(-dot, 0.0, 1.0) * 0.12
    
    illum = np.zeros_like(r2)
    illum[mask] = np.clip(ambient + (1.0 - ambient) * diffuse[mask] + fill[mask], 0.0, 1.0)
    
    # Limb atmospheric rim
    limb = np.zeros_like(r2)
    limb[mask] = (1.0 - dz[mask]) ** 2.2
    
    out_arr = np.zeros((size, size, 4), dtype=np.uint8)
    for c in range(3):
        col = tex_arr[:, :, c] * illum
        col += limb * limb_color[c] * limb_strength
        out_arr[:, :, c] = np.clip(col, 0, 255).astype(np.uint8)
        
    edge_dist = np.clip((1.0 - np.sqrt(np.maximum(0, r2))) * R * 1.5, 0.0, 1.0)
    out_arr[:, :, 3] = (mask * edge_dist * 255).astype(np.uint8)
    
    return Image.fromarray(out_arr, mode="RGBA")

# ==============================================================================
# SCENE 06: PLUTO EMBEDDED IN KUIPER BELT (CRITERION 3: FAILED CLEARING ORBIT)
# ==============================================================================
def make_scene_06():
    print("--- Rendering Perfect Scene 06: Failed Orbit Clearing ---")
    kuiper_master = Image.open("scratch/pluto_raw/0319_kuiper_belt_1.jpg").convert("RGB")
    kw, kh = kuiper_master.size
    
    # Crop containing Sun at (717, 958)
    crop_w = int(kh * 9 / 16) # 1500
    crop_x1 = 950
    crop = kuiper_master.crop((crop_x1, 0, crop_x1 + crop_w, kh))
    bg = crop.resize((W, H), Image.Resampling.LANCZOS)
    
    # Pluto placed at (x: 420, y: 550), diameter 420px
    # Distant Sun is at x=717, y=958
    pluto_raw = Image.open("scratch/pluto_raw/pluto_color_8k.jpg").convert("RGBA")
    pw, ph = pluto_raw.size
    pcx, pcy, prad = pw // 2, ph // 2, int(min(pw, ph) * 0.38)
    pluto_crop = pluto_raw.crop((pcx - prad, pcy - prad, pcx + prad, pcy + prad))
    
    pluto_sz = 420
    pluto_sphere = render_3d_sphere(
        pluto_crop, 
        size=pluto_sz, 
        light_dir=(0.7, 0.6, 0.45), # Towards Sun (down and right)
        ambient=0.25, # Rich visibility of Pluto's heart
        limb_color=(130, 200, 255), 
        limb_strength=0.35
    )
    
    # Atmospheric halo
    halo = Image.new("RGBA", (pluto_sz + 90, pluto_sz + 90), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hc = halo.width // 2
    for r in range(hc, pluto_sz // 2, -2):
        alpha = int(35 * (1.0 - (r - pluto_sz // 2) / (hc - pluto_sz // 2)))
        hd.ellipse([hc - r, hc - r, hc + r, hc + r], fill=(80, 150, 240, alpha))
        
    pluto_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px, py = 420, 550
    pluto_layer.paste(halo, (px - halo.width // 2, py - halo.height // 2), halo)
    pluto_layer.paste(pluto_sphere, (px - pluto_sz // 2, py - pluto_sz // 2), pluto_sphere)
    
    # Composite Pluto over background
    composed = Image.alpha_composite(bg.convert("RGBA"), pluto_layer)
    
    # Safe area vignette and polish
    final = apply_safe_area_vignette(composed.convert("RGB"), dark_start=1380)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = add_film_grain(final, intensity=4)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-06-three-criteria.png")
    final.save(out_path, "PNG")
    print(f"Master Scene 06 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

# ==============================================================================
# SCENE 07: PLUTO & CHARON AS BINARY KINGS OF THE KUIPER REALM
# ==============================================================================
def make_scene_07():
    print("--- Rendering Perfect Scene 07: King of Dwarf Planets ---")
    kuiper_master = Image.open("scratch/pluto_raw/0319_kuiper_belt_1.jpg").convert("RGB")
    kw, kh = kuiper_master.size
    
    # Left crop of Kuiper Belt showing sweeping disc of asteroids in deep perspective
    crop_w = int(kh * 9 / 16) # 1500
    crop_x1 = 200
    crop = kuiper_master.crop((crop_x1, 0, crop_x1 + crop_w, kh))
    bg = crop.resize((W, H), Image.Resampling.LANCZOS)
    
    # Pluto at x: 380, y: 500, size: 500px
    pluto_raw = Image.open("scratch/pluto_raw/pluto_color_8k.jpg").convert("RGBA")
    pw, ph = pluto_raw.size
    pcx, pcy, prad = pw // 2, ph // 2, int(min(pw, ph) * 0.38)
    pluto_crop = pluto_raw.crop((pcx - prad, pcy - prad, pcx + prad, pcy + prad))
    
    pluto_sz = 500
    pluto_sphere = render_3d_sphere(
        pluto_crop,
        size=pluto_sz,
        light_dir=(0.85, 0.15, 0.5), # From right, matching asteroid lighting
        ambient=0.24, # Rich visibility of Pluto's heart & terrain
        limb_color=(130, 200, 255),
        limb_strength=0.35
    )
    
    # Charon at x: 790, y: 360, size: 260px
    charon_raw = Image.open("scratch/pluto_raw/charon_true_color.jpg").convert("RGBA")
    cw, ch = charon_raw.size
    ccx, ccy, crad = cw // 2, ch // 2, int(min(cw, ch) * 0.38)
    charon_crop = charon_raw.crop((ccx - crad, ccy - crad, ccx + crad, ccy + crad))
    
    charon_sz = 260
    charon_sphere = render_3d_sphere(
        charon_crop,
        size=charon_sz,
        light_dir=(0.85, 0.15, 0.5), # Matching light direction
        ambient=0.24,
        limb_color=(140, 165, 190),
        limb_strength=0.18
    )
    
    # Halo for Pluto
    halo = Image.new("RGBA", (pluto_sz + 100, pluto_sz + 100), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hc = halo.width // 2
    for r in range(hc, pluto_sz // 2, -2):
        alpha = int(40 * (1.0 - (r - pluto_sz // 2) / (hc - pluto_sz // 2)))
        hd.ellipse([hc - r, hc - r, hc + r, hc + r], fill=(80, 150, 240, alpha))
        
    actors_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px, py = 380, 500
    actors_layer.paste(halo, (px - halo.width // 2, py - halo.height // 2), halo)
    actors_layer.paste(pluto_sphere, (px - pluto_sz // 2, py - pluto_sz // 2), pluto_sphere)
    
    cx, cy = 790, 360
    actors_layer.paste(charon_sphere, (cx - charon_sz // 2, cy - charon_sz // 2), charon_sphere)
    
    composed = Image.alpha_composite(bg.convert("RGBA"), actors_layer)
    
    # Safe area vignette
    final = apply_safe_area_vignette(composed.convert("RGB"), dark_start=1380)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = add_film_grain(final, intensity=4)
    
    out_path = os.path.join(OUTPUT_DIR, "scene-07-dwarf-planet-king.png")
    final.save(out_path, "PNG")
    print(f"Master Scene 07 saved: {out_path} ({os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    make_scene_06()
    make_scene_07()
