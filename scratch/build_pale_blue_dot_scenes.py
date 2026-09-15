import os
import shutil
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np

TARGET_W = 1080
TARGET_H = 1920
RAW_DIR = Path("scratch/pale_blue_dot_raw")
PREVIEW_DIR = Path("scratch/pale_blue_dot_preview")
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

def create_starfield(w=TARGET_W, h=TARGET_H, seed=42, num_stars=300, max_y=1600):
    np.random.seed(seed)
    star_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(star_img)
    for _ in range(num_stars):
        x = np.random.randint(0, w)
        y = np.random.randint(0, max_y)
        b = np.random.randint(140, 255)
        r = np.random.choice([1, 1, 1, 2])
        col = (b, int(b * 0.95), int(b * 1.1), np.random.randint(160, 255))
        draw.ellipse([x, y, x + r, y + r], fill=col)
    return star_img

def apply_safe_area_vignette(img, bot_height=420, top_height=140):
    w, h = img.size
    arr = np.zeros((h, w, 4), dtype=np.float32)
    y_bot = np.linspace(0.0, 1.0, bot_height) ** 1.8 * 210
    arr[-bot_height:, :, 3] = y_bot[:, None]
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
    print("Building Scene 01 (Key Art / Hook)...")
    canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (2, 4, 10, 255))
    stars = create_starfield(TARGET_W, TARGET_H, seed=77, num_stars=450)
    canvas.alpha_composite(stars)
    
    earth = Image.open(RAW_DIR / "earth_apollo17.jpg").convert("RGBA")
    target_earth_sz = 880
    earth_resized = earth.resize((target_earth_sz, target_earth_sz), Image.Resampling.LANCZOS)
    
    # Smooth circular mask to eliminate square border artifact
    c_mask = Image.new("L", (target_earth_sz, target_earth_sz), 0)
    c_draw = ImageDraw.Draw(c_mask)
    c_draw.ellipse([6, 6, target_earth_sz - 6, target_earth_sz - 6], fill=255)
    c_mask = c_mask.filter(ImageFilter.GaussianBlur(2))
    
    orig_alpha = earth_resized.split()[-1]
    combined_alpha = Image.fromarray(np.minimum(np.array(orig_alpha), np.array(c_mask)))
    earth_resized.putalpha(combined_alpha)
    
    glow = Image.new("RGBA", (target_earth_sz + 120, target_earth_sz + 120), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([30, 30, target_earth_sz + 90, target_earth_sz + 90], fill=(40, 120, 230, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(35))
    
    earth_x = -120
    earth_y = 280
    canvas.alpha_composite(glow, (earth_x - 60, earth_y - 60))
    canvas.alpha_composite(earth_resized, (earth_x, earth_y))
    
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
    
    p_arr = np.array(presenter_scaled, dtype=np.float32)
    rim_w = int(target_w * 0.22)
    rim_gradient = np.linspace(1.0, 0.0, rim_w)[None, :, None]
    p_arr[:, :rim_w, 2] = np.clip(p_arr[:, :rim_w, 2] + 28 * rim_gradient[:, :, 0], 0, 255)
    p_arr[:, :rim_w, 1] = np.clip(p_arr[:, :rim_w, 1] + 16 * rim_gradient[:, :, 0], 0, 255)
    presenter_graded = Image.fromarray(p_arr.astype(np.uint8))
    
    pos_x = TARGET_W - target_w + 40
    pos_y = TARGET_H - target_h
    
    p_shadow = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    sh_mask = Image.fromarray((p_arr[:, :, 3] > 10).astype(np.uint8) * 140)
    sh_solid = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 255))
    sh_solid.putalpha(sh_mask)
    p_shadow.paste(sh_solid, (pos_x - 14, pos_y + 10))
    p_shadow = p_shadow.filter(ImageFilter.GaussianBlur(16))
    canvas.alpha_composite(p_shadow)
    canvas.alpha_composite(presenter_graded, (pos_x, pos_y))
    
    font_path = "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc"
    f_topic = ImageFont.truetype(font_path, 44, index=0)
    f_hook = ImageFont.truetype(font_path, 72, index=0)
    
    tx, ty = 64, 110
    draw_styled_text(canvas, "พิกัดเราในจักรวาล", f_topic, (tx, ty), fill_color=(255, 214, 102, 255))
    
    hy = ty + 66
    draw_styled_text(canvas, "ถ้าเอเลียนมาถามทาง...\nโลกเราอยู่ตรงไหน?", f_hook, (tx, hy), fill_color=(255, 255, 255, 255))
    
    res = apply_safe_area_vignette(canvas, bot_height=420, top_height=140)
    out_file = PREVIEW_DIR / "scene-01-hook.png"
    res.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_02():
    print("Building Scene 02 (Zoom out to Solar System)...")
    src = Image.open(RAW_DIR / "voyager_view_solar_system.jpg").convert("RGB")
    crop_h = src.height # 1935
    crop_w = int(crop_h * 9 / 16) # 1088
    # Center crop around Sun and planetary orbits, excluding spacecraft dish on right
    crop_x = 450
    cropped = src.crop((crop_x, 0, crop_x + crop_w, crop_h))
    res = cropped.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    enh = ImageEnhance.Contrast(res).enhance(1.18)
    enh = ImageEnhance.Color(enh).enhance(1.12)
    res_final = apply_safe_area_vignette(enh, bot_height=420, top_height=140)
    out_file = PREVIEW_DIR / "scene-02-solar-system-zoom.png"
    res_final.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_03():
    print("Building Scene 03 (Voyager 1 at 6 Billion km)...")
    src = Image.open(RAW_DIR / "voyager_interstellar_pia17462.jpg").convert("RGB")
    crop_h = 4610
    crop_w = int(crop_h * 9 / 16)
    crop_x = 4200
    cropped = src.crop((crop_x, 0, crop_x + crop_w, crop_h))
    res = cropped.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    enh = ImageEnhance.Contrast(res).enhance(1.12)
    enh = ImageEnhance.Color(enh).enhance(1.1)
    res_final = apply_safe_area_vignette(enh, bot_height=420, top_height=140)
    out_file = PREVIEW_DIR / "scene-03-voyager-at-edge.png"
    res_final.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_04():
    print("Building Scene 04 (Carl Sagan - Turn Camera Back)...")
    src = Image.open(RAW_DIR / "voyager_spacecraft.jpg").convert("RGB")
    crop_w = 850
    crop_h = int(crop_w * 16 / 9) # 1511
    crop_x = 280
    crop_y = 120
    cropped = src.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
    res = cropped.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    
    # Add warm optical flare and diffraction spike on scan platform camera optics
    overlay = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    flare_draw = ImageDraw.Draw(overlay)
    cx, cy = 480, 410
    flare_draw.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(255, 235, 170, 170))
    flare_draw.ellipse([cx - 85, cy - 85, cx + 85, cy + 85], fill=(255, 205, 110, 80))
    flare_draw.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], fill=(255, 180, 80, 30))
    flare_draw.line([(cx - 140, cy), (cx + 140, cy)], fill=(255, 245, 210, 130), width=2)
    flare_draw.line([(cx, cy - 140), (cx, cy + 140)], fill=(255, 245, 210, 130), width=2)
    overlay = overlay.filter(ImageFilter.GaussianBlur(12))
    
    res_rgba = res.convert("RGBA")
    res_rgba.alpha_composite(overlay)
    enh = ImageEnhance.Contrast(res_rgba.convert("RGB")).enhance(1.15)
    res_final = apply_safe_area_vignette(enh, bot_height=420, top_height=140)
    out_file = PREVIEW_DIR / "scene-04-cagan-turn-camera.png"
    res_final.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_05():
    print("Building Scene 05 (Pale Blue Dot)...")
    src = Image.open(RAW_DIR / "pale_blue_dot_revisited.jpg").convert("RGB")
    crop_h = 5175
    crop_w = int(crop_h * 9 / 16)
    crop_x = int(3340 - (crop_w * 0.52))
    crop_x = max(0, min(crop_x, src.width - crop_w))
    cropped = src.crop((crop_x, 0, crop_x + crop_w, crop_h))
    res = cropped.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    enh = ImageEnhance.Contrast(res).enhance(1.22)
    enh = ImageEnhance.Color(enh).enhance(1.15)
    res_final = apply_safe_area_vignette(enh, bot_height=420, top_height=140)
    out_file = PREVIEW_DIR / "scene-05-pale-blue-dot.png"
    res_final.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_06():
    print("Building Scene 06 (Fiery Sunset Earth Limb - Miracle of Life)...")
    src = Image.open(RAW_DIR / "fiery_sunset_earth_limb.jpg").convert("RGB")
    crop_w = int(src.height * 9 / 16) # 1845
    crop_x = int((src.width - crop_w) * 0.48)
    cropped = src.crop((crop_x, 0, crop_x + crop_w, src.height))
    res = cropped.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    enh = ImageEnhance.Contrast(res).enhance(1.18)
    enh = ImageEnhance.Color(enh).enhance(1.12)
    res_final = apply_safe_area_vignette(enh, bot_height=420, top_height=140)
    out_file = PREVIEW_DIR / "scene-06-earth-miracle-life.png"
    res_final.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_07():
    print("Building Scene 07 (Supernova Crab Nebula Filaments - Stardust)...")
    src = Image.open(RAW_DIR / "crab_nebula_supernova.jpg").convert("RGB")
    crop_h = 3864
    crop_w = int(crop_h * 9 / 16) # 2173
    crop_x = int((src.width - crop_w) * 0.5)
    cropped = src.crop((crop_x, 0, crop_x + crop_w, crop_h))
    res = cropped.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    enh = ImageEnhance.Contrast(res).enhance(1.16)
    enh = ImageEnhance.Color(enh).enhance(1.12)
    res_final = apply_safe_area_vignette(enh, bot_height=420, top_height=140)
    out_file = PREVIEW_DIR / "scene-07-supernova-stardust.png"
    res_final.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_08():
    print("Building Scene 08 (ESO VLT Laser - We are a way for cosmos to know itself)...")
    src = Image.open(RAW_DIR / "eso_vlt_laser_milkyway.jpg").convert("RGB")
    scale = TARGET_H / src.height
    w_scaled = int(src.width * scale)
    scaled = src.resize((w_scaled, TARGET_H), Image.Resampling.LANCZOS)
    crop_x = int((w_scaled - TARGET_W) * 0.5)
    cropped = scaled.crop((crop_x, 0, crop_x + TARGET_W, TARGET_H))
    enh = ImageEnhance.Contrast(cropped).enhance(1.16)
    res_final = apply_safe_area_vignette(enh, bot_height=420, top_height=140)
    out_file = PREVIEW_DIR / "scene-08-cosmos-knowing-itself.png"
    res_final.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_09():
    print("Building Scene 09 (Man meets Milky Way - Loving Ourselves)...")
    src = Image.open(RAW_DIR / "man_meets_milky_way.jpg").convert("RGB")
    crop_w = int(src.height * 9 / 16)
    crop_x = int((src.width - crop_w) * 0.48)
    cropped = src.crop((crop_x, 0, crop_x + crop_w, src.height))
    res = cropped.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    enh = ImageEnhance.Contrast(res).enhance(1.18)
    enh = ImageEnhance.Color(enh).enhance(1.12)
    res_final = apply_safe_area_vignette(enh, bot_height=420, top_height=140)
    out_file = PREVIEW_DIR / "scene-09-stardust-within.png"
    res_final.save(out_file, format="PNG", optimize=True)
    print(f"Saved: {out_file}")

def build_scene_10():
    print("Building Scene 10 (Canonical Mamase Outro)...")
    canonical_src = Path("assets/milky_way_names_reel/scene-09-mamase-outro.png")
    out_file = PREVIEW_DIR / "scene-10-mamase-outro.png"
    shutil.copy2(canonical_src, out_file)
    print(f"Copied canonical outro: {out_file}")

def main():
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
    print("\nAll 10 scene previews successfully rendered!")

if __name__ == "__main__":
    main()
