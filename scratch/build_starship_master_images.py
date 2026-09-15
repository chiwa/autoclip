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
    """Scene 01: Narrative Key Art (Starship V3 towering at pad under launch lights, Mamase presenter, and Thai typography)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (4, 6, 16, 255))

    # Base: Pad liftoff / stack
    base = Image.open(RAW_DIR / "launch_pad_ift5.jpg").convert("RGBA")
    scale = h / base.height
    bw = int(base.width * scale)
    base_scaled = base.resize((bw, h), Image.Resampling.LANCZOS)
    
    crop_x = int((bw - w) * 0.42)
    base_cropped = base_scaled.crop((crop_x, 0, crop_x + w, h))

    # Darken bottom for subtitle safe area and presenter integration
    arr = np.array(base_cropped, dtype=np.float32)
    fade_bot = 480
    arr[-fade_bot:, :, :3] *= np.linspace(1.0, 0.25, fade_bot)[:, None, None]
    
    base_graded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(base_graded, (0, 0))

    # Cosmic starfield in upper dark sky
    canvas.alpha_composite(create_starfield(w, h, seed=777, num_stars=180, max_y=700))

    # Glowing Mars in upper right sky
    mars_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    m_draw = ImageDraw.Draw(mars_overlay)
    mx, my, mr = 800, 240, 52
    for r_glow in range(mr + 24, mr, -2):
        alpha = int(40 * (1.0 - (r_glow - mr) / 24.0))
        m_draw.ellipse([mx - r_glow, my - r_glow, mx + r_glow, my + r_glow], fill=(220, 90, 45, alpha))
    m_draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(195, 75, 40, 255))
    m_draw.ellipse([mx - mr + 6, my - mr + 6, mx + mr - 10, my + mr - 10], fill=(225, 110, 60, 160))
    canvas.alpha_composite(mars_overlay)

    # Presenter Cutout on Right
    cutout_path = Path("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scratch/mamase_presenter_cutout.png")
    if not cutout_path.exists():
        cutout_path = Path("assets/characters/mamase-presenter-v1.png")
    cutout = Image.open(cutout_path).convert("RGBA")
    alpha = np.array(cutout.split()[-1])
    y_indices, x_indices = np.where(alpha > 10)
    x_min, x_max = x_indices.min(), x_indices.max()
    y_min, y_max = y_indices.min(), y_indices.max()
    presenter_cropped = cutout.crop((x_min, y_min, x_max + 1, y_max + 1))

    target_h = 1300
    scale_p = target_h / presenter_cropped.height
    target_w = int(presenter_cropped.width * scale_p)
    presenter_scaled = presenter_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Directional golden-orange rim light on presenter left side from rocket launch fire
    p_arr = np.array(presenter_scaled, dtype=np.float32)
    rim_w = int(target_w * 0.28)
    rim_gradient = np.linspace(1.0, 0.0, rim_w)[None, :, None]
    p_arr[:, :rim_w, 0] = np.clip(p_arr[:, :rim_w, 0] + 35 * rim_gradient[:, :, 0], 0, 255)
    p_arr[:, :rim_w, 1] = np.clip(p_arr[:, :rim_w, 1] + 20 * rim_gradient[:, :, 0], 0, 255)
    p_arr[:, :rim_w, 2] = np.clip(p_arr[:, :rim_w, 2] + 5 * rim_gradient[:, :, 0], 0, 255)
    presenter_graded = Image.fromarray(p_arr.astype(np.uint8))

    pos_x = w - target_w + 50
    pos_y = h - target_h

    # Shadow under presenter
    p_shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    p_shadow.paste(presenter_graded, (pos_x - 16, pos_y + 8), presenter_graded)
    p_shadow_blur = p_shadow.filter(ImageFilter.GaussianBlur(16))
    canvas.alpha_composite(p_shadow_blur)
    canvas.paste(presenter_graded, (pos_x, pos_y), presenter_graded)

    # Typography top-left
    font_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/SukhumvitSet.ttc", 72, index=4)
    font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/SukhumvitSet.ttc", 62, index=4)

    # Topic Title: "STARSHIP V3" in warm gold (#FFD666)
    draw_styled_text(canvas, "STARSHIP V3", font_bold, (80, 160), fill_color=(255, 214, 102, 255), shadow_blur=20, shadow_offset=(0, 6))

    # Hook: "เป้าหมายคือดาวอังคาร!" in crisp white (#FFFFFF)
    draw_styled_text(canvas, "เป้าหมายคือดาวอังคาร!", font_sub, (80, 250), fill_color=(255, 255, 255, 255), shadow_blur=18, shadow_offset=(0, 5))

    out_file = PREVIEW_DIR / "scene-01-hook.png"
    canvas.convert("RGB").save(out_file, "PNG")
    print(f"Saved {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_02():
    """Scene 02: การเปิดตัวรุ่นใหม่ (Starship V3 & Super Heavy V3 liftoff from Pad 2)."""
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "launch_pad_ift5.jpg").convert("RGB")
    scale = h / base.height
    bw = int(base.width * scale)
    base_scaled = base.resize((bw, h), Image.Resampling.LANCZOS)
    
    crop_x = int((bw - w) * 0.48)
    cropped = base_scaled.crop((crop_x, 0, crop_x + w, h))

    enh_c = ImageEnhance.Contrast(cropped).enhance(1.18)
    enh_s = ImageEnhance.Color(enh_c).enhance(1.15)
    
    arr = np.array(enh_s, dtype=np.float32)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.45, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-02-v3-debut-liftoff.png"
    final.save(out_file, "PNG")
    print(f"Saved {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_03():
    """Scene 03: พลัง 33 เครื่องยนต์ (Titanic 33 Raptor 3 engines blazing with supersonic shock diamonds)."""
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "sn20_static_fire.jpg").convert("RGB")
    
    scale = h / base.height
    bw = int(base.width * scale)
    base_scaled = base.resize((bw, h), Image.Resampling.LANCZOS)
    
    crop_x = int((bw - w) * 0.52)
    cropped = base_scaled.crop((crop_x, 0, crop_x + w, h))

    raptor = Image.open(RAW_DIR / "raptor_diamond_fire.jpg").convert("RGBA")
    rw, rh = raptor.size
    r_crop = raptor.crop((int(rw * 0.15), int(rh * 0.25), int(rw * 0.85), int(rh * 0.85)))
    r_scaled = r_crop.resize((960, 680), Image.Resampling.LANCZOS)

    arr_r = np.array(r_scaled, dtype=np.float32)
    feather = 80
    arr_r[:feather, :, 3] *= np.linspace(0.0, 1.0, feather)[:, None]
    arr_r[-feather:, :, 3] *= np.linspace(1.0, 0.0, feather)[:, None]
    arr_r[:, :feather, 3] *= np.linspace(0.0, 1.0, feather)[None, :]
    arr_r[:, -feather:, 3] *= np.linspace(1.0, 0.0, feather)[None, :]
    r_faded = Image.fromarray(np.clip(arr_r, 0, 255).astype(np.uint8))

    canvas = cropped.convert("RGBA")
    canvas.paste(r_faded, (60, 750), r_faded)

    enh = ImageEnhance.Contrast(canvas.convert("RGB")).enhance(1.22)
    enh_col = ImageEnhance.Color(enh).enhance(1.20)

    arr = np.array(enh_col, dtype=np.float32)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.40, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-03-raptor3-fury.png"
    final.save(out_file, "PNG")
    print(f"Saved {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_04():
    """Scene 04: เครื่องยนต์มีปัญหา (Hot staging separation & engine flameout in upper stratosphere)."""
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "bfr_staging_separation.jpg").convert("RGBA")
    
    scale = h / base.height
    bw = int(base.width * scale)
    base_scaled = base.resize((bw, h), Image.Resampling.LANCZOS)
    crop_x = int((bw - w) * 0.50)
    cropped = base_scaled.crop((crop_x, 0, crop_x + w, h))

    canvas = cropped

    arr = np.array(canvas, dtype=np.float32)
    arr[:, :, :3] = np.clip(arr[:, :, :3] * 1.08 - 8, 0, 255)
    fade_len = 450
    arr[-fade_len:, :, :3] *= np.linspace(1.0, 0.35, fade_len)[:, None, None]
    
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    stars = create_starfield(w, h, seed=404, num_stars=220, max_y=900)
    final_rgba = final.convert("RGBA")
    final_rgba.alpha_composite(stars)

    out_file = PREVIEW_DIR / "scene-04-staging-anomaly.png"
    final_rgba.convert("RGB").save(out_file, "PNG")
    print(f"Saved {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_05():
    """Scene 05: Booster Hard Splashdown (Super Heavy plunging into turbulent ocean water)."""
    w, h = TARGET_W, TARGET_H
    booster_img = Image.open(RAW_DIR / "super_heavy_booster.jpg").convert("RGBA")
    landing_img = Image.open(RAW_DIR / "booster_landing_swot.jpg").convert("RGBA")

    scale_l = w / landing_img.width
    lh = int(landing_img.height * scale_l)
    landing_scaled = landing_img.resize((w, lh), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (w, h), (8, 14, 28, 255))
    canvas.paste(landing_scaled, (0, h - lh))

    bw, bh = booster_img.size
    b_crop = booster_img.crop((int(bw * 0.28), int(bh * 0.05), int(bw * 0.72), int(bh * 0.85)))
    target_bh = 1250
    scale_b = target_bh / b_crop.height
    target_bw = int(b_crop.width * scale_b)
    b_scaled = b_crop.resize((target_bw, target_bh), Image.Resampling.LANCZOS)

    arr_b = np.array(b_scaled, dtype=np.float32)
    feather = 140
    arr_b[-feather:, :, 3] *= np.linspace(1.0, 0.0, feather)[:, None]
    b_faded = Image.fromarray(np.clip(arr_b, 0, 255).astype(np.uint8))

    canvas.paste(b_faded, (int((w - target_bw) / 2), 120), b_faded)

    splash = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(splash)
    np.random.seed(555)
    for _ in range(400):
        sx = np.random.randint(40, w - 40)
        sy = np.random.randint(h - 580, h - 80)
        sr = np.random.randint(4, 28)
        alpha = np.random.randint(40, 140)
        s_draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(220, 235, 255, alpha))
    splash_blur = splash.filter(ImageFilter.GaussianBlur(12))
    canvas.alpha_composite(splash_blur)

    arr = np.array(canvas.convert("RGB"), dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.05 + 5, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.10 + 10, 0, 255)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.40, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-05-booster-splashdown.png"
    final.save(out_file, "PNG")
    print(f"Saved {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_06():
    """Scene 06: Starship ไปต่อได้ (Starship V3 in Earth orbit firing vacuum Raptor, proving redundancy)."""
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "starship_in_orbit.jpg").convert("RGB")
    
    scale = h / base.height
    bw = int(base.width * scale)
    base_scaled = base.resize((bw, h), Image.Resampling.LANCZOS)
    
    crop_x = int((bw - w) * 0.48)
    cropped = base_scaled.crop((crop_x, 0, crop_x + w, h))

    plume_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(plume_overlay)
    px, py = 590, 840
    for r in range(120, 10, -8):
        alpha = int(60 * (1.0 - r / 120.0))
        p_draw.ellipse([px - r * 0.6, py - r * 1.8, px + r * 0.6, py + r * 0.4], fill=(70, 160, 255, alpha))
    for r in range(40, 4, -4):
        p_draw.ellipse([px - r * 0.3, py - r * 1.2, px + r * 0.3, py], fill=(220, 240, 255, 120))
    plume_blur = plume_overlay.filter(ImageFilter.GaussianBlur(8))

    canvas = cropped.convert("RGBA")
    canvas.alpha_composite(plume_blur)

    enh = ImageEnhance.Contrast(canvas.convert("RGB")).enhance(1.16)
    enh_c = ImageEnhance.Color(enh).enhance(1.18)

    arr = np.array(enh_c, dtype=np.float32)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.40, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-06-starship-orbital-insertion.png"
    final.save(out_file, "PNG")
    print(f"Saved {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_07():
    """Scene 07: ปล่อย Payload สำเร็จ (Deploying 20 Starlink simulator units + 2 modified satellites)."""
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "starship_in_orbit.jpg").convert("RGBA")
    scale = h / base.height
    bw = int(base.width * scale)
    base_scaled = base.resize((bw, h), Image.Resampling.LANCZOS)
    crop_x = int((bw - w) * 0.35)
    canvas = base_scaled.crop((crop_x, 0, crop_x + w, h))

    sl_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sl_draw = ImageDraw.Draw(sl_overlay)

    np.random.seed(720)
    for i in range(20):
        sx = int(240 + (i % 4) * 140 + (i // 4) * 45 + np.random.randint(-15, 15))
        sy = int(480 + (i // 4) * 110 + (i % 4) * 20 + np.random.randint(-10, 10))
        sw = np.random.randint(65, 85)
        sh = np.random.randint(22, 30)
        
        sl_draw.rectangle([sx, sy, sx + sw, sy + sh], fill=(190, 205, 225, 230), outline=(235, 245, 255, 255), width=1)
        sl_draw.rectangle([sx + 6, sy + 4, sx + sw - 6, sy + sh - 4], fill=(130, 155, 190, 200))
        sl_draw.line([sx + sw // 2, sy + 2, sx + sw // 2, sy + sh - 2], fill=(210, 225, 245, 220), width=1)

    for mod_idx, (mx, my) in enumerate([(680, 420), (760, 720)]):
        sl_draw.rectangle([mx, my, mx + 45, my + 55], fill=(240, 200, 110, 255), outline=(255, 255, 255, 255), width=2)
        sl_draw.rectangle([mx - 65, my + 14, mx - 5, my + 42], fill=(45, 95, 175, 240), outline=(180, 220, 255, 255), width=1)
        sl_draw.rectangle([mx + 50, my + 14, mx + 110, my + 42], fill=(45, 95, 175, 240), outline=(180, 220, 255, 255), width=1)
        for gx in range(mx - 55, mx - 5, 15):
            sl_draw.line([gx, my + 14, gx, my + 42], fill=(80, 140, 220, 200))
        for gx in range(mx + 65, mx + 110, 15):
            sl_draw.line([gx, my + 14, gx, my + 42], fill=(80, 140, 220, 200))

    canvas.alpha_composite(sl_overlay)

    arr = np.array(canvas.convert("RGB"), dtype=np.float32)
    arr[:, :, :3] = np.clip(arr[:, :, :3] * 1.12 - 10, 0, 255)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.40, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-07-starlink-payload-deploy.png"
    final.save(out_file, "PNG")
    print(f"Saved {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_08():
    """Scene 08: กลับเข้าสู่บรรยากาศ (Hypersonic belly-flop re-entry with blazing purple-magenta plasma envelope)."""
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "starship_reentry_plasma.webp").convert("RGB")
    
    scale = h / base.height
    bw = int(base.width * scale)
    base_scaled = base.resize((bw, h), Image.Resampling.LANCZOS)
    
    crop_x = int((bw - w) * 0.50)
    cropped = base_scaled.crop((crop_x, 0, crop_x + w, h))

    enh = ImageEnhance.Contrast(cropped).enhance(1.24)
    enh_col = ImageEnhance.Color(enh).enhance(1.28)

    arr = np.array(enh_col, dtype=np.float32)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.40, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-08-hypersonic-plasma-reentry.png"
    final.save(out_file, "PNG")
    print(f"Saved {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_09():
    """Scene 09: ทำไม V3 จึงสำคัญ (Starship V3 orbital refueling & journey to Moon and Mars)."""
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "starship_mars_4k.jpg").convert("RGB")
    
    scale = h / base.height
    bw = int(base.width * scale)
    base_scaled = base.resize((bw, h), Image.Resampling.LANCZOS)
    
    crop_x = int((bw - w) * 0.50)
    cropped = base_scaled.crop((crop_x, 0, crop_x + w, h))

    enh = ImageEnhance.Contrast(cropped).enhance(1.18)
    enh_col = ImageEnhance.Color(enh).enhance(1.15)

    arr = np.array(enh_col, dtype=np.float32)
    fade_len = 450
    arr[-fade_len:, :, :] *= np.linspace(1.0, 0.40, fade_len)[:, None, None]
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    out_file = PREVIEW_DIR / "scene-09-moon-mars-refueling-future.png"
    final.save(out_file, "PNG")
    print(f"Saved {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_10():
    """Scene 10: Canonical Mamase Brand Outro."""
    src = Path("assets/pale_blue_dot_universe_reel/scene-10-mamase-outro.png")
    if not src.exists():
        src = Path("assets/bepicolombo_extreme_mercury_reel/scene-09-mamase-outro.png")
    out_file = PREVIEW_DIR / "scene-10-mamase-outro.png"
    shutil.copy2(src, out_file)
    print(f"Saved {out_file.name}: {out_file.stat().st_size:,} bytes")

def main():
    print("Building all 10 master images for Starship V3 Flight 12 Reel...")
    build_scene_01()
    build_scene_02()
    build_scene_03()
    build_scene_04()
    build_scene_05()
    build_scene_06()
    build_scene_07()
    build_scene_08()
    build_scene_09()
    build_scene_10()
    print("All 10 images generated successfully in scratch/starship_preview/!")

if __name__ == "__main__":
    main()
