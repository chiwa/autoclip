import json
import os
import shutil
import zipfile
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np

def create_starfield(w, h, seed=42, num_stars=350):
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

def build_scene_01(out_path):
    w, h = 1080, 1920
    canvas = Image.new("RGBA", (w, h), (4, 6, 15, 255))
    
    # Base arrival illustration
    base = Image.open("scratch/bepi_esa/Mercury_arrival.png").convert("RGBA")
    # Scale base to fit width 1080
    scale = 1080 / base.width
    bh = int(base.height * scale)
    base_fit = base.resize((1080, bh), Image.Resampling.LANCZOS)
    
    # Soft vertical fade at bottom of base
    fade_len = 140
    base_arr = np.array(base_fit, dtype=np.float32)
    base_arr[-fade_len:, :, 3] *= np.linspace(1.0, 0.0, fade_len)[:, None]
    base_faded = Image.fromarray(np.clip(base_arr, 0, 255).astype(np.uint8))
    
    # Paste base near top
    canvas.paste(base_faded, (0, 80), base_faded)
    
    # Add starfield layer
    stars = create_starfield(w, h, seed=101, num_stars=250)
    canvas.alpha_composite(stars)
    
    # Presenter Cutout on Right
    cutout = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scratch/mamase_presenter_cutout.png").convert("RGBA")
    target_h = 1320
    scale_p = target_h / cutout.height
    target_w = int(cutout.width * scale_p)
    presenter_fit = cutout.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Position on right side, grounded at bottom
    px = w - target_w + 60
    py = h - target_h
    canvas.paste(presenter_fit, (px, py), presenter_fit)
    
    # Typography in Upper-Left
    font_path = "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc"
    f_topic = ImageFont.truetype(font_path, 42, index=0)
    f_hook = ImageFont.truetype(font_path, 76, index=0)
    
    draw = ImageDraw.Draw(canvas)
    tx, ty = 60, 110
    
    # Topic Shadow & Glow
    draw.text((tx + 2, ty + 2), "ภารกิจสำรวจดาวพุธ", font=f_topic, fill=(0, 0, 0, 220))
    draw.text((tx, ty), "ภารกิจสำรวจดาวพุธ", font=f_topic, fill=(255, 209, 102, 255))
    
    # Hook Text Shadow & Glow
    hook_y = ty + 68
    draw.text((tx + 3, hook_y + 3), "ไปดาวพุธ\nยากกว่าพลูโต?", font=f_hook, fill=(0, 0, 0, 220))
    draw.text((tx, hook_y), "ไปดาวพุธ\nยากกว่าพลูโต?", font=f_hook, fill=(255, 255, 255, 255))
    
    final_rgb = canvas.convert("RGB")
    final_rgb.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 01: {out_path} ({final_rgb.size})")

