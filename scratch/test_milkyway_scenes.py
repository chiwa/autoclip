import os
import shutil
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np

TARGET_W = 1080
TARGET_H = 1920
OUT_DIR = Path("scratch/milkyway_preview")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def create_starfield(w=TARGET_W, h=TARGET_H, seed=42, num_stars=350, max_y=1600):
    np.random.seed(seed)
    star_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(star_img)
    for _ in range(num_stars):
        x = np.random.randint(0, w)
        y = np.random.randint(0, max_y)
        b = np.random.randint(120, 255)
        r = np.random.choice([1, 1, 1, 2])
        col = (b, int(b * 0.96), int(b * 1.1), np.random.randint(150, 255))
        draw.ellipse([x, y, x + r, y + r], fill=col)
    return star_img

def apply_safe_area_vignette(img, bot_height=420, top_height=140):
    """Adds a soft dark gradient at bottom for subtitles and top for platform UI."""
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    arr = np.zeros((h, w, 4), dtype=np.float32)
    
    # Bottom vignette (smooth quadratic curve for subtle documentary feel)
    y_bot = np.linspace(0.0, 1.0, bot_height) ** 1.8 * 210
    arr[-bot_height:, :, 3] = y_bot[:, None]
    
    # Top vignette
    y_top = np.linspace(1.0, 0.0, top_height) ** 1.5 * 140
    arr[:top_height, :, 3] = np.maximum(arr[:top_height, :, 3], y_top[:, None])
    
    vignette = Image.fromarray(arr.astype(np.uint8))
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(vignette)
    return img_rgba.convert("RGB")

