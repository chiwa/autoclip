import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np

TARGET_W = 1080
TARGET_H = 1920

RAW_DIR = Path("scratch/starship_raw")
OUT_DIR = Path("scratch/starship_master_final")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def apply_safe_darkening(img, fade_len=450, target_mult=0.40):
    arr = np.array(img.convert("RGB"), dtype=np.float32)
    arr[-fade_len:, :, :] *= np.linspace(1.0, target_mult, fade_len)[:, None, None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

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
    w, h = TARGET_W, TARGET_H
    base = Image.open("scratch/full_stack_starship.jpg")
    pw, ph = base.size
    scale_w = 1260 / pw
    sh = int(ph * scale_w)
    base_scaled = base.resize((1260, sh), Image.Resampling.LANCZOS)
    crop_x = int((1260 - w) * 0.45)
    crop_y = int(sh - h)
    canvas = base_scaled.crop((crop_x, crop_y, crop_x + w, crop_y + h)).convert("RGBA")

    # Presenter
    presenter = Image.open("scratch/mamase_presenter_cutout.png").convert("RGBA")
    target_h = 1320
    scale_p = target_h / presenter.height
    target_w = int(presenter.width * scale_p)
    presenter_scaled = presenter.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Warm rim lighting
    p_arr = np.array(presenter_scaled, dtype=np.float32)
    rim_w = int(target_w * 0.25)
    rim_grad = np.linspace(1.0, 0.0, rim_w)[None, :, None]
    p_arr[:, :rim_w, 0] = np.clip(p_arr[:, :rim_w, 0] + 30 * rim_grad[:, :, 0], 0, 255)
    p_arr[:, :rim_w, 1] = np.clip(p_arr[:, :rim_w, 1] + 18 * rim_grad[:, :, 0], 0, 255)
    presenter_graded = Image.fromarray(p_arr.astype(np.uint8))

    pos_x = w - target_w + 35
    pos_y = h - target_h + 20

    # Drop shadow
    p_shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    p_shadow.paste(presenter_graded, (pos_x - 14, pos_y + 10), presenter_graded)
    p_shadow_blur = p_shadow.filter(ImageFilter.GaussianBlur(16))
    canvas.alpha_composite(p_shadow_blur)
    canvas.paste(presenter_graded, (pos_x, pos_y), presenter_graded)

    # Typography
    font_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/SukhumvitSet.ttc", 76, index=4)
    font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/SukhumvitSet.ttc", 60, index=4)

    draw_styled_text(canvas, "STARSHIP V3", font_bold, (75, 140), fill_color=(255, 214, 102, 255), shadow_blur=22, shadow_offset=(0, 6))
    draw_styled_text(canvas, "เป้าหมายคือดาวอังคาร!", font_sub, (75, 235), fill_color=(255, 255, 255, 255), shadow_blur=20, shadow_offset=(0, 5))

    final = apply_safe_darkening(canvas, fade_len=450, target_mult=0.42)
    out_file = OUT_DIR / "scene-01-hook.png"
    final.save(out_file, "PNG")
    print(f"Built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_02():
    w, h = TARGET_W, TARGET_H
    base = Image.open("scratch/liftoff_ift5.jpg")
    bw, bh = base.size # 3648 x 4180
    crop_w = int(bh * 9 / 16) # 2351
    crop_x = int(bw * 0.18) # Center on ascending stack and fire
    cropped = base.crop((crop_x, 0, crop_x + crop_w, bh)).resize((w, h), Image.Resampling.LANCZOS)
    
    enh = ImageEnhance.Contrast(cropped).enhance(1.15)
    enh_c = ImageEnhance.Color(enh).enhance(1.12)
    final = apply_safe_darkening(enh_c, fade_len=450, target_mult=0.40)

    out_file = OUT_DIR / "scene-02-v3-debut-liftoff.png"
    final.save(out_file, "PNG")
    print(f"Built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_03():
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "raptor_diamond_fire.jpg")
    bw, bh = base.size # 4752 x 3168
    crop_w = int(2300 * 9 / 16)
    crop_h = 2300
    crop_x = int(bw * 0.16)
    crop_y = int(bh * 0.12)
    cropped = base.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h)).resize((w, h), Image.Resampling.LANCZOS)

    enh = ImageEnhance.Contrast(cropped).enhance(1.20)
    enh_c = ImageEnhance.Color(enh).enhance(1.22)
    final = apply_safe_darkening(enh_c, fade_len=480, target_mult=0.35)

    out_file = OUT_DIR / "scene-03-raptor3-fury.png"
    final.save(out_file, "PNG")
    print(f"Built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_04():
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "bfr_staging_separation.jpg")
    bw, bh = base.size # 3840 x 2160
    crop_w = int(bh * 9 / 16)
    crop_x = int(bw * 0.45)
    cropped = base.crop((crop_x, 0, crop_x + crop_w, bh)).resize((w, h), Image.Resampling.LANCZOS)

    enh = ImageEnhance.Contrast(cropped).enhance(1.12)
    enh_c = ImageEnhance.Color(enh).enhance(1.12)
    final = apply_safe_darkening(enh_c, fade_len=450, target_mult=0.38)

    out_file = OUT_DIR / "scene-04-staging-anomaly.png"
    final.save(out_file, "PNG")
    print(f"Built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_05():
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "booster_final_approach.jpg")
    bw, bh = base.size # 2648 x 3684
    crop_w = int(bh * 9 / 16)
    crop_x = int(bw * 0.22)
    cropped = base.crop((crop_x, 0, crop_x + crop_w, bh)).resize((w, h), Image.Resampling.LANCZOS)

    enh = ImageEnhance.Contrast(cropped).enhance(1.16)
    enh_c = ImageEnhance.Color(enh).enhance(1.15)
    final = apply_safe_darkening(enh_c, fade_len=450, target_mult=0.38)

    out_file = OUT_DIR / "scene-05-booster-splashdown.png"
    final.save(out_file, "PNG")
    print(f"Built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_06():
    src = Path("scratch/starship_preview/scene-06-starship-orbital-insertion.png")
    dst = OUT_DIR / "scene-06-starship-orbital-insertion.png"
    shutil.copy(src, dst)
    print(f"Copied {dst.name}: {dst.stat().st_size:,} bytes")

def build_scene_07():
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "starlink_orbit.webp")
    bw, bh = base.size # 4000 x 2000
    crop_w = int(bh * 9 / 16)
    crop_x = int(bw * 0.28)
    cropped = base.crop((crop_x, 0, crop_x + crop_w, bh)).resize((w, h), Image.Resampling.LANCZOS)

    enh = ImageEnhance.Contrast(cropped).enhance(1.14)
    enh_c = ImageEnhance.Color(enh).enhance(1.12)
    final = apply_safe_darkening(enh_c, fade_len=450, target_mult=0.38)

    out_file = OUT_DIR / "scene-07-starlink-payload-deploy.png"
    final.save(out_file, "PNG")
    print(f"Built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_08():
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "starship_reentry_plasma.webp")
    bw, bh = base.size # 3027 x 2010
    crop_w = int(bh * 9 / 16)
    crop_x = int(bw * 0.36)
    cropped = base.crop((crop_x, 0, crop_x + crop_w, bh)).resize((w, h), Image.Resampling.LANCZOS).convert("RGBA")

    # Subtle atmospheric plasma ionization glow along heat shield
    plasma = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(plasma)
    px, py = 500, 1580
    for r in range(160, 20, -10):
        alpha = int(75 * (1.0 - r / 160.0))
        p_draw.ellipse([px - r * 1.8, py - r * 0.5, px + r * 1.8, py + r * 0.5], fill=(220, 50, 240, alpha))
    for r in range(80, 10, -8):
        alpha = int(120 * (1.0 - r / 80.0))
        p_draw.ellipse([px - r * 1.4, py - r * 0.3, px + r * 1.4, py + r * 0.3], fill=(255, 140, 255, alpha))
    
    plasma_blur = plasma.filter(ImageFilter.GaussianBlur(14))
    cropped.alpha_composite(plasma_blur)

    enh = ImageEnhance.Contrast(cropped.convert("RGB")).enhance(1.18)
    enh_c = ImageEnhance.Color(enh).enhance(1.16)
    final = apply_safe_darkening(enh_c, fade_len=450, target_mult=0.36)

    out_file = OUT_DIR / "scene-08-hypersonic-plasma-reentry.png"
    final.save(out_file, "PNG")
    print(f"Built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_09():
    w, h = TARGET_W, TARGET_H
    base = Image.open(RAW_DIR / "starship_mars_spacex.jpg")
    bw, bh = base.size # 3840 x 2160
    crop_w = int(bh * 9 / 16)
    crop_x = int(bw * 0.42)
    cropped = base.crop((crop_x, 0, crop_x + crop_w, bh)).resize((w, h), Image.Resampling.LANCZOS)

    enh = ImageEnhance.Contrast(cropped).enhance(1.15)
    enh_c = ImageEnhance.Color(enh).enhance(1.15)
    final = apply_safe_darkening(enh_c, fade_len=450, target_mult=0.38)

    out_file = OUT_DIR / "scene-09-moon-mars-refueling-future.png"
    final.save(out_file, "PNG")
    print(f"Built {out_file.name}: {out_file.stat().st_size:,} bytes")

def build_scene_10():
    src = Path("scratch/starship_preview/scene-10-mamase-outro.png")
    dst = OUT_DIR / "scene-10-mamase-outro.png"
    shutil.copy(src, dst)
    print(f"Copied {dst.name}: {dst.stat().st_size:,} bytes")

def main():
    print("Building complete clean master set...")
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
    print("All 10 scenes built successfully!")

if __name__ == "__main__":
    main()