def build_scene_02(out_path):
    # Gravitational Well Paradox
    w, h = 1080, 1920
    canvas = Image.new("RGB", (w, h), (4, 6, 18))
    draw = ImageDraw.Draw(canvas)
    
    # Starfield
    np.random.seed(202)
    for _ in range(450):
        sx = np.random.randint(0, w)
        sy = np.random.randint(0, h)
        sb = np.random.randint(90, 255)
        r = np.random.choice([1, 1, 1, 2])
        draw.ellipse([sx, sy, sx+r, sy+r], fill=(sb, int(sb*0.95), int(sb*1.1)))
    
    cx, cy = 540, 1150
    
    # Gravitational potential funnel rings (3D perspective)
    for i in range(1, 28):
        r_base = i * 26
        depth = 380 / (1 + (r_base / 75)**1.4)
        pts = []
        for deg in range(0, 360, 4):
            rad = math.radians(deg)
            x = cx + r_base * math.cos(rad) * 1.35
            y = cy + r_base * math.sin(rad) * 0.42 + depth
            pts.append((x, y))
        
        # Color gradient: deep cyan glow
        intensity = max(35, min(240, int(255 - i * 8)))
        ring_col = (int(intensity * 0.25), int(intensity * 0.85), intensity)
        draw.line(pts + [pts[0]], fill=ring_col, width=2)
    
    # Radial curvature spokes
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        pts = []
        for i in range(1, 28):
            r_base = i * 26
            depth = 380 / (1 + (r_base / 75)**1.4)
            x = cx + r_base * math.cos(rad) * 1.35
            y = cy + r_base * math.sin(rad) * 0.42 + depth
            pts.append((x, y))
        spoke_col = (18, 75, 130)
        draw.line(pts, fill=spoke_col, width=1)
    
    # Blazing Sun at center vortex
    for r in range(130, 0, -5):
        glow_col = (int(255 * (1 - r/180)), int(185 * (1 - r/140)), int(45 * (1 - r/130)))
        draw.ellipse([cx - r, cy + 340 - r*0.55, cx + r, cy + 340 + r*0.55], outline=glow_col, width=2)
    draw.ellipse([cx - 40, cy + 340 - 22, cx + 40, cy + 340 + 22], fill=(255, 240, 200))
    
    # Mercury (deep in steep funnel, screaming at 47 km/s)
    mx, my = cx - 150, cy + 240
    # Velocity trail
    draw.arc([mx - 40, my - 20, mx + 40, my + 20], start=120, end=300, fill=(255, 170, 80), width=3)
    draw.ellipse([mx - 15, my - 15, mx + 15, my + 15], fill=(220, 140, 85), outline=(255, 210, 160), width=2)
    
    # Earth (mid slope, blue marble)
    ex, ey = cx + 330, cy + 90
    draw.arc([ex - 50, ey - 25, ex + 50, ey + 25], start=40, end=220, fill=(100, 180, 255), width=2)
    draw.ellipse([ex - 18, ey - 18, ex + 18, ey + 18], fill=(60, 140, 240), outline=(150, 215, 255), width=2)
    
    # Pluto (far out on high flat rim, ice purple)
    px, py = cx - 460, cy - 320
    draw.ellipse([px - 10, py - 10, px + 10, py + 10], fill=(190, 190, 230), outline=(230, 230, 255), width=2)
    
    canvas.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 02: {out_path} ({canvas.size})")

def build_scene_03(out_path):
    # Celestial Billiards: 9 Flybys
    w, h = 1080, 1920
    canvas = Image.new("RGB", (w, h), (3, 5, 14))
    
    # Sourced from ESA flyby illustration & timeline
    base = Image.open("scratch/bepi_esa/BepiColombo_and_Solar_Orbiter_flyby_illustration.png").convert("RGBA")
    # Fit width nicely
    scale = 1080 / base.width
    bh = int(base.height * scale)
    base_fit = base.resize((1080, bh), Image.Resampling.LANCZOS)
    
    # Center vertically around y=360
    fade_len = 120
    base_arr = np.array(base_fit, dtype=np.float32)
    base_arr[:fade_len, :, 3] *= np.linspace(0.0, 1.0, fade_len)[:, None]
    base_arr[-fade_len:, :, 3] *= np.linspace(1.0, 0.0, fade_len)[:, None]
    base_faded = Image.fromarray(np.clip(base_arr, 0, 255).astype(np.uint8))
    
    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.paste(base_faded, (0, 320), base_faded)
    
    # Add starfield
    stars = create_starfield(w, h, seed=303, num_stars=300)
    canvas_rgba.alpha_composite(stars)
    
    # Orbital Trajectory Rings (concentric glowing orbits)
    draw = ImageDraw.Draw(canvas_rgba)
    cx, cy = 540, 720
    
    # Orbits: Mercury (amber), Venus (gold), Earth (cyan)
    draw.ellipse([cx - 220, cy - 140, cx + 220, cy + 140], outline=(230, 140, 70, 160), width=2)
    draw.ellipse([cx - 360, cy - 220, cx + 360, cy + 220], outline=(255, 210, 100, 140), width=2)
    draw.ellipse([cx - 500, cy - 300, cx + 500, cy + 300], outline=(100, 190, 255, 120), width=2)
    
    # Spiraling braking transfer arc (BepiColombo path)
    spiral_pts = []
    for t in np.linspace(0, 1, 150):
        rad = t * 6.5 * math.pi
        r = 500 * (1 - 0.58 * t)
        x = cx + r * math.cos(rad)
        y = cy + r * 0.6 * math.sin(rad)
        spiral_pts.append((x, y))
    
    for i in range(len(spiral_pts) - 1):
        alpha = int(140 + 115 * (i / len(spiral_pts)))
        draw.line([spiral_pts[i], spiral_pts[i+1]], fill=(140, 230, 255, alpha), width=3)
    
    final_rgb = canvas_rgba.convert("RGB")
    final_rgb.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 03: {out_path} ({final_rgb.size})")

