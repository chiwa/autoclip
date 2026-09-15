import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H = 1080, 1920

def test_scene_02():
    # Base: Rich dark wooden observatory interior with warm tungsten lighting
    base = Image.new("RGBA", (W, H), (10, 12, 18, 255))
    draw = ImageDraw.Draw(base)
    
    # 1. Upper background: Observatory dome slit opening to deep starry sky
    for y in range(0, 520):
        t = y / 520.0
        r = int(3 + 8 * (1 - t))
        g = int(6 + 10 * (1 - t))
        b = int(18 + 20 * (1 - t))
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    np.random.seed(1930)
    for _ in range(400):
        sx = np.random.randint(20, W - 20)
        sy = np.random.randint(15, 480)
        bright = np.random.randint(100, 255)
        sz = np.random.choice([1, 1, 1, 2, 2, 3], p=[0.7, 0.15, 0.08, 0.04, 0.02, 0.01])
        col = (bright, int(bright * 0.95), int(bright * 0.9), 230)
        if sz == 1:
            draw.point((sx, sy), fill=col)
        else:
            draw.ellipse([sx - sz, sy - sz, sx + sz, sy + sz], fill=col)
            
    # Curved observatory dome arch
    dome = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dome)
    # Left and right dome walls
    dd.polygon([(0, 0), (180, 0), (120, 520), (0, 520)], fill=(16, 18, 24, 255))
    dd.polygon([(W - 180, 0), (W, 0), (W, 520), (W - 120, 520)], fill=(16, 18, 24, 255))
    # Structural arches
    for y in [120, 280, 440]:
        dd.line([(0, y), (W, y)], fill=(32, 36, 48, 160), width=6)
        dd.line([(0, y+4), (W, y+4)], fill=(8, 10, 14, 200), width=3)
    dome = dome.filter(ImageFilter.GaussianBlur(2))
    base.paste(dome, (0, 0), dome)
    
    # 2. Hero Center: The Zeiss Blink Comparator (Clean & Prominent)
    # Load authentic zeiss comparator (2592x1936)
    zeiss = Image.open("scratch/pluto_raw/zeiss_comparator_1930.jpg").convert("RGBA")
    zw, zh = zeiss.size
    # Crop central comparator mechanism
    crop = zeiss.crop((int(zw * 0.08), int(zh * 0.02), int(zw * 0.92), int(zh * 0.96)))
    
    # Resize to fill midground (y: 420 to 1380)
    target_w = 1040
    target_h = int(crop.height * (target_w / crop.width))
    comp_res = crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Enrich colors: deep blacks, warm amber backlight on the glass plates
    r, g, b, a = comp_res.split()
    r = r.point(lambda p: min(255, int(p * 1.15)))
    g = g.point(lambda p: min(255, int(p * 1.02)))
    b = b.point(lambda p: min(255, int(p * 0.88))) # Warm tungsten vintage look
    comp_col = Image.merge("RGBA", (r, g, b, a))
    
    # Clean feathered mask for seamless blending
    c_mask = Image.new("L", comp_col.size, 255)
    cm_draw = ImageDraw.Draw(c_mask)
    for y in range(80):
        val = int(255 * (y / 80.0))
        cm_draw.line([(0, y), (target_w, y)], fill=val)
    for y in range(target_h - 100, target_h):
        val = int(255 * ((target_h - y) / 100.0))
        cm_draw.line([(0, y), (target_w, y)], fill=val)
        
    paste_y = 440
    base.paste(comp_col, ((W - target_w) // 2, paste_y), c_mask)
    
    # 3. Enhance the dual illuminated circular apertures with real discovery starfields
    plates_raw = Image.open("scratch/pluto_raw/pluto_discovery_plates.png").convert("RGBA")
    pw, ph = plates_raw.size
    p_left = plates_raw.crop((int(pw * 0.05), int(ph * 0.1), int(pw * 0.45), int(ph * 0.9))).resize((260, 260))
    p_right = plates_raw.crop((int(pw * 0.55), int(ph * 0.1), int(pw * 0.95), int(ph * 0.9))).resize((260, 260))
    
    # Circular apertures at left ~ (250, 780), right ~ (830, 780)
    # Mask to circles
    circ_mask = Image.new("L", (260, 260), 0)
    ImageDraw.Draw(circ_mask).ellipse([5, 5, 255, 255], fill=220)
    circ_mask = circ_mask.filter(ImageFilter.GaussianBlur(3))
    
    # Warm tone the plates
    pr, pg, pb, pa = p_left.split()
    pr = pr.point(lambda p: min(255, int(p * 1.2)))
    pg = pg.point(lambda p: min(255, int(p * 1.05)))
    pb = pb.point(lambda p: min(255, int(p * 0.85)))
    p_left_warm = Image.merge("RGBA", (pr, pg, pb, pa))
    
    pr2, pg2, pb2, pa2 = p_right.split()
    pr2 = pr2.point(lambda p: min(255, int(p * 1.2)))
    pg2 = pg2.point(lambda p: min(255, int(p * 1.05)))
    pb2 = pb2.point(lambda p: min(255, int(p * 0.85)))
    p_right_warm = Image.merge("RGBA", (pr2, pg2, pb2, pa2))
    
    # Glowing backlights behind the glass plates
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gl_draw = ImageDraw.Draw(glow_layer)
    for gr in range(180, 20, -12):
        alpha = int(50 * (1.0 - gr / 180.0) ** 1.5)
        gl_draw.ellipse([250 - gr, 780 - gr, 250 + gr, 780 + gr], fill=(255, 195, 80, alpha))
        gl_draw.ellipse([830 - gr, 780 - gr, 830 + gr, 780 + gr], fill=(255, 195, 80, alpha))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(12))
    base.paste(glow_layer, (0, 0), glow_layer)
    
    # Paste plates inside apertures with blending
    base.paste(p_left_warm, (250 - 130, 780 - 130), circ_mask)
    base.paste(p_right_warm, (830 - 130, 780 - 130), circ_mask)
    
    # 4. Foreground: Clyde's Mahogany Desk with vintage tools, star charts, warm brass lamp
    desk = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(desk)
    
    for y in range(1200, H):
        t = (y - 1200) / (H - 1200)
        # Deep lustrous mahogany wood tone fading to black
        mr = int((38 + 12 * math.sin(y * 0.05)) * (1.0 - t * 0.85))
        mg = int((20 + 8 * math.sin(y * 0.05)) * (1.0 - t * 0.85))
        mb = int((12 + 4 * math.sin(y * 0.05)) * (1.0 - t * 0.85))
        dd.line([(0, y), (W, y)], fill=(mr, mg, mb, 255))
        
    # Polished brass desk edge rail
    dd.line([(0, 1202), (W, 1202)], fill=(180, 140, 60, 220), width=3)
    dd.line([(0, 1205), (W, 1205)], fill=(80, 55, 20, 240), width=2)
    
    # Warm amber desk lamp lighting cone from lower right corner
    lamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lamp)
    for lr in range(550, 40, -20):
        alpha = int(40 * (1.0 - lr / 550.0) ** 1.3)
        ld.ellipse([920 - lr, int(1300 - lr * 0.6), 920 + lr, int(1300 + lr * 0.6)], fill=(255, 185, 75, alpha))
    lamp = lamp.filter(ImageFilter.GaussianBlur(30))
    desk.paste(lamp, (0, 0), lamp)
    
    base.paste(desk, (0, 0), desk)
    
    # 5. Clyde Tombaugh archival inset portrait on the left desk / observatory station
    clyde_raw = Image.open("scratch/pluto_raw/clyde_tombaugh.jpg").convert("RGBA")
    cw, ch = clyde_raw.size
    # Clyde looking up towards the stars / telescope
    c_face = clyde_raw.crop((int(cw * 0.4), int(ch * 0.22), int(cw * 0.85), int(ch * 0.58)))
    
    # Vintage tint Clyde
    c_gray = c_face.convert("L")
    c_arr = np.array(c_gray).astype(np.float32)
    cr = np.clip(c_arr * 1.15 + 20, 0, 255).astype(np.uint8)
    cg = np.clip(c_arr * 0.98 + 12, 0, 255).astype(np.uint8)
    cb = np.clip(c_arr * 0.78 + 5, 0, 255).astype(np.uint8)
    c_warm = Image.fromarray(np.stack([cr, cg, cb], axis=-1)).convert("RGBA")
    
    # Frame Clyde in a vintage brass oval vignette on the upper left (y: 200 - 450)
    c_warm_res = c_warm.resize((240, 290), Image.Resampling.LANCZOS)
    oval_mask = Image.new("L", (240, 290), 0)
    ImageDraw.Draw(oval_mask).ellipse([8, 8, 232, 282], fill=240)
    oval_mask = oval_mask.filter(ImageFilter.GaussianBlur(6))
    
    # Brass oval frame
    brass_frame = Image.new("RGBA", (250, 300), (0, 0, 0, 0))
    bf_draw = ImageDraw.Draw(brass_frame)
    bf_draw.ellipse([5, 5, 245, 295], outline=(185, 145, 70, 220), width=4)
    bf_draw.ellipse([8, 8, 242, 292], outline=(90, 65, 30, 200), width=2)
    
    clyde_inset = Image.new("RGBA", (250, 300), (0, 0, 0, 0))
    clyde_inset.paste(c_warm_res, (5, 5), oval_mask)
    clyde_inset.paste(brass_frame, (0, 0), brass_frame)
    
    # Subtle drop shadow behind Clyde portrait
    shadow = Image.new("RGBA", (270, 320), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([15, 15, 255, 305], fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    base.paste(shadow, (65, 175), shadow)
    base.paste(clyde_inset, (75, 185), clyde_inset)
    
    # 6. Apply safe area vignette (y: 1380 - 1920)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    for y in range(1340, H):
        factor = (y - 1340) / (H - 1340)
        alpha = int(230 * (factor ** 1.3))
        ov_draw.line([(0, y), (W, y)], fill=(4, 6, 12, alpha))
    final = Image.alpha_composite(base, overlay).convert("RGB")
    
    # 7. Cinematic grading & film grain
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = ImageEnhance.Color(final).enhance(1.05)
    
    arr = np.array(final).astype(np.float32)
    grain = np.random.normal(0, 8, arr.shape)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    final = Image.fromarray(arr)
    
    final.save("assets/pluto_demoted_reel/scene-02-discovery.png", "PNG")
    print("Scene 02 refined and saved!")

test_scene_02()
