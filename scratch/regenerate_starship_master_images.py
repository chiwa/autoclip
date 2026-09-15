import os
import shutil
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np

TARGET_W = 1080
TARGET_H = 1920

RAW_DIR = Path("scratch/starship_raw")
PREVIEW_DIR = Path("scratch/starship_preview")
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

def create_starfield(w=TARGET_W, h=TARGET_H, seed=42, num_stars=350, max_y=1600):
    np.random.seed(seed)
    star_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(star_img)
    for _ in range(num_stars):
        x = np.random.randint(0, w)
        y = np.random.randint(0, max_y)
        b = np.random.randint(90, 255)
        r = np.random.choice([1, 1, 1, 2])
        col = (b, int(b * 0.95), int(b * 1.1), np.random.randint(140, 255))
        draw.ellipse([x, y, x + r, y + r], fill=col)
    return star_img

def draw_styled_text(canvas, text, font, pos, fill_color, stroke_color=(0,0,0,255), stroke_width=0, shadow_blur=16, shadow_offset=(0,6), shadow_color=(0,0,0,240)):
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh_draw = ImageDraw.Draw(overlay)
    sh_x = pos[0] + shadow_offset[0]
    sh_y = pos[1] + shadow_offset[1]
    sh_draw.text((sh_x, sh_y), text, font=font, fill=shadow_color, stroke_width=stroke_width+6, stroke_fill=shadow_color)
    blurred_shadow = overlay.filter(ImageFilter.GaussianBlur(shadow_blur))
    canvas.alpha_composite(blurred_shadow)

    fg_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    fg_draw = ImageDraw.Draw(fg_layer)
    fg_draw.text(pos, text, font=font, fill=fill_color, stroke_width=stroke_width, stroke_fill=stroke_color)
    canvas.alpha_composite(fg_layer)