def build_scene_04(out_path):
    # Xenon Ion Thrusters (T6 Ion Thruster Firing)
    w, h = 1080, 1920
    canvas = Image.new("RGB", (w, h), (2, 3, 9))
    
    im = Image.open("scratch/bepi_esa/T6_ion_thruster_firing.jpg").convert("RGB")
    # Fit width 1080
    scale = 1080 / im.width
    nh = int(im.height * scale)
    im_fit = im.resize((1080, nh), Image.Resampling.LANCZOS)
    
    # Contrast & color boost for rich electric-blue plasma
    enh = ImageEnhance.Color(im_fit).enhance(1.25)
    enh = ImageEnhance.Contrast(enh).enhance(1.15)
    
    # Feather top & bottom
    im_arr = np.array(enh, dtype=np.float32)
    fade = 100
    im_arr[:fade, :] *= np.linspace(0.0, 1.0, fade)[:, None, None]
    im_arr[-fade:, :] *= np.linspace(1.0, 0.0, fade)[:, None, None]
    im_feathered = Image.fromarray(np.clip(im_arr, 0, 255).astype(np.uint8))
    
    # Place at y=360 (leaving subtitle safe area dark)
    canvas.paste(im_feathered, (0, 360))
    
    # Add starfield around frame
    canvas_rgba = canvas.convert("RGBA")
    stars = create_starfield(w, h, seed=404, num_stars=300)
    canvas_rgba.alpha_composite(stars)
    
    final_rgb = canvas_rgba.convert("RGB")
    final_rgb.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 04: {out_path} ({final_rgb.size})")

def build_scene_05(out_path):
    # Milestone: MTM Separation
    w, h = 1080, 1920
    canvas = Image.new("RGB", (w, h), (3, 4, 11))
    
    # Sourced from Bepi, Mio and MTM complete final flyby / arrival
    im = Image.open("scratch/bepi_esa/Bepi_Mio_and_MTM_complete_their_final_Mercury_flyby.jpg").convert("RGB")
    # Scale to fill height nicely
    scale = 1920 / im.height
    nw = int(im.width * scale)
    im_scaled = im.resize((nw, 1920), Image.Resampling.LANCZOS)
    
    # Horizontal crop with spacecraft stack & separation focus
    x0 = int((nw - 1080) * 0.45)
    crop = im_scaled.crop((x0, 0, x0 + 1080, 1920))
    
    # Subtle vignette at bottom for subtitle safe area
    crop_arr = np.array(crop, dtype=np.float32)
    safe_fade = 350
    crop_arr[-safe_fade:, :] *= np.linspace(1.0, 0.15, safe_fade)[:, None, None]
    
    final = Image.fromarray(np.clip(crop_arr, 0, 255).astype(np.uint8))
    final.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 05: {out_path} ({final.size})")

def build_scene_06(out_path):
    # Twin Orbiters (MPO & Mio in orbit)
    w, h = 1080, 1920
    im = Image.open("scratch/bepi_esa/BepiColombo_hugs_Mercury.png").convert("RGB")
    # 1920x1920 -> center crop horizontally to 1080x1920
    x0 = (im.width - 1080) // 2
    crop = im.crop((x0, 0, x0 + 1080, 1920))
    
    # Contrast enhance for crisp spacecraft details & planetary horizon
    enh = ImageEnhance.Contrast(crop).enhance(1.15)
    
    # Subtitle safe area fade at bottom
    arr = np.array(enh, dtype=np.float32)
    safe_fade = 300
    arr[-safe_fade:, :] *= np.linspace(1.0, 0.2, safe_fade)[:, None, None]
    
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    final.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 06: {out_path} ({final.size})")

