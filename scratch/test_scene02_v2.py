import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H = 1080, 1920

def create_scene_02():
    # 1. Base canvas: Deep atmospheric observatory tones (charcoal navy & rich mahogany)
    base = Image.new("RGBA", (W, H), (8, 10, 16, 255))
    draw = ImageDraw.Draw(base)
    
    # Observatory background wall & dome architecture
    for y in range(H):
        t = y / H
        # Deep vintage vignette gradient
        r = int(6 + 8 * (1 - t) + 12 * (1 - abs(y - 700)/700))
        g = int(8 + 10 * (1 - t) + 10 * (1 - abs(y - 700)/700))
        b = int(16 + 18 * (1 - t) + 8 * (1 - abs(y - 700)/700))
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        
    # Subtle observatory slit opening at top (y: 0 to 420)
    for y in range(0, 420):
        t = y / 420.0
        draw.line([(180, y), (W - 180, y)], fill=(int(10 + 20*(1-t)), int(18 + 25*(1-t)), int(38 + 40*(1-t)), 255))
        
    np.random.seed(1930)
    for _ in range(250):
        sx = np.random.randint(190, W - 190)
        sy = np.random.randint(10, 390)
        b = np.random.randint(140, 255)
        sz = np.random.choice([1, 1, 2, 2, 3], p=[0.7, 0.2, 0.06, 0.03, 0.01])
        draw.ellipse([sx-sz, sy-sz, sx+sz, sy+sz], fill=(b, int(b*0.95), int(b*0.9), 240))
        
    # Dome frame arches
    arch = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(arch)
    ad.polygon([(0, 0), (180, 0), (150, 440), (0, 460)], fill=(12, 14, 20, 255))
    ad.polygon([(W - 180, 0), (W, 0), (W, 460), (W - 150, 440)], fill=(12, 14, 20, 255))
    for y in [100, 240, 380]:
        ad.line([(160, y), (W - 160, y)], fill=(45, 50, 65, 120), width=4)
    arch = arch.filter(ImageFilter.GaussianBlur(3))
    base.paste(arch, (0, 0), arch)
    
    # 2. Main Hero Subject: The Zeiss Blink Comparator from lowell_blink_comparator.jpg
    # This angle shows the glowing amber backlit circular aperture and brass eyepiece
    comp = Image.open("scratch/pluto_raw/lowell_blink_comparator.jpg").convert("RGBA")
    cw, ch = comp.size
    
    # Crop machine from top arched head down to just above the paper cards on the desk
    # x: 60 to 1860, y: 30 to 1540
    crop_m = comp.crop((int(cw * 0.03), int(ch * 0.01), int(cw * 0.96), int(ch * 0.69)))
    
    # Scale to fill width 1080
    scale = W / crop_m.width
    target_h = int(crop_m.height * scale)
    crop_res = crop_m.resize((W, target_h), Image.Resampling.LANCZOS)
    
    # Rich color grading: golden amber glow on the circular light, deep cast iron blacks
    cr, cg, cb, ca = crop_res.split()
    cr = cr.point(lambda p: min(255, int(p * 1.14)))
    cg = cg.point(lambda p: min(255, int(p * 1.02)))
    cb = cb.point(lambda p: min(255, int(p * 0.90)))
    comp_graded = Image.merge("RGBA", (cr, cg, cb, ca))
    
    # Feather top and bottom
    m_mask = Image.new("L", comp_graded.size, 255)
    md = ImageDraw.Draw(m_mask)
    for y in range(70):
        md.line([(0, y), (W, y)], fill=int(255 * (y / 70.0)))
    for y in range(target_h - 90, target_h):
        md.line([(0, y), (W, y)], fill=int(255 * ((target_h - y) / 90.0)))
        
    # Place machine at y: 280
    paste_y = 280
    base.paste(comp_graded, (0, paste_y), m_mask)
    
    # 3. Add glowing volumetric amber warmth to the comparator light source
    # The glowing amber circle is at roughly x: 330, y: 280 + 580 = 860
    light_x, light_y = 330, 860
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for gr in range(260, 30, -15):
        alpha = int(45 * (1.0 - gr / 260.0) ** 1.6)
        gd.ellipse([light_x - gr, light_y - gr, light_x + gr, light_y + gr], fill=(255, 190, 70, alpha))
    # Warm beam across the eyepiece (from x: 330 toward eyepiece at x: 800)
    for w in range(120, 10, -10):
        alpha = int(25 * (1.0 - w / 120.0))
        gd.line([(light_x + 50, light_y), (820, 780)], fill=(255, 210, 110, alpha), width=w)
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    base.paste(glow, (0, 0), glow)
    
    # 4. Foreground: Rich mahogany observatory desk (y: 1180 to 1920)
    desk = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(desk)
    for y in range(1180, H):
        t = (y - 1180) / (H - 1180)
        mr = int((42 + 10 * math.sin(y * 0.04)) * (1.0 - t * 0.88))
        mg = int((24 + 6 * math.sin(y * 0.04)) * (1.0 - t * 0.88))
        mb = int((14 + 4 * math.sin(y * 0.04)) * (1.0 - t * 0.88))
        dd.line([(0, y), (W, y)], fill=(mr, mg, mb, 255))
        
    # Brass rail on desk edge
    dd.line([(0, 1182), (W, 1182)], fill=(175, 135, 60, 200), width=3)
    dd.line([(0, 1185), (W, 1185)], fill=(70, 50, 20, 220), width=2)
    
    # Atmospheric warm light pool on desk
    desk_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dgd = ImageDraw.Draw(desk_glow)
    for r in range(480, 40, -20):
        alpha = int(35 * (1.0 - r / 480.0))
        dgd.ellipse([420 - r, int(1280 - r * 0.5), 420 + r, int(1280 + r * 0.5)], fill=(255, 180, 70, alpha))
    desk_glow = desk_glow.filter(ImageFilter.GaussianBlur(25))
    desk.paste(desk_glow, (0, 0), desk_glow)
    base.paste(desk, (0, 0), desk)
    
    # 5. Safe Area Vignette (y: 1380 - 1920)
    final = base.convert("RGB")
    final_v = apply_safe_area_vignette(final, dark_start=1330)
    
    # 6. Photographic film grain & enhancement
    final_v = ImageEnhance.Contrast(final_v).enhance(1.10)
    final_v = ImageEnhance.Color(final_v).enhance(1.08)
    
    arr = np.array(final_v).astype(np.float32)
    grain = np.random.normal(0, 8, arr.shape)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    res = Image.fromarray(arr)
    
    res.save("assets/pluto_demoted_reel/scene-02-discovery.png", "PNG")
    print("Scene 02 lowell comparator version saved!")

def apply_safe_area_vignette(img, dark_start=1350):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(dark_start, H):
        factor = (y - dark_start) / (H - dark_start)
        alpha = int(235 * (factor ** 1.3))
        draw.line([(0, y), (W, y)], fill=(3, 5, 10, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

create_scene_02()