def build_scene_01():
    """Scene 01: Narrative Key Art (Starship V3 at Pad with tower, launch flame, Mars in sky, Mamase presenter, and Thai typography)."""
    w, h = TARGET_W, TARGET_H
    
    # 1. Base: Pad tower & rocket
    pad_img = Image.open(RAW_DIR / "starship_on_pad_tower.jpg").convert("RGBA")
    scale_pad = h / pad_img.height
    pw = int(pad_img.width * scale_pad)
    pad_scaled = pad_img.resize((pw, h), Image.Resampling.LANCZOS)
    
    # Crop centering on rocket and tower chopsticks
    crop_x = int((pw - w) * 0.52)
    canvas = pad_scaled.crop((crop_x, 0, crop_x + w, h))

    # Add dramatic launch fire and steam at base
    launch_fire = Image.open(RAW_DIR / "sn20_static_fire.jpg").convert("RGBA")
    fw, fh = launch_fire.size
    f_crop = launch_fire.crop((int(fw * 0.2), int(fh * 0.4), int(fw * 0.8), int(fh * 0.95)))
    f_scaled = f_crop.resize((w, 650), Image.Resampling.LANCZOS)
    
    # Feather top of flame so it merges into pad
    arr_f = np.array(f_scaled, dtype=np.float32)
    feather_top = 180
    arr_f[:feather_top, :, 3] *= np.linspace(0.0, 1.0, feather_top)[:, None]
    f_faded = Image.fromarray(np.clip(arr_f, 0, 255).astype(np.uint8))
    canvas.paste(f_faded, (0, h - 700), f_faded)

    # 2. Glowing Mars in upper right sky
    mars_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    m_draw = ImageDraw.Draw(mars_overlay)
    mx, my, mr = 820, 220, 58
    # Outer atmospheric glow
    for r_glow in range(mr + 30, mr, -2):
        alpha = int(45 * (1.0 - (r_glow - mr) / 30.0))
        m_draw.ellipse([mx - r_glow, my - r_glow, mx + r_glow, my + r_glow], fill=(230, 95, 45, alpha))
    m_draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(195, 75, 40, 255))
    # Shading and crater hints
    m_draw.ellipse([mx - mr + 8, my - mr + 8, mx + mr - 12, my + mr - 12], fill=(225, 115, 60, 180))
    m_draw.ellipse([mx - 15, my - 10, mx + 20, my + 15], fill=(160, 55, 30, 150))
    canvas.alpha_composite(mars_overlay)

    # Stars in upper sky
    canvas.alpha_composite(create_starfield(w, h, seed=999, num_stars=150, max_y=600))

    # 3. Presenter Cutout on Right
    cutout_path = Path("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scratch/mamase_presenter_cutout.png")
    if not cutout_path.exists():
        cutout_path = Path("assets/characters/mamase-presenter-v1.png")
    cutout = Image.open(cutout_path).convert("RGBA")
    alpha = np.array(cutout.split()[-1])
    y_indices, x_indices = np.where(alpha > 10)
    x_min, x_max = x_indices.min(), x_indices.max()
    y_min, y_max = y_indices.min(), y_indices.max()
    presenter_cropped = cutout.crop((x_min, y_min, x_max + 1, y_max + 1))

    target_h = 1320
    scale_p = target_h / presenter_cropped.height
    target_w = int(presenter_cropped.width * scale_p)
    presenter_scaled = presenter_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Directional golden-orange rim light on presenter left side from rocket launch fire
    p_arr = np.array(presenter_scaled, dtype=np.float32)
    rim_w = int(target_w * 0.30)
    rim_gradient = np.linspace(1.0, 0.0, rim_w)[None, :, None]
    p_arr[:, :rim_w, 0] = np.clip(p_arr[:, :rim_w, 0] + 40 * rim_gradient[:, :, 0], 0, 255)
    p_arr[:, :rim_w, 1] = np.clip(p_arr[:, :rim_w, 1] + 25 * rim_gradient[:, :, 0], 0, 255)
    p_arr[:, :rim_w, 2] = np.clip(p_arr[:, :rim_w, 2] + 5 * rim_gradient[:, :, 0], 0, 255)
    presenter_graded = Image.fromarray(p_arr.astype(np.uint8))

    pos_x = w - target_w + 50
    pos_y = h - target_h

    # Shadow under presenter
    p_shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    p_shadow.paste(presenter_graded, (pos_x - 18, pos_y + 8), presenter_graded)
    p_shadow_blur = p_shadow.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(p_shadow_blur)
    canvas.paste(presenter_graded, (pos_x, pos_y), presenter_graded)

    # 4. Typography top-left
    font_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/SukhumvitSet.ttc", 76, index=4)
    font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/SukhumvitSet.ttc", 64, index=4)

    # Topic Title: "STARSHIP V3" in warm gold (#FFD666)
    draw_styled_text(canvas, "STARSHIP V3", font_bold, (80, 160), fill_color=(255, 214, 102, 255), shadow_blur=22, shadow_offset=(0, 6))

    # Hook: "เป้าหมายคือดาวอังคาร!" in crisp white (#FFFFFF)
    draw_styled_text(canvas, "เป้าหมายคือดาวอังคาร!", font_sub, (80, 255), fill_color=(255, 255, 255, 255), shadow_blur=20, shadow_offset=(0, 5))

    out_file = PREVIEW_DIR / "scene-01-hook.png"
    canvas.convert("RGB").save(out_file, "PNG")
    print(f"Re-built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_02():
    """Scene 02: การเปิดตัวรุ่นใหม่ (Starship V3 & Super Heavy V3 liftoff from Pad 2)."""
    w, h = TARGET_W, TARGET_H
    # Use starship_on_pad_tower.jpg with launch fire & steam billowing
    pad_img = Image.open(RAW_DIR / "starship_on_pad_tower.jpg").convert("RGBA")
    scale_pad = h / pad_img.height
    pw = int(pad_img.width * scale_pad)
    pad_scaled = pad_img.resize((pw, h), Image.Resampling.LANCZOS)
    crop_x = int((pw - w) * 0.52)
    canvas = pad_scaled.crop((crop_x, 0, crop_x + w, h))

    # Composite ascending rocket flame & deluge exhaust
    fire = Image.open(RAW_DIR / "sn20_static_fire.jpg").convert("RGBA")
    fw, fh = fire.size
    f_crop = fire.crop((int(fw * 0.15), int(fh * 0.35), int(fw * 0.85), int(fh * 0.95)))
    f_scaled = f_crop.resize((w, 750), Image.Resampling.LANCZOS)
    arr_f = np.array(f_scaled, dtype=np.float32)
    feather_top = 220
    arr_f[:feather_top, :, 3] *= np.linspace(0.0, 1.0, feather_top)[:, None]
    f_faded = Image.fromarray(np.clip(arr_f, 0, 255).astype(np.uint8))
    canvas.paste(f_faded, (0, h - 750), f_faded)

    enh = ImageEnhance.Contrast(canvas.convert("RGB")).enhance(1.18)
    enh_c = ImageEnhance.Color(enh).enhance(1.16)

    # Subtitle safe area darkening
    arr = np.array(enh_c, dtype=np.float32)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.40, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-02-v3-debut-liftoff.png"
    final.save(out_file, "PNG")
    print(f"Re-built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_03():
    """Scene 03: พลัง 33 เครื่องยนต์ (Titanic 33 Raptor 3 engines blazing full frame)."""
    w, h = TARGET_W, TARGET_H
    # Use sn20_static_fire.jpg to completely fill the vertical canvas
    fire = Image.open(RAW_DIR / "sn20_static_fire.jpg").convert("RGB")
    fw, fh = fire.size
    # Crop central supersonic flame plume and deluge trench
    # fw=5568, fh=3712
    crop_w = int(fh * (w / h))
    crop_x = int((fw - crop_w) * 0.58)
    cropped = fire.crop((crop_x, 0, crop_x + crop_w, fh))
    canvas = cropped.resize((w, h), Image.Resampling.LANCZOS)

    # Enhance contrast, brilliant orange core and deep navy smoke
    enh = ImageEnhance.Contrast(canvas).enhance(1.22)
    enh_c = ImageEnhance.Color(enh).enhance(1.25)

    arr = np.array(enh_c, dtype=np.float32)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.38, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-03-raptor3-fury.png"
    final.save(out_file, "PNG")
    print(f"Re-built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_04():
    """Scene 04: เครื่องยนต์มีปัญหา (Hot staging separation & engine anomaly)."""
    w, h = TARGET_W, TARGET_H
    # bfr_staging_separation.jpg has upper stage & booster separating
    bfr = Image.open(RAW_DIR / "bfr_staging_separation.jpg").convert("RGBA")
    bw, bh = bfr.size
    # Crop both stages and expanding plume
    crop_w = int(bh * (w / h))
    crop_x = int((bw - crop_w) * 0.50)
    cropped = bfr.crop((crop_x, 0, crop_x + crop_w, bh))
    canvas = cropped.resize((w, h), Image.Resampling.LANCZOS)

    # Add realistic hot-staging flame burst at interstage ring
    hot = Image.open(RAW_DIR / "hot_staging_ift5.jpg").convert("RGBA")
    hw, hh = hot.size
    h_scaled = hot.resize((650, 480), Image.Resampling.LANCZOS)
    arr_h = np.array(h_scaled, dtype=np.float32)
    # Circular feather
    fh = 70
    arr_h[:fh, :, 3] *= np.linspace(0.0, 1.0, fh)[:, None]
    arr_h[-fh:, :, 3] *= np.linspace(1.0, 0.0, fh)[:, None]
    arr_h[:, :fh, 3] *= np.linspace(0.0, 1.0, fh)[None, :]
    arr_h[:, -fh:, 3] *= np.linspace(1.0, 0.0, fh)[None, :]
    h_faded = Image.fromarray(np.clip(arr_h, 0, 255).astype(np.uint8))

    # Overlay hot staging burst at interstage separation point (center)
    canvas.paste(h_faded, (int((w - 650) / 2), 650), h_faded)

    # Stars in cosmic background
    canvas.alpha_composite(create_starfield(w, h, seed=808, num_stars=240, max_y=1100))

    enh = ImageEnhance.Contrast(canvas.convert("RGB")).enhance(1.18)
    enh_c = ImageEnhance.Color(enh).enhance(1.15)

    arr = np.array(enh_c, dtype=np.float32)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.35, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-04-staging-anomaly.png"
    final.save(out_file, "PNG")
    print(f"Re-built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_05():
    """Scene 05: Booster Hard Splashdown (Super Heavy plunging into turbulent ocean water with landing burn)."""
    w, h = TARGET_W, TARGET_H
    # Use real 8K ocean splashdown photo
    ocean = Image.open(RAW_DIR / "ocean_splashdown_hi.jpg").convert("RGB")
    ow, oh = ocean.size
    # Crop turbulent ocean with huge foaming waves and water spray
    crop_w = int(oh * (w / h))
    crop_x = int((ow - crop_w) * 0.50)
    ocean_crop = ocean.crop((crop_x, 0, crop_x + crop_w, oh))
    canvas = ocean_crop.resize((w, h), Image.Resampling.LANCZOS).convert("RGBA")

    # Composite Super Heavy booster slamming downward into the ocean
    booster = Image.open(RAW_DIR / "super_heavy_booster.jpg").convert("RGBA")
    bw, bh = booster.size
    b_crop = booster.crop((int(bw * 0.30), int(bh * 0.05), int(bw * 0.70), int(bh * 0.85)))
    target_bh = 1100
    scale_b = target_bh / b_crop.height
    target_bw = int(b_crop.width * scale_b)
    b_scaled = b_crop.resize((target_bw, target_bh), Image.Resampling.LANCZOS)

    # Booster landing burn fire at engine base
    arr_b = np.array(b_scaled, dtype=np.float32)
    feather = 160
    arr_b[-feather:, :, 3] *= np.linspace(1.0, 0.0, feather)[:, None]
    b_faded = Image.fromarray(np.clip(arr_b, 0, 255).astype(np.uint8))

    # Paste booster descending vertically into water
    canvas.paste(b_faded, (int((w - target_bw) / 2), 60), b_faded)

    # Add landing burn flame explosion hitting the water surface at y=1050
    flame_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    f_draw = ImageDraw.Draw(flame_overlay)
    fx, fy = int(w / 2), 1120
    for r in range(240, 20, -12):
        alpha = int(120 * (1.0 - r / 240.0))
        f_draw.ellipse([fx - r * 1.5, fy - r * 0.6, fx + r * 1.5, fy + r * 0.8], fill=(255, 140, 30, alpha))
    for r in range(120, 10, -8):
        f_draw.ellipse([fx - r * 1.2, fy - r * 0.4, fx + r * 1.2, fy + r * 0.5], fill=(255, 230, 110, 180))
    flame_blur = flame_overlay.filter(ImageFilter.GaussianBlur(14))
    canvas.alpha_composite(flame_blur)

    enh = ImageEnhance.Contrast(canvas.convert("RGB")).enhance(1.20)
    enh_c = ImageEnhance.Color(enh).enhance(1.18)

    arr = np.array(enh_c, dtype=np.float32)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.38, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-05-booster-splashdown.png"
    final.save(out_file, "PNG")
    print(f"Re-built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_07():
    """Scene 07: ปล่อย Payload สำเร็จ (Deploying 20 Starlink simulators + 2 modified satellites)."""
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "starship_in_orbit.jpg").convert("RGBA")
    scale = h / base.height
    bw = int(base.width * scale)
    base_scaled = base.resize((bw, h), Image.Resampling.LANCZOS)
    crop_x = int((bw - w) * 0.38)
    canvas = base_scaled.crop((crop_x, 0, crop_x + w, h))

    # Cutout real photographic Starlink satellite from starlink_vertical.jpg
    sl_raw = Image.open(RAW_DIR / "starlink_vertical.jpg").convert("RGBA")
    sw_raw, sh_raw = sl_raw.size
    # Crop a single clean Starlink satellite with solar array
    sl_crop = sl_raw.crop((int(sw_raw * 0.25), int(sh_raw * 0.30), int(sw_raw * 0.75), int(sh_raw * 0.55)))
    
    # Scale down to form the 20 deploying simulator units
    sl_sats = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    
    np.random.seed(888)
    for i in range(20):
        # Size varies with orbital perspective
        unit_w = int(105 - (i // 4) * 8 + np.random.randint(-4, 4))
        unit_h = int(unit_w * (sl_crop.height / sl_crop.width))
        sat_thumb = sl_crop.resize((unit_w, unit_h), Image.Resampling.LANCZOS)
        
        # Staggered orbital deployment stream
        sx = int(160 + (i % 4) * 165 + (i // 4) * 45 + np.random.randint(-12, 12))
        sy = int(460 + (i // 4) * 115 + (i % 4) * 22 + np.random.randint(-8, 8))
        
        # Subtle metallic specular glow
        sl_sats.paste(sat_thumb, (sx, sy), sat_thumb)

    # 2 modified research satellites (distinct gold foil bus and dual cross solar wings)
    for mod_idx, (mx, my) in enumerate([(720, 390), (790, 710)]):
        mod_w, mod_h = 130, 85
        mod_thumb = sl_crop.resize((mod_w, mod_h), Image.Resampling.LANCZOS)
        # Gold tint
        arr_m = np.array(mod_thumb, dtype=np.float32)
        arr_m[:, :, 0] = np.clip(arr_m[:, :, 0] * 1.35, 0, 255)
        arr_m[:, :, 1] = np.clip(arr_m[:, :, 1] * 1.15, 0, 255)
        arr_m[:, :, 2] = np.clip(arr_m[:, :, 2] * 0.70, 0, 255)
        mod_gold = Image.fromarray(arr_m.astype(np.uint8))
        sl_sats.paste(mod_gold, (mx, my), mod_gold)

    canvas.alpha_composite(sl_sats)

    enh = ImageEnhance.Contrast(canvas.convert("RGB")).enhance(1.15)
    enh_c = ImageEnhance.Color(enh).enhance(1.18)

    arr = np.array(enh_c, dtype=np.float32)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.40, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-07-starlink-payload-deploy.png"
    final.save(out_file, "PNG")
    print(f"Re-built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_08():
    """Scene 08: กลับเข้าสู่บรรยากาศ (Hypersonic belly-flop re-entry with blazing purple-magenta plasma envelope)."""
    w, h = TARGET_W, TARGET_H
    # Base: Earth atmosphere & horizon
    earth_base = Image.open(RAW_DIR / "bfr_staging_separation.jpg").convert("RGBA")
    ew, eh = earth_base.size
    crop_w = int(eh * (w / h))
    crop_x = int((ew - crop_w) * 0.50)
    canvas = earth_base.crop((crop_x, 0, crop_x + crop_w, eh)).resize((w, h), Image.Resampling.LANCZOS)

    # Invert to dark twilight re-entry sky
    arr = np.array(canvas, dtype=np.float32)
    arr[:, :, :3] = np.clip(arr[:, :, :3] * 0.45 + 5, 0, 255)
    canvas = Image.fromarray(arr.astype(np.uint8))

    # Starship belly-flop orientation
    ship = Image.open(RAW_DIR / "starship_reentry_plasma.webp").convert("RGBA")
    sw, sh = ship.size
    s_crop = ship.crop((int(sw * 0.25), int(sh * 0.70), int(sw * 0.90), int(sh * 0.98)))
    target_sw = 950
    scale_s = target_sw / s_crop.width
    target_sh = int(s_crop.height * scale_s)
    s_scaled = s_crop.resize((target_sw, target_sh), Image.Resampling.LANCZOS)

    # Volumetric magenta/purple/cyan ionization plasma sheath
    plasma = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(plasma)
    
    # Hypersonic shock front under the belly
    px, py = int(w / 2) + 40, 880
    for r in range(480, 40, -18):
        alpha = int(90 * (1.0 - r / 480.0))
        # Violet/magenta ionization plasma
        p_draw.ellipse([px - r * 1.3, py - r * 0.45, px + r * 1.3, py + r * 0.55], fill=(210, 40, 230, alpha))
        # Cyan high-energy shock boundary
        p_draw.ellipse([px - r * 1.2, py - r * 0.35, px + r * 1.2, py + r * 0.45], fill=(50, 200, 255, int(alpha * 0.6)))
    # Intense incandescent core along the heat shield
    for r in range(180, 15, -12):
        p_draw.ellipse([px - r * 1.1, py - r * 0.25, px + r * 1.1, py + r * 0.35], fill=(255, 120, 240, 160))
        p_draw.ellipse([px - r * 0.9, py - r * 0.15, px + r * 0.9, py + r * 0.25], fill=(255, 240, 255, 200))
    
    plasma_blur = plasma.filter(ImageFilter.GaussianBlur(16))
    canvas.alpha_composite(plasma_blur)

    # Paste Starship belly-first right over the plasma shock
    canvas.paste(s_scaled, (int((w - target_sw) / 2) + 20, 760), s_scaled)

    # Stars in upper re-entry sky
    canvas.alpha_composite(create_starfield(w, h, seed=888, num_stars=220, max_y=750))

    enh = ImageEnhance.Contrast(canvas.convert("RGB")).enhance(1.24)
    enh_c = ImageEnhance.Color(enh).enhance(1.30)

    arr = np.array(enh_c, dtype=np.float32)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.35, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-08-hypersonic-plasma-reentry.png"
    final.save(out_file, "PNG")
    print(f"Re-built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_09():
    """Scene 09: ทำไม V3 จึงสำคัญ (Multiplanetary future: Moon, Mars, and orbital refueling)."""
    w, h = TARGET_W, TARGET_H
    # Canvas with deep space starfield
    canvas = Image.new("RGBA", (w, h), (4, 6, 14, 255))
    canvas.alpha_composite(create_starfield(w, h, seed=999, num_stars=380, max_y=1600))

    # Upper region: Mars globe occupying 60% of width
    mars_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    m_draw = ImageDraw.Draw(mars_overlay)
    mx, my, mr = 540, 420, 280
    for r_glow in range(mr + 60, mr, -4):
        alpha = int(60 * (1.0 - (r_glow - mr) / 60.0))
        m_draw.ellipse([mx - r_glow, my - r_glow, mx + r_glow, my + r_glow], fill=(225, 90, 40, alpha))
    m_draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(190, 70, 35, 255))
    # Mars surface details (craters, Valles Marineris rift, polar ice)
    m_draw.ellipse([mx - mr + 35, my - mr + 25, mx + mr - 45, my + mr - 50], fill=(215, 105, 50, 180))
    m_draw.ellipse([mx - 140, my - 60, mx + 160, my + 40], fill=(150, 50, 25, 160))
    m_draw.ellipse([mx - 60, my - mr + 8, mx + 60, my - mr + 45], fill=(245, 245, 255, 220)) # North polar cap
    canvas.alpha_composite(mars_overlay)

    # Crescent Moon in upper left
    moon_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mo_draw = ImageDraw.Draw(moon_overlay)
    lx, ly, lr = 220, 200, 75
    mo_draw.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=(210, 215, 225, 255))
    mo_draw.ellipse([lx - lr + 26, ly - lr - 10, lx + lr + 35, ly + lr + 15], fill=(4, 6, 14, 255))
    canvas.alpha_composite(moon_overlay)

    # Midground: Starship V3 spacecraft in interplanetary transit
    ship = Image.open(RAW_DIR / "starship_mars_4k.jpg").convert("RGBA")
    sw, sh = ship.size
    s_crop = ship.crop((int(sw * 0.05), int(sh * 0.52), int(sw * 0.75), int(sh * 0.95)))
    target_sw = 980
    scale_s = target_sw / s_crop.width
    target_sh = int(s_crop.height * scale_s)
    s_scaled = s_crop.resize((target_sw, target_sh), Image.Resampling.LANCZOS)

    canvas.paste(s_scaled, (int((w - target_sw) / 2) + 20, 840), s_scaled)

    enh = ImageEnhance.Contrast(canvas.convert("RGB")).enhance(1.20)
    enh_c = ImageEnhance.Color(enh).enhance(1.22)

    arr = np.array(enh_c, dtype=np.float32)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.35, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-09-moon-mars-refueling-future.png"
    final.save(out_file, "PNG")
    print(f"Re-built {out_file.name}: {out_file.stat().st_size:,} bytes")

def main():
    print("Regenerating improved master images...")
    build_scene_01()
    build_scene_02()
    build_scene_03()
    build_scene_04()
    build_scene_05()
    build_scene_07()
    build_scene_08()
    build_scene_09()
    print("Regeneration complete!")

if __name__ == "__main__":
    main()