def draw_styled_text(canvas, text, font, pos, fill_color, stroke_color=(0,0,0,255), stroke_width=0, shadow_blur=14, shadow_offset=(0,6), shadow_color=(0,0,0,240)):
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
    print("Building Scene 01...")
    canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (3, 5, 14, 255))
    
    # 1. Base Milky Way core
    base = Image.open("scratch/milkyway_raw/milky_way_rising_core.jpg").convert("RGBA")
    scale = TARGET_H / base.height
    bw = int(base.width * scale)
    base_scaled = base.resize((bw, TARGET_H), Image.Resampling.LANCZOS)
    crop_x = int((bw - TARGET_W) * 0.45)
    base_cropped = base_scaled.crop((crop_x, 0, crop_x + TARGET_W, TARGET_H))
    
    enhancer = ImageEnhance.Contrast(base_cropped.convert("RGB"))
    base_enh = enhancer.enhance(1.18).convert("RGBA")
    canvas.paste(base_enh, (0, 0))
    
    # 2. Presenter Cutout on Right
    presenter_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scratch/mamase_presenter_cutout.png"
    cutout = Image.open(presenter_path).convert("RGBA")
    alpha = np.array(cutout.split()[-1])
    y_indices, x_indices = np.where(alpha > 10)
    x_min, x_max = x_indices.min(), x_indices.max()
    y_min, y_max = y_indices.min(), y_indices.max()
    presenter_cropped = cutout.crop((x_min, y_min, x_max + 1, y_max + 1))
    
    target_h = 1260
    scale_p = target_h / presenter_cropped.height
    target_w = int(presenter_cropped.width * scale_p)
    presenter_scaled = presenter_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Subtle cool blue night rim lighting on left edge
    p_arr = np.array(presenter_scaled, dtype=np.float32)
    rim_w = int(target_w * 0.22)
    rim_gradient = np.linspace(1.0, 0.0, rim_w)[None, :, None]
    p_arr[:, :rim_w, 2] = np.clip(p_arr[:, :rim_w, 2] + 25 * rim_gradient[:, :, 0], 0, 255)
    p_arr[:, :rim_w, 1] = np.clip(p_arr[:, :rim_w, 1] + 12 * rim_gradient[:, :, 0], 0, 255)
    presenter_graded = Image.fromarray(p_arr.astype(np.uint8))
    
    pos_x = TARGET_W - target_w + 40
    pos_y = TARGET_H - target_h
    
    p_shadow = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    p_shadow.paste(presenter_graded, (pos_x - 12, pos_y + 6), presenter_graded)
    p_shadow_blur = p_shadow.filter(ImageFilter.GaussianBlur(16))
    canvas.alpha_composite(p_shadow_blur)
    canvas.paste(presenter_graded, (pos_x, pos_y), presenter_graded)
    
    # 3. Typography top-left
    font_path = "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc"
    f_topic = ImageFont.truetype(font_path, 44, index=0)
    f_hook = ImageFont.truetype(font_path, 72, index=0)
    
    tx, ty = 64, 110
    draw_styled_text(canvas, "ความลับบนผืนฟ้า", f_topic, (tx, ty), fill_color=(255, 214, 102, 255))
    
    hy = ty + 66
    draw_styled_text(canvas, "แต่ละชาติเรียกทางช้างเผือก\nว่าอะไรบ้าง?", f_hook, (tx, hy), fill_color=(255, 255, 255, 255))
    
    res = apply_safe_area_vignette(canvas, bot_height=420, top_height=140)
    out_file = OUT_DIR / "scene-01-hook.png"
    res.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_02():
    print("Building Scene 02 (Thailand)...")
    # Sukhothai clean: 1500x1000
    src = Image.open("scratch/milkyway_raw/thailand_sukhothai_milkyway_clean.jpg").convert("RGB")
    
    # Scale to width 1080
    # height becomes 1080 * 1000 / 1500 = 720
    # To give the temple substantial presence and high fidelity:
    scale = 1.45
    nw, nh = int(src.width * scale), int(src.height * scale) # 2175 x 1450
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    cx = int((nw - TARGET_W) * 0.42)
    temple_crop = resized.crop((cx, 0, cx + TARGET_W, nh)) # 1080 x 1450
    
    canvas = Image.new("RGB", (TARGET_W, TARGET_H), (2, 4, 12))
    # Place temple in lower portion: y = TARGET_H - nh = 470
    y_pos = TARGET_H - nh
    canvas.paste(temple_crop, (0, y_pos))
    
    # In upper portion (y = 0..520), blend with upper starry sky from temple_crop
    top_strip = temple_crop.crop((0, 0, TARGET_W, 260))
    sky_fill = top_strip.resize((TARGET_W, 520), Image.Resampling.LANCZOS)
    canvas.paste(sky_fill, (0, 0))
    
    # Blend transition zone between sky_fill and temple_crop
    arr_can = np.array(canvas, dtype=np.float32)
    fade_len = 160
    for i in range(fade_len):
        alpha = i / fade_len
        arr_can[y_pos + i, :, :] = arr_can[y_pos + i, :, :] * alpha + arr_can[y_pos - (fade_len - i), :, :] * (1.0 - alpha)
    
    canvas_blended = Image.fromarray(np.clip(arr_can, 0, 255).astype(np.uint8)).convert("RGBA")
    stars_upper = create_starfield(TARGET_W, TARGET_H, seed=202, num_stars=180, max_y=480)
    canvas_blended.alpha_composite(stars_upper)
    
    enh = ImageEnhance.Color(canvas_blended.convert("RGB"))
    graded = enh.enhance(1.15)
    
    res = apply_safe_area_vignette(graded, bot_height=420, top_height=140)
    out_file = OUT_DIR / "scene-02-thailand-white-elephant.png"
    res.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_03():
    print("Building Scene 03 (Greece/Rome - Via Lactea)...")
    src = Image.open("scratch/milkyway_raw/poseidon_milkyway.jpg").convert("RGB")
    scale = TARGET_H / src.height
    nw = int(src.width * scale)
    resized = src.resize((nw, TARGET_H), Image.Resampling.LANCZOS)
    
    cx = int((nw - TARGET_W) * 0.48)
    cropped = resized.crop((cx, 0, cx + TARGET_W, TARGET_H))
    
    enh = ImageEnhance.Contrast(cropped)
    contrast = enh.enhance(1.15)
    
    res = apply_safe_area_vignette(contrast, bot_height=420, top_height=140)
    out_file = OUT_DIR / "scene-03-west-milky-way.png"
    res.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_04():
    print("Building Scene 04 (East Asia - Silver River)...")
    src = Image.open("scratch/milkyway_raw/china_nianhu_lake_stars.jpg").convert("RGB")
    scale = TARGET_H / src.height
    nw = int(src.width * scale)
    resized = src.resize((nw, TARGET_H), Image.Resampling.LANCZOS)
    
    cx = int((nw - TARGET_W) * 0.50)
    cropped = resized.crop((cx, 0, cx + TARGET_W, TARGET_H))
    
    arr = np.array(cropped, dtype=np.float32)
    arr[:, :, 0] *= 0.95
    arr[:, :, 1] *= 1.02
    arr[:, :, 2] *= 1.12
    silver_graded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    
    enh = ImageEnhance.Contrast(silver_graded)
    contrast = enh.enhance(1.12)
    
    res = apply_safe_area_vignette(contrast, bot_height=420, top_height=140)
    out_file = OUT_DIR / "scene-04-east-asia-silver-river.png"
    res.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_05():
    print("Building Scene 05 (Sweden - Vintergatan)...")
    # snowy_alps_arches.jpg is 7500x3214
    src = Image.open("scratch/milkyway_raw/snowy_alps_arches.jpg").convert("RGB")
    scale = TARGET_H / src.height
    nw = int(src.width * scale)
    resized = src.resize((nw, TARGET_H), Image.Resampling.LANCZOS)
    
    # Spectacular jagged alpine snow peak meeting the frosty Milky Way arch
    cx = int((nw - TARGET_W) * 0.52)
    cropped = resized.crop((cx, 0, cx + TARGET_W, TARGET_H))
    
    # Frosty cool winter grade
    arr = np.array(cropped, dtype=np.float32)
    arr[:, :, 0] *= 0.96
    arr[:, :, 2] *= 1.08
    frosty = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    
    enh = ImageEnhance.Contrast(frosty)
    contrast = enh.enhance(1.16)
    
    res = apply_safe_area_vignette(contrast, bot_height=420, top_height=140)
    out_file = OUT_DIR / "scene-05-sweden-vintergatan.png"
    res.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def draw_flying_bird(draw, cx, cy, wing_span=30, angle_deg=-25, color=(12, 16, 26, 230)):
    """Draws an authentic, aerodynamic migratory bird silhouette (crane/goose in flight)."""
    # Wing curves using bezier-like polygon points
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    # Local bird coordinates: (0,0) is bird center
    # Head/beak, body, left wing tip, right wing tip, tail
    pts_local = [
        (0, -wing_span * 0.45),      # Beak/head
        (wing_span * 0.15, -wing_span * 0.1), # Right shoulder
        (wing_span * 0.9, -wing_span * 0.25),  # Right wing tip
        (wing_span * 0.4, 0.0),                # Right trailing edge
        (wing_span * 0.1, wing_span * 0.4),   # Tail right
        (0, wing_span * 0.5),                 # Tail tip
        (-wing_span * 0.1, wing_span * 0.4),  # Tail left
        (-wing_span * 0.4, 0.0),               # Left trailing edge
        (-wing_span * 0.9, -wing_span * 0.25), # Left wing tip
        (-wing_span * 0.15, -wing_span * 0.1) # Left shoulder
    ]
    
    # Rotate and translate
    pts_trans = []
    for lx, ly in pts_local:
        rx = lx * cos_a - ly * sin_a + cx
        ry = lx * sin_a + ly * cos_a + cy
        pts_trans.append((rx, ry))
    
    draw.polygon(pts_trans, fill=color)

