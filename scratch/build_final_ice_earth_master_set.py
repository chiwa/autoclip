import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np

TARGET_W = 1080
TARGET_H = 1920

ROOT_DIR = Path("/Users/zengcode/projects/autoclip")
RAW_DIR = ROOT_DIR / "scratch/ice_raw"
PBD_RAW_DIR = ROOT_DIR / "scratch/pale_blue_dot_raw"
OUTPUT_DIR = ROOT_DIR / "assets/ice-cold-earth"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc"
f_topic = ImageFont.truetype(FONT_PATH, 44, index=5)
f_hook = ImageFont.truetype(FONT_PATH, 72, index=5)

def draw_styled_text(cv, text, font, pos, fill_color, shadow_blur=16, shadow_offset=(0,6), shadow_color=(0,0,0,240)):
    ol = Image.new('RGBA', cv.size, (0,0,0,0))
    ImageDraw.Draw(ol).text((pos[0]+shadow_offset[0], pos[1]+shadow_offset[1]), text, font=font, fill=shadow_color, stroke_width=6, stroke_fill=shadow_color)
    cv.alpha_composite(ol.filter(ImageFilter.GaussianBlur(shadow_blur)))
    fg = Image.new('RGBA', cv.size, (0,0,0,0))
    ImageDraw.Draw(fg).text(pos, text, font=font, fill=fill_color)
    cv.alpha_composite(fg)

def apply_safe_vignette(img, fade_len=380, min_factor=0.35):
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape[:2]
    factor = np.linspace(1.0, min_factor, fade_len)[:, None, None]
    arr[h - fade_len:, :, :3] *= factor
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