def build_scene_07(out_path):
    # Extreme Mercury: Shadowy North Pole & Craters
    w, h = 1080, 1920
    im = Image.open("scratch/bepi_esa/Mercury_s_shadowy_north_pole_revealed_by_M-CAM_1.jpg").convert("RGB")
    # 1920x1920 -> center crop horizontally to 1080x1920
    x0 = (im.width - 1080) // 2
    crop = im.crop((x0, 0, x0 + 1080, 1920))
    
    # Contrast enhancement to highlight deep pitch-black crater shadows and brilliant sunlit rims
    enh = ImageEnhance.Contrast(crop).enhance(1.22)
    
    # Safe area dimming at bottom
    arr = np.array(enh, dtype=np.float32)
    safe_fade = 320
    arr[-safe_fade:, :] *= np.linspace(1.0, 0.15, safe_fade)[:, None, None]
    
    final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    final.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 07: {out_path} ({final.size})")

def build_scene_08(out_path):
    # Philosophical Climax: BepiColombo in orbit, cosmic wonder
    w, h = 1080, 1920
    canvas = Image.new("RGB", (w, h), (3, 5, 12))
    
    im = Image.open("scratch/bepi_esa/BepiColombo_approaches_Mercury.png").convert("RGB")
    scale = 1080 / im.width
    nh = int(im.height * scale)
    im_fit = im.resize((1080, nh), Image.Resampling.LANCZOS)
    
    # Feather top and bottom
    arr = np.array(im_fit, dtype=np.float32)
    fade = 120
    arr[:fade, :] *= np.linspace(0.0, 1.0, fade)[:, None, None]
    arr[-fade:, :] *= np.linspace(1.0, 0.0, fade)[:, None, None]
    im_faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    
    canvas.paste(im_faded, (0, 320))
    
    # Deep space stars
    canvas_rgba = canvas.convert("RGBA")
    stars = create_starfield(w, h, seed=808, num_stars=320)
    canvas_rgba.alpha_composite(stars)
    
    final = canvas_rgba.convert("RGB")
    final.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 08: {out_path} ({final.size})")

def build_scene_09(out_path):
    # Canonical Outro
    src = "dist/mamase-james-webb-time-machine-reel-v1/images/scene-11-mamase-outro.png"
    shutil.copy(src, out_path)
    im = Image.open(out_path)
    print(f"Copied Scene 09 Outro: {out_path} ({im.size})")

def main():
    assets_dir = Path("assets/bepicolombo_mercury_reel")
    stage_dir = Path("dist/mamase-bepicolombo-mercury-reel-v1")
    stage_images_dir = stage_dir / "images"
    
    assets_dir.mkdir(parents=True, exist_ok=True)
    stage_images_dir.mkdir(parents=True, exist_ok=True)
    
    scenes_info = [
        ("scene-01-hook.png", build_scene_01),
        ("scene-02-gravity-well-paradox.png", build_scene_02),
        ("scene-03-celestial-billiards.png", build_scene_03),
        ("scene-04-ion-thrusters.png", build_scene_04),
        ("scene-05-mtm-separation.png", build_scene_05),
        ("scene-06-twin-orbiters.png", build_scene_06),
        ("scene-07-extreme-mercury.png", build_scene_07),
        ("scene-08-philosophical-climax.png", build_scene_08),
        ("scene-09-mamase-outro.png", build_scene_09),
    ]
    
    for filename, builder in scenes_info:
        asset_target = assets_dir / filename
        stage_target = stage_images_dir / filename
        builder(asset_target)
        shutil.copy(asset_target, stage_target)
    
    print("\n--- All 9 Scene Images Generated and Staged ---")

if __name__ == "__main__":
    main()