def build_scene_06():
    print("Building Scene 06 (Finland - Linnunrata / Path of the Birds)...")
    # Base: december_winter_night.jpg (2048x2048) or norway_aurora_milkyway.jpg (2048x1119)
    # december_winter_night has towering pine trees dusted with snow and radiant Milky Way overhead
    src = Image.open("scratch/milkyway_raw/december_winter_night.jpg").convert("RGB")
    scale = TARGET_H / src.height
    nw = int(src.width * scale)
    resized = src.resize((nw, TARGET_H), Image.Resampling.LANCZOS)
    
    cx = int((nw - TARGET_W) * 0.45)
    cropped = resized.crop((cx, 0, cx + TARGET_W, TARGET_H))
    
    canvas = cropped.convert("RGBA")
    
    # Composite graceful flock of migratory birds flying along the Milky Way band toward Lintukoto (South)
    # We place a flight formation soaring upwards/diagonally along the glowing celestial path
    bird_layer = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(bird_layer)
    
    # Migration formation coordinates along the stellar highway
    flock_positions = [
        # (x, y, span, angle)
        (540, 680, 36, -22),   # Leader
        (480, 740, 30, -20),   # Left wing 1
        (420, 800, 26, -18),   # Left wing 2
        (370, 860, 22, -22),   # Left wing 3
        (600, 735, 29, -24),   # Right wing 1
        (660, 790, 25, -21),   # Right wing 2
        (720, 845, 21, -23),   # Right wing 3
        (535, 830, 18, -20),   # Trailing central
        (470, 890, 16, -19),   # Trailing left
        (610, 885, 17, -22),   # Trailing right
    ]
    
    for bx, by, b_span, b_ang in flock_positions:
        draw_flying_bird(b_draw, bx, by, wing_span=b_span, angle_deg=b_ang, color=(16, 22, 34, 235))
    
    # Soft blur to blend bird silhouettes naturally into atmospheric depth
    bird_layer = bird_layer.filter(ImageFilter.GaussianBlur(0.8))
    canvas.alpha_composite(bird_layer)
    
    enh = ImageEnhance.Contrast(canvas.convert("RGB"))
    contrast = enh.enhance(1.14)
    
    res = apply_safe_area_vignette(contrast, bot_height=420, top_height=140)
    out_file = OUT_DIR / "scene-06-finland-birds-pathway.png"
    res.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_07():
    print("Building Scene 07 (Arabic - Darb al-Tabbāna / Haymaker's Way)...")
    # tunisia_desert_milkyway.jpg is 2048x1813
    src = Image.open("scratch/milkyway_raw/tunisia_desert_milkyway.jpg").convert("RGB")
    scale = TARGET_H / src.height
    nw = int(src.width * scale)
    resized = src.resize((nw, TARGET_H), Image.Resampling.LANCZOS)
    
    cx = int((nw - TARGET_W) * 0.48)
    cropped = resized.crop((cx, 0, cx + TARGET_W, TARGET_H))
    
    # Warm golden-amber highlights on galactic dust lanes (like scattered straw in desert)
    arr = np.array(cropped, dtype=np.float32)
    # Warm the midtones slightly
    arr[:, :, 0] *= 1.05  # boost warm gold
    arr[:, :, 1] *= 1.02  # slight green
    warm_desert = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    
    enh = ImageEnhance.Contrast(warm_desert)
    contrast = enh.enhance(1.18)
    
    res = apply_safe_area_vignette(contrast, bot_height=420, top_height=140)
    out_file = OUT_DIR / "scene-07-arabic-haymakers-way.png"
    res.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_08():
    print("Building Scene 08 (Modern Science - Barred Spiral Galaxy Home)...")
    # ngc1300_barred_spiral.jpg is 6637x3787
    src = Image.open("scratch/milkyway_raw/ngc1300_barred_spiral.jpg").convert("RGB")
    scale = TARGET_H / src.height
    nw = int(src.width * scale)
    resized = src.resize((nw, TARGET_H), Image.Resampling.LANCZOS)
    
    # Center crop on the galactic core and magnificent sweeping spiral arms
    cx = int((nw - TARGET_W) * 0.50)
    cropped = resized.crop((cx, 0, cx + TARGET_W, TARGET_H))
    
    enh = ImageEnhance.Contrast(cropped)
    contrast = enh.enhance(1.15)
    
    res = apply_safe_area_vignette(contrast, bot_height=420, top_height=140)
    out_file = OUT_DIR / "scene-08-milky-way-our-home.png"
    res.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_09():
    print("Building Scene 09 (Mamase Outro)...")
    src = "assets/bepicolombo_extreme_mercury_reel/scene-09-mamase-outro.png"
    out_file = OUT_DIR / "scene-09-mamase-outro.png"
    shutil.copy(src, out_file)
    print(f"Copied outro to: {out_file}")

if __name__ == "__main__":
    build_scene_01()
    build_scene_02()
    build_scene_03()
    build_scene_04()
    build_scene_05()
    build_scene_06()
    build_scene_07()
    build_scene_08()
    build_scene_09()
    print("ALL 9 SCENES BUILT SUCCESSFULLY!")