# ==========================================
# SCENE 01: Narrative Key Art (Hook)
# ==========================================
def build_scene_01():
    print("Building Scene 01 (Key Art / Hook)...")
    canvas = Image.new('RGBA', (TARGET_W, TARGET_H), (4, 7, 20, 255))
    neb = Image.new('RGBA', (TARGET_W, TARGET_H), (0,0,0,0))
    nd = ImageDraw.Draw(neb)
    np.random.seed(101)
    for _ in range(16):
        nx = np.random.randint(50, TARGET_W - 50)
        ny = np.random.randint(100, TARGET_H - 100)
        nr = np.random.randint(300, 600)
        col = (np.random.randint(15, 45), np.random.randint(25, 65), np.random.randint(75, 140), np.random.randint(35, 75))
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=col)
    canvas.alpha_composite(neb.filter(ImageFilter.GaussianBlur(100)))

    sd = ImageDraw.Draw(canvas)
    for _ in range(550):
        x = np.random.randint(0, TARGET_W)
        y = np.random.randint(0, TARGET_H)
        b = np.random.randint(140, 255)
        r = 1 if np.random.rand() > 0.1 else 2
        col = (255, 215, 170, b) if np.random.rand() > 0.8 else (185, 225, 255, b)
        sd.ellipse([x, y, x + r, y + r], fill=col)

    # Orange host star in upper right
    star_raw = Image.open(RAW_DIR / "orange_dwarf.png").convert('RGBA')
    star_sz = 340
    star_res = star_raw.resize((star_sz, star_sz), Image.Resampling.LANCZOS)
    y_idx, x_idx = np.ogrid[:star_sz, :star_sz]
    rad = star_sz / 2.0
    dist = np.sqrt((x_idx - rad)**2 + (y_idx - rad)**2)
    fade = np.clip(1.0 - (dist - rad*0.82) / (rad*0.18), 0.0, 1.0)
    star_res.putalpha(Image.fromarray((fade * 255).astype(np.uint8)))

    sglow = Image.new('RGBA', (star_sz + 200, star_sz + 200), (0,0,0,0))
    ImageDraw.Draw(sglow).ellipse([40, 40, star_sz + 160, star_sz + 160], fill=(255, 140, 30, 110))
    sglow = sglow.filter(ImageFilter.GaussianBlur(45))

    sx, sy = TARGET_W - star_sz + 30, 120
    canvas.alpha_composite(sglow, (sx - 100, sy - 100))
    canvas.alpha_composite(star_res, (sx, sy))

    # Ice planet in upper-left/center: sz 960
    planet_sz = 960
    raw_p = Image.open(RAW_DIR / "frozen_planet.png").convert('RGBA')
    cx_p, cy_p, r_p = 3843, 3155, 2430
    cropped_p = raw_p.crop((cx_p - r_p, cy_p - r_p, cx_p + r_p, cy_p + r_p)).rotate(180, resample=Image.Resampling.BICUBIC)
    planet_res = cropped_p.resize((planet_sz, planet_sz), Image.Resampling.LANCZOS)
    p_mask = Image.new('L', (planet_sz, planet_sz), 0)
    ImageDraw.Draw(p_mask).ellipse([3, 3, planet_sz - 3, planet_sz - 3], fill=255)
    planet_res.putalpha(p_mask.filter(ImageFilter.GaussianBlur(2.0)))

    # Atmospheric crescent glow along top-right limb (facing star)
    pglow = Image.new('RGBA', (planet_sz + 140, planet_sz + 140), (0,0,0,0))
    pg_cx, pg_cy = (planet_sz + 140)//2, (planet_sz + 140)//2
    pgr = planet_sz // 2 + 6
    for w_val, alpha in [(30, 45), (16, 85), (6, 150)]:
        ImageDraw.Draw(pglow).arc([pg_cx - pgr - w_val//2, pg_cy - pgr - w_val//2, 
                                   pg_cx + pgr + w_val//2, pg_cy + pgr + w_val//2],
                                  start=-80, end=70, fill=(85, 210, 255, alpha), width=w_val)
    pglow = pglow.filter(ImageFilter.GaussianBlur(18))

    px, py = -100, 260
    canvas.alpha_composite(pglow, (px - 70, py - 70))
    canvas.alpha_composite(planet_res, (px, py))

    # Mamase presenter on right
    cutout = Image.open(ROOT_DIR / 'scratch/mamase_presenter_cutout.png').convert('RGBA')
    alpha = np.array(cutout.split()[-1])
    y_i, x_i = np.where(alpha > 10)
    presenter_cropped = cutout.crop((x_i.min(), y_i.min(), x_i.max() + 1, y_i.max() + 1))
    target_hp = 1290
    scale_p = target_hp / presenter_cropped.height
    target_wp = int(presenter_cropped.width * scale_p)
    presenter_fit = presenter_cropped.resize((target_wp, target_hp), Image.Resampling.LANCZOS)

    # Rim lighting on presenter
    p_arr = np.array(presenter_fit, dtype=np.float32)
    rim_w = int(target_wp * 0.22)
    rim_grad = np.linspace(1.0, 0.0, rim_w)[None, :, None]
    p_arr[:, :rim_w, 2] = np.clip(p_arr[:, :rim_w, 2] + 35 * rim_grad[:, :, 0], 0, 255)
    p_arr[:, :rim_w, 1] = np.clip(p_arr[:, :rim_w, 1] + 20 * rim_grad[:, :, 0], 0, 255)
    presenter_final = Image.fromarray(p_arr.astype(np.uint8))

    pos_px = TARGET_W - target_wp + 40
    pos_py = TARGET_H - target_hp
    canvas.alpha_composite(presenter_final, (pos_px, pos_py))

    tx, ty = 70, 95
    draw_styled_text(canvas, 'โลกอีกใบ', f_topic, (tx, ty), fill_color=(255, 214, 102, 255), shadow_blur=16)
    hy = ty + 68
    draw_styled_text(canvas, 'โลกอีกใบที่อาจ...\nเย็นจนตาย?', f_hook, (tx, hy), fill_color=(255, 255, 255, 255), shadow_blur=20)

    out = apply_safe_vignette(canvas)
    out.save(OUTPUT_DIR / "scene-01-hook.png")
    print("Scene 01 saved!")

# ==========================================
# SCENE 02: Kepler Transit Detection
# ==========================================
def build_scene_02():
    print("Building Scene 02 (Kepler Transit Detection)...")
    bg = Image.new('RGBA', (TARGET_W, TARGET_H), (4, 7, 20, 255))
    neb = Image.new('RGBA', (TARGET_W, TARGET_H), (0,0,0,0))
    nd = ImageDraw.Draw(neb)
    np.random.seed(202)
    for _ in range(16):
        nx = np.random.randint(50, TARGET_W - 50)
        ny = np.random.randint(100, TARGET_H - 100)
        nr = np.random.randint(250, 550)
        col = (np.random.randint(20, 50), np.random.randint(25, 65), np.random.randint(70, 135), np.random.randint(35, 75))
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=col)
    bg.alpha_composite(neb.filter(ImageFilter.GaussianBlur(90)))

    sd = ImageDraw.Draw(bg)
    for _ in range(600):
        x = np.random.randint(0, TARGET_W)
        y = np.random.randint(0, TARGET_H)
        b = np.random.randint(140, 255)
        r = 1 if np.random.rand() > 0.1 else 2
        col = (255, 210, 160, b) if np.random.rand() > 0.8 else (180, 220, 255, b)
        sd.ellipse([x, y, x + r, y + r], fill=col)

    # Orange host star HD 137010 in upper right
    star_raw = Image.open(RAW_DIR / "orange_dwarf.png").convert('RGBA')
    star_sz = 440
    star_res = star_raw.resize((star_sz, star_sz), Image.Resampling.LANCZOS)
    y_idx, x_idx = np.ogrid[:star_sz, :star_sz]
    rad = star_sz / 2.0
    dist = np.sqrt((x_idx - rad)**2 + (y_idx - rad)**2)
    fade = np.clip(1.0 - (dist - rad*0.8) / (rad*0.2), 0.0, 1.0)
    star_res.putalpha(Image.fromarray((fade * 255).astype(np.uint8)))

    # Transit silhouette dot
    st_draw = ImageDraw.Draw(star_res)
    tcx, tcy = int(star_sz * 0.48), int(star_sz * 0.52)
    tr = 15
    st_draw.ellipse([tcx - tr, tcy - tr, tcx + tr, tcy + tr], fill=(12, 14, 22, 255))

    sglow = Image.new('RGBA', (star_sz + 220, star_sz + 220), (0,0,0,0))
    ImageDraw.Draw(sglow).ellipse([40, 40, star_sz + 180, star_sz + 180], fill=(255, 140, 30, 110))
    sglow = sglow.filter(ImageFilter.GaussianBlur(50))

    sx, sy = TARGET_W - star_sz - 40, 130
    bg.alpha_composite(sglow, (sx - 110, sy - 110))
    bg.alpha_composite(star_res, (sx, sy))

    # Kepler telescope
    kepler = Image.open(RAW_DIR / "kepler_clean_cutout.png").convert('RGBA')
    kw_target = 680
    kh_target = int(kepler.height * kw_target / kepler.width)
    kepler_fit = kepler.resize((kw_target, kh_target), Image.Resampling.LANCZOS)
    kepler_rot = kepler_fit.rotate(14, resample=Image.Resampling.BICUBIC, expand=True)

    kx = 80
    ky = 680
    bg.alpha_composite(kepler_rot, (kx, ky))

    out = apply_safe_vignette(bg)
    out.save(OUTPUT_DIR / "scene-02-kepler-transit.png")
    print("Scene 02 saved!")

# ==========================================
# SCENE 03: Twin Comparison (Earth vs HD 137010 b)
# ==========================================
def build_scene_03():
    print("Building Scene 03 (Twin Comparison)...")
    canvas = Image.new('RGBA', (TARGET_W, TARGET_H), (4, 7, 20, 255))
    neb = Image.new('RGBA', (TARGET_W, TARGET_H), (0,0,0,0))
    nd = ImageDraw.Draw(neb)
    np.random.seed(303)
    for _ in range(18):
        nx = np.random.randint(50, TARGET_W - 50)
        ny = np.random.randint(100, TARGET_H - 100)
        nr = np.random.randint(300, 600)
        col = (np.random.randint(15, 45), np.random.randint(25, 65), np.random.randint(75, 140), np.random.randint(35, 75))
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=col)
    canvas.alpha_composite(neb.filter(ImageFilter.GaussianBlur(100)))

    sd = ImageDraw.Draw(canvas)
    for _ in range(700):
        x = np.random.randint(0, TARGET_W)
        y = np.random.randint(0, TARGET_H)
        b = np.random.randint(140, 255)
        r = 1 if np.random.rand() > 0.1 else 2
        col = (255, 215, 170, b) if np.random.rand() > 0.8 else (185, 225, 255, b)
        sd.ellipse([x, y, x + r, y + r], fill=col)

    # Earth at upper left (size 620)
    raw_earth = Image.open(RAW_DIR / "earth_blue_marble.jpg").convert('RGBA')
    earth_crop = raw_earth.crop((151, 151, 3557, 3572))
    sq = min(earth_crop.width, earth_crop.height)
    cx, cy = earth_crop.width // 2, earth_crop.height // 2
    earth_sq = earth_crop.crop((cx - sq//2, cy - sq//2, cx + sq//2, cy + sq//2))
    earth_sz = 620
    earth_res = earth_sq.resize((earth_sz, earth_sz), Image.Resampling.LANCZOS)
    e_mask = Image.new('L', (earth_sz, earth_sz), 0)
    ImageDraw.Draw(e_mask).ellipse([3, 3, earth_sz - 3, earth_sz - 3], fill=255)
    earth_res.putalpha(e_mask.filter(ImageFilter.GaussianBlur(2.0)))

    eglow = Image.new('RGBA', (earth_sz + 140, earth_sz + 140), (0,0,0,0))
    ImageDraw.Draw(eglow).ellipse([35, 35, earth_sz + 105, earth_sz + 105], fill=(50, 140, 255, 85))
    eglow = eglow.filter(ImageFilter.GaussianBlur(30))

    ex, ey = 50, 160
    canvas.alpha_composite(eglow, (ex - 70, ey - 70))
    canvas.alpha_composite(earth_res, (ex, ey))

    # HD 137010 b at lower right (size 657)
    ice_sz = int(earth_sz * 1.06)
    raw_p = Image.open(RAW_DIR / "frozen_planet.png").convert('RGBA')
    cx_p, cy_p, r_p = 3843, 3155, 2430
    cropped_p = raw_p.crop((cx_p - r_p, cy_p - r_p, cx_p + r_p, cy_p + r_p)).rotate(180, resample=Image.Resampling.BICUBIC)
    ice_res = cropped_p.resize((ice_sz, ice_sz), Image.Resampling.LANCZOS)
    p_mask = Image.new('L', (ice_sz, ice_sz), 0)
    ImageDraw.Draw(p_mask).ellipse([3, 3, ice_sz - 3, ice_sz - 3], fill=255)
    ice_res.putalpha(p_mask.filter(ImageFilter.GaussianBlur(2.0)))

    iglow = Image.new('RGBA', (ice_sz + 140, ice_sz + 140), (0,0,0,0))
    ig_cx, ig_cy = (ice_sz + 140)//2, (ice_sz + 140)//2
    igr = ice_sz // 2 + 6
    for w_val, alpha in [(30, 45), (16, 85), (6, 150)]:
        ImageDraw.Draw(iglow).arc([ig_cx - igr - w_val//2, ig_cy - igr - w_val//2, 
                                   ig_cx + igr + w_val//2, ig_cy + igr + w_val//2],
                                  start=-90, end=60, fill=(85, 210, 255, alpha), width=w_val)
    iglow = iglow.filter(ImageFilter.GaussianBlur(18))

    ix, iy = TARGET_W - ice_sz - 40, 840
    canvas.alpha_composite(iglow, (ix - 70, iy - 70))
    canvas.alpha_composite(ice_res, (ix, iy))

    out = apply_safe_vignette(canvas)
    out.save(OUTPUT_DIR / "scene-03-twin-comparison.png")
    print("Scene 03 saved!")

# ==========================================
# SCENE 04: Dim Host Star (Orange Dwarf)
# ==========================================
def build_scene_04():
    print("Building Scene 04 (Dim Host Star)...")
    canvas = Image.new('RGBA', (TARGET_W, TARGET_H), (4, 7, 20, 255))
    neb = Image.new('RGBA', (TARGET_W, TARGET_H), (0,0,0,0))
    nd = ImageDraw.Draw(neb)
    np.random.seed(404)
    for _ in range(18):
        nx = np.random.randint(50, TARGET_W - 50)
        ny = np.random.randint(100, TARGET_H - 100)
        nr = np.random.randint(300, 600)
        col = (np.random.randint(18, 50), np.random.randint(28, 65), np.random.randint(75, 140), np.random.randint(35, 75))
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=col)
    canvas.alpha_composite(neb.filter(ImageFilter.GaussianBlur(100)))

    sd = ImageDraw.Draw(canvas)
    for _ in range(650):
        x = np.random.randint(0, TARGET_W)
        y = np.random.randint(0, TARGET_H)
        b = np.random.randint(140, 255)
        r = 1 if np.random.rand() > 0.1 else 2
        col = (255, 215, 170, b) if np.random.rand() > 0.8 else (185, 225, 255, b)
        sd.ellipse([x, y, x + r, y + r], fill=col)

    # Huge Orange Dwarf at top
    star_sz = 860
    star_raw = Image.open(RAW_DIR / "orange_dwarf.png").convert('RGBA')
    star_res = star_raw.resize((star_sz, star_sz), Image.Resampling.LANCZOS)
    y_idx, x_idx = np.ogrid[:star_sz, :star_sz]
    rad = star_sz / 2.0
    dist = np.sqrt((x_idx - rad)**2 + (y_idx - rad)**2)
    fade = np.clip(1.0 - (dist - rad*0.82) / (rad*0.18), 0.0, 1.0)
    star_res.putalpha(Image.fromarray((fade * 255).astype(np.uint8)))

    sglow = Image.new('RGBA', (star_sz + 300, star_sz + 300), (0,0,0,0))
    ImageDraw.Draw(sglow).ellipse([40, 40, star_sz + 260, star_sz + 260], fill=(255, 130, 25, 120))
    sglow = sglow.filter(ImageFilter.GaussianBlur(65))

    sx, sy = (TARGET_W - star_sz)//2, -160
    canvas.alpha_composite(sglow, (sx - 150, sy - 150))
    canvas.alpha_composite(star_res, (sx, sy))

    # HD 137010 b below (size 980)
    planet_sz = 980
    raw_p = Image.open(RAW_DIR / "frozen_planet.png").convert('RGBA')
    cx_p, cy_p, r_p = 3843, 3155, 2430
    cropped_p = raw_p.crop((cx_p - r_p, cy_p - r_p, cx_p + r_p, cy_p + r_p)).rotate(270, resample=Image.Resampling.BICUBIC)
    planet_res = cropped_p.resize((planet_sz, planet_sz), Image.Resampling.LANCZOS)
    p_mask = Image.new('L', (planet_sz, planet_sz), 0)
    ImageDraw.Draw(p_mask).ellipse([3, 3, planet_sz - 3, planet_sz - 3], fill=255)
    planet_res.putalpha(p_mask.filter(ImageFilter.GaussianBlur(2.0)))

    p_arr = np.array(planet_res, dtype=np.float32)
    y_coords, x_coords = np.ogrid[:planet_sz, :planet_sz]
    illum = np.clip(1.0 - (y_coords / (planet_sz * 0.85)) * 0.65, 0.35, 1.0)[:, :, None]
    p_arr[:, :, :3] *= illum

    amber_tint = np.clip(1.0 - y_coords / (planet_sz * 0.40), 0.0, 1.0)[:, :, None]
    p_arr[:, :, 0] = np.clip(p_arr[:, :, 0] + 60 * amber_tint[:, :, 0], 0, 255)
    p_arr[:, :, 1] = np.clip(p_arr[:, :, 1] + 30 * amber_tint[:, :, 0], 0, 255)
    planet_lit = Image.fromarray(np.clip(p_arr, 0, 255).astype(np.uint8))

    rglow = Image.new('RGBA', (planet_sz + 140, planet_sz + 140), (0,0,0,0))
    rg_cx, rg_cy = (planet_sz + 140)//2, (planet_sz + 140)//2
    rgr = planet_sz // 2 + 6
    for w_val, alpha in [(35, 50), (18, 90), (6, 160)]:
        ImageDraw.Draw(rglow).arc([rg_cx - rgr - w_val//2, rg_cy - rgr - w_val//2, 
                                   rg_cx + rgr + w_val//2, rg_cy + rgr + w_val//2],
                                  start=-160, end=-20, fill=(255, 175, 75, alpha), width=w_val)
    rglow = rglow.filter(ImageFilter.GaussianBlur(18))

    px, py = (TARGET_W - planet_sz)//2, 740
    canvas.alpha_composite(rglow, (px - 70, py - 70))
    canvas.alpha_composite(planet_lit, (px, py))

    out = apply_safe_vignette(canvas)
    out.save(OUTPUT_DIR / "scene-04-dim-orange-star.png")
    print("Scene 04 saved!")

# ==========================================
# SCENE 05: Deep Freeze Surface
# ==========================================
def build_scene_05():
    print("Building Scene 05 (Deep Freeze Surface)...")
    glacier_raw = Image.open(RAW_DIR / 'glacier_ice.jpg').convert('RGBA')
    horizon_y = 700
    gh_target = TARGET_H - horizon_y
    gw_target = int(glacier_raw.width * gh_target / glacier_raw.height)
    glacier_scaled = glacier_raw.resize((gw_target, gh_target), Image.Resampling.LANCZOS)
    gx_crop = (gw_target - TARGET_W) // 2
    glacier_crop = glacier_scaled.crop((gx_crop, 0, gx_crop + TARGET_W, gh_target))

    g_arr = np.array(glacier_crop, dtype=np.float32)
    g_arr[:, :, 0] *= 0.82
    g_arr[:, :, 1] *= 0.95
    g_arr[:, :, 2] = np.clip(g_arr[:, :, 2] * 1.10, 0, 255)
    fade_h = 90
    horizon_alpha = np.linspace(0.0, 1.0, fade_h)[:, None]
    g_arr[:fade_h, :, 3] *= horizon_alpha
    glacier_graded = Image.fromarray(np.clip(g_arr, 0, 255).astype(np.uint8))

    canvas = Image.new('RGBA', (TARGET_W, TARGET_H), (4, 7, 20, 255))
    neb = Image.new('RGBA', (TARGET_W, horizon_y + 100), (0,0,0,0))
    nd = ImageDraw.Draw(neb)
    np.random.seed(505)
    for _ in range(16):
        nx = np.random.randint(50, TARGET_W - 50)
        ny = np.random.randint(50, horizon_y - 50)
        nr = np.random.randint(200, 450)
        col = (np.random.randint(20, 50), np.random.randint(25, 60), np.random.randint(70, 130), np.random.randint(30, 70))
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=col)
    canvas.alpha_composite(neb.filter(ImageFilter.GaussianBlur(80)))

    sd = ImageDraw.Draw(canvas)
    for _ in range(350):
        x = np.random.randint(0, TARGET_W)
        y = np.random.randint(0, horizon_y - 20)
        b = np.random.randint(140, 255)
        r = 1 if np.random.rand() > 0.1 else 2
        col = (255, 215, 170, b) if np.random.rand() > 0.8 else (185, 225, 255, b)
        sd.ellipse([x, y, x + r, y + r], fill=col)

    # Star and smooth radial glow
    star_raw = Image.open(RAW_DIR / "orange_dwarf.png").convert('RGBA')
    star_sz = 340
    star_res = star_raw.resize((star_sz, star_sz), Image.Resampling.LANCZOS)
    y_idx, x_idx = np.ogrid[:star_sz, :star_sz]
    rad = star_sz / 2.0
    dist = np.sqrt((x_idx - rad)**2 + (y_idx - rad)**2)
    fade = np.clip(1.0 - (dist - rad*0.82) / (rad*0.18), 0.0, 1.0)
    star_res.putalpha(Image.fromarray((fade * 255).astype(np.uint8)))

    scx, scy = 700, horizon_y - 40
    y_all, x_all = np.ogrid[:TARGET_H, :TARGET_W]
    dist_star = np.sqrt((x_all - scx)**2 + (y_all - scy)**2)
    glow_intensity = np.exp(-dist_star / 110.0) * 160.0
    c_arr = np.array(canvas, dtype=np.float32)
    c_arr[:, :, 0] = np.clip(c_arr[:, :, 0] + glow_intensity * 1.0, 0, 255)
    c_arr[:, :, 1] = np.clip(c_arr[:, :, 1] + glow_intensity * 0.55, 0, 255)
    c_arr[:, :, 2] = np.clip(c_arr[:, :, 2] + glow_intensity * 0.15, 0, 255)
    canvas = Image.fromarray(c_arr.astype(np.uint8))

    canvas.alpha_composite(star_res, (scx - star_sz//2, scy - star_sz//2))
    canvas.alpha_composite(glacier_graded, (0, horizon_y))

    # Sunlight glint on ice surface
    glint_layer = Image.new('RGBA', (TARGET_W, gh_target), (0,0,0,0))
    gld = ImageDraw.Draw(glint_layer)
    gld.ellipse([scx - 220, -60, scx + 220, 220], fill=(255, 175, 65, 75))
    canvas.alpha_composite(glint_layer.filter(ImageFilter.GaussianBlur(35)), (0, horizon_y))

    # Atmospheric frost mist along horizon
    mist = Image.new('RGBA', (TARGET_W, 180), (0,0,0,0))
    ImageDraw.Draw(mist).rectangle([0, 40, TARGET_W, 140], fill=(180, 220, 255, 38))
    canvas.alpha_composite(mist.filter(ImageFilter.GaussianBlur(25)), (0, horizon_y - 90))

    out = apply_safe_vignette(canvas)
    out.save(OUTPUT_DIR / "scene-05-deep-freeze-surface.png")
    print("Scene 05 saved!")

# ==========================================
# SCENE 06: Habitable Zone Outer Edge
# ==========================================
def build_scene_06():
    print("Building Scene 06 (Habitable Zone Outer Edge)...")
    canvas = Image.new('RGBA', (TARGET_W, TARGET_H), (4, 7, 20, 255))
    neb = Image.new('RGBA', (TARGET_W, TARGET_H), (0,0,0,0))
    nd = ImageDraw.Draw(neb)
    np.random.seed(606)

    for _ in range(12):
        nx = np.random.randint(50, TARGET_W - 50)
        ny = np.random.randint(50, 700)
        nr = np.random.randint(250, 500)
        col = (np.random.randint(25, 60), np.random.randint(35, 75), np.random.randint(80, 150), np.random.randint(40, 80))
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=col)

    for _ in range(20):
        nx = np.random.randint(50, TARGET_W - 50)
        ny = np.random.randint(700, 1850)
        nr = np.random.randint(280, 600)
        col = (np.random.randint(18, 48), np.random.randint(28, 68), np.random.randint(75, 135), np.random.randint(35, 75))
        nd.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=col)

    canvas.alpha_composite(neb.filter(ImageFilter.GaussianBlur(100)))

    sd = ImageDraw.Draw(canvas)
    for _ in range(850):
        x = np.random.randint(0, TARGET_W)
        y = np.random.randint(0, TARGET_H)
        b = np.random.randint(140, 255)
        r = 1 if np.random.rand() > 0.08 else 2
        col = (255, 215, 170, b) if np.random.rand() > 0.75 else (185, 225, 255, b)
        sd.ellipse([x, y, x + r, y + r], fill=col)

    # Host star at upper center
    scx, scy = 540, 360
    star_sz = 340
    star_raw = Image.open(RAW_DIR / "orange_dwarf.png").convert('RGBA')
    star_res = star_raw.resize((star_sz, star_sz), Image.Resampling.LANCZOS)
    y_idx, x_idx = np.ogrid[:star_sz, :star_sz]
    rad = star_sz / 2.0
    dist = np.sqrt((x_idx - rad)**2 + (y_idx - rad)**2)
    fade = np.clip(1.0 - (dist - rad*0.82) / (rad*0.18), 0.0, 1.0)
    star_res.putalpha(Image.fromarray((fade * 255).astype(np.uint8)))

    y_all, x_all = np.ogrid[:TARGET_H, :TARGET_W]
    dist_s = np.sqrt((x_all - scx)**2 + (y_all - scy)**2)
    s_glow = np.exp(-dist_s / 130.0) * 170.0
    c_arr = np.array(canvas, dtype=np.float32)
    c_arr[:, :, 0] = np.clip(c_arr[:, :, 0] + s_glow * 1.0, 0, 255)
    c_arr[:, :, 1] = np.clip(c_arr[:, :, 1] + s_glow * 0.55, 0, 255)
    c_arr[:, :, 2] = np.clip(c_arr[:, :, 2] + s_glow * 0.15, 0, 255)
    canvas = Image.fromarray(c_arr.astype(np.uint8))

    # Volumetric Habitable Zone Belt
    hz_layer = Image.new('RGBA', (TARGET_W, TARGET_H), (0,0,0,0))
    hzd = ImageDraw.Draw(hz_layer)
    tilt = 0.78
    for rx in range(560, 980, 8):
        ry = int(rx * tilt)
        rel = 1.0 - abs(rx - 770) / 210.0
        alpha = int(22 + rel * 40)
        col = (45, 185, 165, alpha) if rx < 770 else (35, 145, 230, alpha)
        hzd.ellipse([scx - rx, scy - ry, scx + rx, scy + ry], outline=col, width=9)

    # Orbit line of HD 137010 b (outer edge = 960)
    p_rx = 960
    p_ry = int(p_rx * tilt)
    hzd.ellipse([scx - p_rx, scy - p_ry, scx + p_rx, scy + p_ry], outline=(100, 200, 255, 95), width=3)

    canvas.alpha_composite(hz_layer.filter(ImageFilter.GaussianBlur(12)))
    canvas.alpha_composite(star_res, (scx - star_sz//2, scy - star_sz//2))

    # HD 137010 b positioned on outer edge
    planet_x, planet_y = 640, 1080
    planet_sz = 680
    raw_p = Image.open(RAW_DIR / "frozen_planet.png").convert('RGBA')
    cx_p, cy_p, r_p = 3843, 3155, 2430
    cropped_p = raw_p.crop((cx_p - r_p, cy_p - r_p, cx_p + r_p, cy_p + r_p)).rotate(180, resample=Image.Resampling.BICUBIC)
    planet_res = cropped_p.resize((planet_sz, planet_sz), Image.Resampling.LANCZOS)
    p_mask = Image.new('L', (planet_sz, planet_sz), 0)
    ImageDraw.Draw(p_mask).ellipse([3, 3, planet_sz - 3, planet_sz - 3], fill=255)
    planet_res.putalpha(p_mask.filter(ImageFilter.GaussianBlur(2.0)))

    p_arr = np.array(planet_res, dtype=np.float32)
    y_c, x_c = np.ogrid[:planet_sz, :planet_sz]
    norm_dist = ((x_c / planet_sz) * 0.3 + (y_c / planet_sz) * 0.7)
    illum = np.clip(1.0 - norm_dist * 0.65, 0.32, 1.0)[:, :, None]
    p_arr[:, :, :3] *= illum

    top_left_fac = np.clip(1.0 - (x_c*0.4 + y_c*0.6) / (planet_sz * 0.4), 0.0, 1.0)[:, :, None]
    p_arr[:, :, 0] = np.clip(p_arr[:, :, 0] + 55 * top_left_fac[:, :, 0], 0, 255)
    p_arr[:, :, 1] = np.clip(p_arr[:, :, 1] + 28 * top_left_fac[:, :, 0], 0, 255)
    planet_lit = Image.fromarray(np.clip(p_arr, 0, 255).astype(np.uint8))

    pglow = Image.new('RGBA', (planet_sz + 140, planet_sz + 140), (0,0,0,0))
    pg_cx, pg_cy = (planet_sz + 140)//2, (planet_sz + 140)//2
    pgr = planet_sz // 2 + 6
    for w_val, alpha in [(32, 45), (16, 90), (6, 160)]:
        ImageDraw.Draw(pglow).arc([pg_cx - pgr - w_val//2, pg_cy - pgr - w_val//2, 
                                   pg_cx + pgr + w_val//2, pg_cy + pgr + w_val//2],
                                  start=-140, end=10, fill=(90, 215, 255, alpha), width=w_val)
    pglow = pglow.filter(ImageFilter.GaussianBlur(18))

    canvas.alpha_composite(pglow, (planet_x - planet_sz//2 - 70, planet_y - planet_sz//2 - 70))
    canvas.alpha_composite(planet_lit, (planet_x - planet_sz//2, planet_y - planet_sz//2))

    out = apply_safe_vignette(canvas)
    out.save(OUTPUT_DIR / "scene-06-habitable-zone-edge.png")
    print("Scene 06 saved!")

# ==========================================
# SCENE 07: Greenhouse Atmosphere
# ==========================================
def build_scene_07():
    print("Building Scene 07 (Greenhouse Atmosphere)...")
    im = Image.open(RAW_DIR / 'exoplanet_atmosphere.png')
    scale = TARGET_H / im.height
    new_w = int(im.width * scale)
    im_scaled = im.resize((new_w, TARGET_H), Image.Resampling.LANCZOS)
    # Crop at offset 600
    crop = im_scaled.crop((600, 0, 600 + TARGET_W, TARGET_H))
    out = apply_safe_vignette(crop)
    out.save(OUTPUT_DIR / "scene-07-greenhouse-atmosphere.png")
    print("Scene 07 saved!")

# ==========================================
# SCENE 08: Subsurface Ocean & Hydrothermal Vent
# ==========================================
def build_scene_08():
    print("Building Scene 08 (Subsurface Ocean)...")
    # NOAA hydrothermal vent with tube worms
    raw_vent = Image.open(RAW_DIR / 'hydrothermal_vent.jpg').convert('RGBA')
    scale_v = TARGET_W / raw_vent.width
    vh = int(raw_vent.height * scale_v)
    vent_fit = raw_vent.resize((TARGET_W, vh), Image.Resampling.LANCZOS)

    canvas = Image.new('RGBA', (TARGET_W, TARGET_H), (2, 5, 12, 255))

    # Ice ceiling at top (y: 0..320)
    glacier_raw = Image.open(RAW_DIR / 'glacier_ice.jpg').convert('RGBA')
    ice_crop = glacier_raw.crop((0, 0, glacier_raw.width, int(glacier_raw.height * 0.35)))
    ice_fit = ice_crop.resize((TARGET_W, 300), Image.Resampling.LANCZOS)
    # Invert/flip so it looks like an overhead ice sheet ceiling
    ice_ceiling = ice_fit.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    # Blue/dark water tint on ice ceiling
    ic_arr = np.array(ice_ceiling, dtype=np.float32)
    ic_arr[:, :, 0] *= 0.6
    ic_arr[:, :, 1] *= 0.8
    fade_len = 120
    bot_fade = np.linspace(1.0, 0.0, fade_len)[:, None]
    ic_arr[-fade_len:, :, 3] *= bot_fade
    ice_ceiling_graded = Image.fromarray(np.clip(ic_arr, 0, 255).astype(np.uint8))

    canvas.alpha_composite(ice_ceiling_graded, (0, 0))

    # Position hydrothermal vent chimney in lower/mid canvas (y: 260 to 1920)
    canvas.alpha_composite(vent_fit, (0, TARGET_H - vh))

    # Water column scattering & geothermal glow
    water_haze = Image.new('RGBA', (TARGET_W, TARGET_H), (0,0,0,0))
    whd = ImageDraw.Draw(water_haze)
    # Warm amber/orange geothermal plume glow around the vent top
    whd.ellipse([TARGET_W//2 - 200, TARGET_H - int(vh * 0.75), TARGET_W//2 + 200, TARGET_H - int(vh * 0.4)], fill=(255, 120, 30, 45))
    water_haze = water_haze.filter(ImageFilter.GaussianBlur(60))
    canvas.alpha_composite(water_haze)

    out = apply_safe_vignette(canvas)
    out.save(OUTPUT_DIR / "scene-08-subsurface-ocean.png")
    print("Scene 08 saved!")

# ==========================================
# SCENE 09: Future Exploration & Wonder
# ==========================================
def build_scene_09():
    print("Building Scene 09 (Future Telescopes & Wonder)...")
    raw_laser = Image.open(PBD_RAW_DIR / 'eso_vlt_laser_milkyway.jpg').convert('RGBA')
    scale = max(TARGET_W / raw_laser.width, TARGET_H / raw_laser.height)
    lw, lh = int(raw_laser.width * scale), int(raw_laser.height * scale)
    laser_scaled = raw_laser.resize((lw, lh), Image.Resampling.LANCZOS)
    lx = (lw - TARGET_W) // 2
    ly = (lh - TARGET_H) // 2
    canvas = laser_scaled.crop((lx, ly, lx + TARGET_W, ly + TARGET_H))

    # Add JWST in upper right
    jwst = Image.open(RAW_DIR / 'jwst_clean_cutout.png').convert('RGBA')
    jw_target = 360
    jh_target = int(jwst.height * jw_target / jwst.width)
    jwst_fit = jwst.resize((jw_target, jh_target), Image.Resampling.LANCZOS)
    canvas.alpha_composite(jwst_fit, (TARGET_W - jw_target - 60, 110))

    out = apply_safe_vignette(canvas)
    out.save(OUTPUT_DIR / "scene-09-future-eyes-wonder.png")
    print("Scene 09 saved!")

if __name__ == '__main__':
    build_scene_01()
    build_scene_02()
    build_scene_03()
    build_scene_04()
    build_scene_05()
    build_scene_06()
    build_scene_07()
    build_scene_08()
    build_scene_09()
    print("All 9 scenes rendered successfully!")
