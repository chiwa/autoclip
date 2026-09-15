import json
import os
import shutil
import zipfile
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np
from app.services.package_service import PackageService

TARGET_W = 1080
TARGET_H = 1920

def create_starfield(w=TARGET_W, h=TARGET_H, seed=42, num_stars=360, max_y=1500):
    np.random.seed(seed)
    star_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(star_img)
    for _ in range(num_stars):
        x = np.random.randint(0, w)
        y = np.random.randint(0, max_y)
        b = np.random.randint(80, 255)
        r = np.random.choice([1, 1, 1, 2])
        col = (b, int(b * 0.95), int(b * 1.1), np.random.randint(140, 255))
        draw.ellipse([x, y, x + r, y + r], fill=col)
    return star_img

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

def build_scene_01(out_path):
    """Scene 01: Narrative Key Art (Earth-Moon cislunar space, satellites, Mamase presenter, and Thai typography)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    # 1. Earth & satellite orbit background
    base = Image.open("assets/parker_solar_probe_reel/scene-10-space-weather-earth.png").convert("RGBA")
    # Scale to fill upper/mid region
    base_fit = base.resize((w, h), Image.Resampling.LANCZOS)
    
    arr_b = np.array(base_fit, dtype=np.float32)
    # Darken bottom for presenter & subtitle safe area
    arr_b[-550:, :, 3] *= np.linspace(1.0, 0.0, 550)[:, None]
    base_faded = Image.fromarray(np.clip(arr_b, 0, 255).astype(np.uint8))
    canvas.paste(base_faded, (0, 0), base_faded)
    
    # 2. Add satellite in upper-center
    sat = Image.open("assets/solar_storm_documentary/scene_24_solar_observing_spacecraft.png").convert("RGBA")
    sat_crop = sat.crop((300, 100, 1600, 980))
    sat_fit = sat_crop.resize((720, 480), Image.Resampling.LANCZOS)
    arr_sat = np.array(sat_fit, dtype=np.float32)
    # Circular feathered edge
    fade_s = 60
    arr_sat[:fade_s, :, 3] *= np.linspace(0.0, 1.0, fade_s)[:, None]
    arr_sat[-fade_s:, :, 3] *= np.linspace(1.0, 0.0, fade_s)[:, None]
    arr_sat[:, :fade_s, 3] *= np.linspace(0.0, 1.0, fade_s)[None, :]
    arr_sat[:, -fade_s:, 3] *= np.linspace(1.0, 0.0, fade_s)[None, :]
    sat_faded = Image.fromarray(np.clip(arr_sat, 0, 255).astype(np.uint8))
    canvas.paste(sat_faded, (40, 360), sat_faded)
    
    # 3. Add cosmic stars
    canvas.alpha_composite(create_starfield(w, h, seed=101, num_stars=280))
    
    # 4. Presenter Cutout on Right
    cutout = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scratch/mamase_presenter_cutout.png").convert("RGBA")
    alpha = np.array(cutout.split()[-1])
    y_indices, x_indices = np.where(alpha > 10)
    x_min, x_max = x_indices.min(), x_indices.max()
    y_min, y_max = y_indices.min(), y_indices.max()
    presenter_cropped = cutout.crop((x_min, y_min, x_max + 1, y_max + 1))
    
    target_h = 1260
    scale_p = target_h / presenter_cropped.height
    target_w = int(presenter_cropped.width * scale_p)
    presenter_scaled = presenter_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Gentle cyan/blue rim light on presenter left side matching Earth orbit
    p_arr = np.array(presenter_scaled, dtype=np.float32)
    rim_w = int(target_w * 0.25)
    rim_gradient = np.linspace(1.0, 0.0, rim_w)[None, :, None]
    p_arr[:, :rim_w, 0] = np.clip(p_arr[:, :rim_w, 0] + 15 * rim_gradient[:, :, 0], 0, 255)
    p_arr[:, :rim_w, 1] = np.clip(p_arr[:, :rim_w, 1] + 25 * rim_gradient[:, :, 0], 0, 255)
    p_arr[:, :rim_w, 2] = np.clip(p_arr[:, :rim_w, 2] + 35 * rim_gradient[:, :, 0], 0, 255)
    presenter_graded = Image.fromarray(p_arr.astype(np.uint8))
    
    pos_x = w - target_w + 50
    pos_y = h - target_h
    
    p_shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    p_shadow.paste(presenter_graded, (pos_x - 14, pos_y + 8), presenter_graded)
    p_shadow_blur = p_shadow.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(p_shadow_blur)
    canvas.paste(presenter_graded, (pos_x, pos_y), presenter_graded)
    
    # 5. Typography at top-left
    font_path = "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc"
    f_topic = ImageFont.truetype(font_path, 42, index=0)
    f_hook = ImageFont.truetype(font_path, 72, index=0)
    
    tx, ty = 60, 110
    draw_styled_text(canvas, "ทางด่วนอวกาศโลก-ดวงจันทร์", f_topic, (tx, ty), fill_color=(255, 214, 102, 255))
    
    hy = ty + 68
    draw_styled_text(canvas, "ฝูงดาวเทียมจิ๋ว C3...\nไทยร่วมลุย!", f_hook, (tx, hy), fill_color=(255, 255, 255, 255))
    
    final_rgb = canvas.convert("RGB")
    final_rgb.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 01: {out_path} ({final_rgb.size}, {os.path.getsize(out_path):,} bytes)")

def build_scene_02(out_path):
    """Scene 02: The Vast Cislunar Frontier (2,000,000 km space between Earth and Moon)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    # Interplanetary transit panorama
    base = Image.open("assets/solar_storm_documentary/scene_06_interplanetary_transit.png").convert("RGBA")
    scale = 1600 / base.height
    bw = int(base.width * scale)
    base_fit = base.resize((bw, 1600), Image.Resampling.LANCZOS)
    
    cx = int((bw - w) * 0.5)
    base_crop = base_fit.crop((cx, 0, cx + w, 1600))
    
    arr = np.array(base_crop, dtype=np.float32)
    arr[:120, :, 3] *= np.linspace(0.0, 1.0, 120)[:, None]
    arr[-320:, :, 3] *= np.linspace(1.0, 0.0, 320)[:, None]
    base_faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    
    canvas.paste(base_faded, (0, 60), base_faded)
    canvas.alpha_composite(create_starfield(w, h, seed=202, num_stars=400))
    
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 02: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_03(out_path):
    """Scene 03: The Invisible Dangers (Solar storms and cosmic radiation in unprotected cislunar space)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (4, 4, 10, 255))
    
    # 1. Solar flare & CME expansion at top
    flare = Image.open("assets/solar_storm_documentary/scene_04_solar_flare.png").convert("RGBA")
    scale_f = (w + 200) / flare.width
    fh = int(flare.height * scale_f)
    flare_fit = flare.resize((w + 200, fh), Image.Resampling.LANCZOS).crop((100, 0, 100 + w, fh))
    
    arr_f = np.array(flare_fit, dtype=np.float32)
    arr_f[-320:, :, 3] *= np.linspace(1.0, 0.0, 320)[:, None]
    flare_faded = Image.fromarray(np.clip(arr_f, 0, 255).astype(np.uint8))
    canvas.paste(flare_faded, (0, 0), flare_faded)
    
    # 2. Earth magnetic boundary at lower-mid
    shield = Image.open("assets/solar_storm_documentary/scene_27_earth_magnetic_shield.png").convert("RGBA")
    scale_s = 1350 / shield.height
    sw = int(shield.width * scale_s)
    shield_fit = shield.resize((sw, 1350), Image.Resampling.LANCZOS)
    
    cx = (sw - w) // 2
    shield_crop = shield_fit.crop((cx, 0, cx + w, 1350))
    arr_s = np.array(shield_crop, dtype=np.float32)
    arr_s[:220, :, 3] *= np.linspace(0.0, 1.0, 220)[:, None]
    arr_s[-350:, :, 3] *= np.linspace(1.0, 0.0, 350)[:, None]
    shield_faded = Image.fromarray(np.clip(arr_s, 0, 255).astype(np.uint8))
    canvas.paste(shield_faded, (0, 480), shield_faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=303, num_stars=320, max_y=1400))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 03: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_04(out_path):
    """Scene 04: Enter C3: The 30-CubeSat Swarm (Compact satellites in precise formation)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    # High-tech satellite in deep space
    sat = Image.open("assets/solar_storm_documentary/scene_22_low_orbit_satellite.png").convert("RGBA")
    scale = 1600 / sat.height
    bw = int(sat.width * scale)
    sat_fit = sat.resize((bw, 1600), Image.Resampling.LANCZOS)
    
    cx = int((bw - w) * 0.45)
    sat_crop = sat_fit.crop((cx, 0, cx + w, 1600))
    
    arr = np.array(sat_crop, dtype=np.float32)
    arr[:120, :, 3] *= np.linspace(0.0, 1.0, 120)[:, None]
    arr[-300:, :, 3] *= np.linspace(1.0, 0.0, 300)[:, None]
    sat_faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(sat_faded, (0, 80), sat_faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=404, num_stars=350))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 04: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_05(out_path):
    """Scene 05: Supporting the Lunar Base (Moon's south pole craters & satellite support)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    # 1. Authentic polar cratered lunar terrain (1920x1920)
    moon = Image.open("scratch/bepi_esa/Mercury_s_shadowy_north_pole_revealed_by_M-CAM_1.jpg").convert("RGBA")
    scale_m = 1350 / moon.height
    mw = int(moon.width * scale_m)
    moon_fit = moon.resize((mw, 1350), Image.Resampling.LANCZOS)
    
    cx = (mw - w) // 2
    moon_crop = moon_fit.crop((cx, 0, cx + w, 1350))
    arr_m = np.array(moon_crop, dtype=np.float32)
    arr_m[:160, :, 3] *= np.linspace(0.0, 1.0, 160)[:, None]
    arr_m[-350:, :, 3] *= np.linspace(1.0, 0.0, 350)[:, None]
    moon_faded = Image.fromarray(np.clip(arr_m, 0, 255).astype(np.uint8))
    canvas.paste(moon_faded, (0, 480), moon_faded)
    
    # 2. Orbital satellite in upper sky surveying the base
    sat = Image.open("assets/solar_storm_documentary/scene_24_solar_observing_spacecraft.png").convert("RGBA")
    sat_crop = sat.crop((350, 120, 1550, 960))
    sat_fit = sat_crop.resize((680, 470), Image.Resampling.LANCZOS)
    arr_s = np.array(sat_fit, dtype=np.float32)
    fade_s = 50
    arr_s[:fade_s, :, 3] *= np.linspace(0.0, 1.0, fade_s)[:, None]
    arr_s[-fade_s:, :, 3] *= np.linspace(1.0, 0.0, fade_s)[:, None]
    arr_s[:, :fade_s, 3] *= np.linspace(0.0, 1.0, fade_s)[None, :]
    arr_s[:, -fade_s:, 3] *= np.linspace(1.0, 0.0, fade_s)[None, :]
    sat_faded = Image.fromarray(np.clip(arr_s, 0, 255).astype(np.uint8))
    canvas.paste(sat_faded, (200, 120), sat_faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=505, num_stars=380, max_y=700))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 05: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_06(out_path):
    """Scene 06: Thailand & Global Partnership (International ground station & satellite network)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    # International space operations center
    base = Image.open("assets/solar_storm_documentary/scene_23_space_weather_center.png").convert("RGBA")
    scale = 1600 / base.height
    bw = int(base.width * scale)
    base_fit = base.resize((bw, 1600), Image.Resampling.LANCZOS)
    
    cx = int((bw - w) * 0.45)
    base_crop = base_fit.crop((cx, 0, cx + w, 1600))
    
    arr = np.array(base_crop, dtype=np.float32)
    arr[:120, :, 3] *= np.linspace(0.0, 1.0, 120)[:, None]
    arr[-320:, :, 3] *= np.linspace(1.0, 0.0, 320)[:, None]
    base_faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(base_faded, (0, 80), base_faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=606, num_stars=300))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 06: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_07(out_path):
    """Scene 07: Cosmic Guardians & Gamma-Ray Discovery (Detecting distant cosmic Gamma-Ray Bursts)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    # Colossal cosmic burst / energetic nebula
    base = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.tempmediaStorage/media_1788566981436.png").convert("RGBA")
    base_fit = base.resize((w, h), Image.Resampling.LANCZOS)
    arr = np.array(base_fit, dtype=np.float32)
    arr[-320:, :, 3] *= np.linspace(1.0, 0.0, 320)[:, None]
    base_faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(base_faded, (0, 0), base_faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=707, num_stars=320, max_y=1400))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 07: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_08(out_path):
    """Scene 08: Philosophical Climax (Earth and Moon together in deep cosmic harmony)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    # Sublime view of Earth & Moon in space
    base = Image.open("assets/parker_solar_probe_reel/scene-10-space-weather-earth.png").convert("RGBA")
    base_fit = base.resize((w, h), Image.Resampling.LANCZOS)
    arr = np.array(base_fit, dtype=np.float32)
    arr[-340:, :, 3] *= np.linspace(1.0, 0.0, 340)[:, None]
    
    # Warm golden/peaceful grade
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.08 + 8, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.04 + 4, 0, 255)
    
    base_faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(base_faded, (0, 0), base_faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=808, num_stars=380, max_y=1400))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 08: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_09(out_path):
    """Scene 09: Canonical Mamase Outro."""
    src = Path("dist/mamase-james-webb-time-machine-reel-v1/images/scene-11-mamase-outro.png")
    if not src.exists():
        src = Path("dist/mamase-roman-space-telescope-wan-v2/images/scene-08-mamase-outro.png")
    shutil.copy(src, out_path)
    print(f"Copied Scene 09 Outro: {out_path} ({os.path.getsize(out_path):,} bytes)")

def create_complete_package():
    print("=== 1. Setting up paths ===")
    root = Path("/Users/zengcode/projects/autoclip")
    asset_dir = root / "assets" / "cislunar_c3_constellation_reel"
    staging_dir = root / "dist" / "mamase-cislunar-c3-constellation-reel-v1"
    staging_images = staging_dir / "images"
    zip_path = root / "dist" / "mamase-cislunar-c3-constellation-reel-v1.zip"
    
    asset_dir.mkdir(parents=True, exist_ok=True)
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_images.mkdir(parents=True, exist_ok=True)
    
    print("=== 2. Generating Master Assets ===")
    builders = [
        ("scene-01-hook.png", build_scene_01),
        ("scene-02-cislunar-frontier.png", build_scene_02),
        ("scene-03-invisible-dangers.png", build_scene_03),
        ("scene-04-cubesat-swarm.png", build_scene_04),
        ("scene-05-lunar-base-support.png", build_scene_05),
        ("scene-06-thailand-global-partnership.png", build_scene_06),
        ("scene-07-gamma-ray-discovery.png", build_scene_07),
        ("scene-08-philosophical-climax.png", build_scene_08),
        ("scene-09-mamase-outro.png", build_scene_09),
    ]
    
    for filename, fn in builders:
        master_dst = asset_dir / filename
        staging_dst = staging_images / filename
        fn(master_dst)
        shutil.copy(master_dst, staging_dst)
        print(f"Copied {filename} to staging.")

    print("=== 3. Writing video-metadata.json ===")
    metadata = {
        "title": "ทางด่วนอวกาศโลก-ดวงจันทร์! ฝูงดาวเทียมจิ๋ว C3... ไทยร่วมลุยด้วย (2 ล้าน กม.)",
        "description": "จีนประกาศเปิดตัวโครงการ Cislunar CubeSat Constellation (C3) สร้างเครือข่ายดาวเทียมตรวจการณ์อัจฉริยะ 30 ลำ ครอบคลุมอวกาศระหว่างโลกถึงดวงจันทร์ไกลกว่า 2 ล้านกิโลเมตร!\n\nทำหน้าที่เฝ้าระวังพายุสุริยะ คอยชี้เป้าแหล่งน้ำแข็งขั้วใต้ดวงจันทร์ สนับสนุนสถานีวิจัยนานาชาติ ILRS ก่อนปี 2030 และตรวจจับระเบิดรังสีแกมมาลึกสุดจักรวาล ที่น่าภาคภูมิใจคือ 'ประเทศไทย' ได้เข้าร่วมเป็นพันธมิตรกลุ่มแรกของภารกิจประวัติศาสตร์นี้ด้วยครับ\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#C3Constellation #Cislunar #CubeSat #ดวงจันทร์ #อวกาศ #ดาราศาสตร์ #วิทยาศาสตร์ #NARIT #GISTDA #ไทยในอวกาศ #Mamase #จักรวาลของใจ"
    }
    with open(staging_dir / "video-metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print("Created video-metadata.json")

    print("=== 4. Writing script.json ===")
    script = {
        "project": {
            "id": "mamase-cislunar-c3-constellation-reel-v1",
            "title": "ทางด่วนอวกาศโลก-ดวงจันทร์: ฝูงดาวเทียม C3",
            "language": "th-TH",
            "resolution": "1080x1920",
            "fps": 30
        },
        "voice": {
            "provider": "google-gemini",
            "voice": "Fenrir",
            "speed": 1.3,
            "style_prompt": "Read aloud like a charismatic science storyteller with a playful personality. Sound curious, friendly, slightly cheeky, and genuinely excited by surprising facts. Keep the delivery natural and conversational, with small pauses for comedic timing and emphasis. Never sound like a news anchor. Keep the delivery energetic, clear, playful, warm, and reassuring. Make the listener feel relaxed and curious, never rushed, tense, or overly dramatic."
        },
        "scenes": [
            {
                "id": "scene-01-hook",
                "image": "images/scene-01-hook.png",
                "narration": "สวัสดีครับ ยินดีต้อนรับสู่ Mamase จักรวาลของใจ ห้วงอวกาศระหว่างโลกกับดวงจันทร์ที่เคยว่างเปล่า กำลังจะกลายเป็น 'เครือข่ายอัจฉริยะ' ด้วยฝูงดาวเทียมจิ๋ว 30 ลำ... และรู้ไหมครับว่า ประเทศไทยเราได้ร่วมภารกิจนี้ด้วย!",
                "tts_text": "สวัสดีครับ ยินดีต้อนรับสู่ มามาเซ่ จักรวาลของใจ ห้วงอวกาศระหว่างโลกกับดวงจันทร์ที่เคยว่างเปล่า กำลังจะกลายเป็น เครือข่ายอัจฉริยะ ด้วยฝูงดาวเทียมจิ๋ว สามสิบ ลำ... และรู้ไหมครับว่า ประเทศไทยเราได้ร่วมภารกิจนี้ด้วย!",
                "subtitle": "ฝูงดาวเทียม C3 เครือข่ายทางด่วนโลก-ดวงจันทร์",
                "motion": "cinematic_push_in",
                "motion_speed": "normal",
                "motion_intensity": 0.2,
                "focus": "right",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Use the canonical Mamase anime presenter identity, friendly Thai male with tousled black hair, thin rectangular glasses and navy blazer, face-forward on the right for a talking shot. High-tech CubeSat satellites in cislunar space between blue Earth and glowing Moon, elegant Thai hook text in upper left. Subtle natural head movement and gentle pointing gesture, stable composition.",
                    "negative_prompt": "extra person, extra text, watermark, logo, distorted face, distorted hands, duplicated fingers, blurry spacecraft, flicker, jitter, sudden camera movement",
                    "seed": 901,
                    "frames": 81,
                    "steps": 25,
                    "lip_sync": True,
                    "character_id": "mamase-presenter-v1"
                }
            },
            {
                "id": "scene-02-cislunar-frontier",
                "image": "images/scene-02-cislunar-frontier.png",
                "narration": "พื้นที่ที่เรียกว่า 'ซีสลูนาร์' ครอบคลุมตั้งแต่เหนือวงโคจรโลกออกไปถึง 2 ล้านกิโลเมตร นี่คือเส้นทางยุทธศาสตร์สำคัญที่มนุษย์กำลังจะใช้เดินทางไปกลับดวงจันทร์ในทศวรรษนี้ครับ",
                "tts_text": "พื้นที่ที่เรียกว่า ซีสลูนาร์ ครอบคลุมตั้งแต่เหนือวงโคจรโลกออกไปถึง สอง ล้านกิโลเมตร นี่คือเส้นทางยุทธศาสตร์สำคัญที่มนุษย์กำลังจะใช้เดินทางไปกลับดวงจันทร์ในทศวรรษนี้ครับ",
                "subtitle": "ซีสลูนาร์: เขตอวกาศ 2 ล้านกิโลเมตร",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic space documentary view of vast cislunar space between planet Earth and the Moon spanning 2 million kilometers, orbital highway trajectories connecting the two worlds in deep cosmos, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, flicker, jitter",
                    "seed": 902,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-03-invisible-dangers",
                "image": "images/scene-03-invisible-dangers.png",
                "narration": "แต่การอยู่นอกร่มเงาสนามแม่เหล็กโลกนั้นอันตรายมาก พายุสุริยะ รังสีคอสมิก และสะเก็ดดาว อาจทำลายยานหรือเป็นอันตรายถึงชีวิตนักบินอวกาศได้ในเสี้ยววินาที",
                "tts_text": "แต่การอยู่นอกร่มเงาสนามแม่เหล็กโลกนั้นอันตรายมาก พายุสุริยะ รังสีคอสมิก และสะเก็ดดาว อาจทำลายยานหรือเป็นอันตรายถึงชีวิตนักบินอวกาศได้ในเสี้ยววินาที",
                "subtitle": "อันตรายจากพายุสุริยะนอกสนามแม่เหล็กโลก",
                "motion": "cinematic_pull_out",
                "motion_speed": "slow",
                "motion_intensity": 0.16,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic space science documentary showing violent solar storm and cosmic radiation particles bombarding deep space outside Earth magnetic shield, dramatic space weather physics, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, explosion, flicker, jitter",
                    "seed": 903,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-04-cubesat-swarm",
                "image": "images/scene-04-cubesat-swarm.png",
                "narration": "จีนจึงเปิดตัวโครงการ C3 ส่งฝูงดาวเทียมจิ๋วขนาดไม่เกิน 30 กิโลกรัม จำนวน 30 ลำ กระจายตัวเป็นโครงข่ายตรวจวัดสภาพแวดล้อมอวกาศตลอด 24 ชั่วโมง",
                "tts_text": "จีนจึงเปิดตัวโครงการ ซีทรี ส่งฝูงดาวเทียมจิ๋วขนาดไม่เกิน สามสิบ กิโลกรัม จำนวน สามสิบ ลำ กระจายตัวเป็นโครงข่ายตรวจวัดสภาพแวดล้อมอวกาศตลอด ยี่สิบสี่ ชั่วโมง",
                "subtitle": "ฝูงคิวบ์แซต 30 ลำ เฝ้าระวังภัย 24 ชม.",
                "motion": "gentle_float",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Cinematic aerospace engineering shot of sleek modern 30-kilogram CubeSats flying in constellation formation in deep space, solar panels deployed, micro-thrusters, scientific sensors glistening in sunlight, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, damage, flicker, jitter",
                    "seed": 904,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-05-lunar-base-support",
                "image": "images/scene-05-lunar-base-support.png",
                "narration": "ฝูงดาวเทียมนี้จะทำหน้าที่ทั้งเป็นสถานีตรวจสภาพอวกาศ คอยชี้เป้าแหล่งน้ำแข็ง และสนับสนุนการสร้างสถานีวิจัยถาวรบนดวงจันทร์ของมนุษย์ก่อนปี 2030",
                "tts_text": "ฝูงดาวเทียมนี้จะทำหน้าที่ทั้งเป็นสถานีตรวจสภาพอวกาศ คอยชี้เป้าแหล่งน้ำแข็ง และสนับสนุนการสร้างสถานีวิจัยถาวรบนดวงจันทร์ของมนุษย์ก่อนปี สองพันสามสิบ",
                "subtitle": "รองรับการสร้างสถานีวิจัยบนดวงจันทร์",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic documentary view of lunar south pole craters with permanent shadows, CubeSat satellite surveying overhead for water ice, supporting future international lunar research station, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, fire, explosion, flicker, jitter",
                    "seed": 905,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-06-thailand-global-partnership",
                "image": "images/scene-06-thailand-global-partnership.png",
                "narration": "ที่พิเศษที่สุดคือ นี่ไม่ใช่ภารกิจเดี่ยว แต่เปิดกว้างให้ทั่วโลก และนักวิทยาศาสตร์ไทยเราก็เป็นหนึ่งในกลุ่มแรก ๆ ที่เข้าร่วมโครงการประวัติศาสตร์นี้ครับ",
                "tts_text": "ที่พิเศษที่สุดคือ นี่ไม่ใช่ภารกิจเดี่ยว แต่เปิดกว้างให้ทั่วโลก และนักวิทยาศาสตร์ไทยเราก็เป็นหนึ่งในกลุ่มแรก ๆ ที่เข้าร่วมโครงการประวัติศาสตร์นี้ครับ",
                "subtitle": "ไทยร่วมเป็นหนึ่งในชาติบุกเบิกโครงการ",
                "motion": "documentary_pan",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic documentary shot of modern international space operations center and satellite tracking screens, global scientific partnership, deep space communication dish under starry sky, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, flicker, jitter",
                    "seed": 906,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-07-gamma-ray-discovery",
                "image": "images/scene-07-gamma-ray-discovery.png",
                "narration": "นอกจากดูแลความปลอดภัยให้นักบินอวกาศแล้ว เครือข่ายนี้ยังทำหน้าที่เป็นกล้องโทรทรรศน์ขนาดยักษ์ คอยตรวจจับการระเบิดของรังสีแกมมาที่ไกลโพ้นในจักรวาลอีกด้วย",
                "tts_text": "นอกจากดูแลความปลอดภัยให้นักบินอวกาศแล้ว เครือข่ายนี้ยังทำหน้าที่เป็นกล้องโทรทรรศน์ขนาดยักษ์ คอยตรวจจับการระเบิดของรังสีแกมมาที่ไกลโพ้นในจักรวาลอีกด้วย",
                "subtitle": "ตรวจจับการระเบิดรังสีแกมมาลึกสุดจักรวาล",
                "motion": "cinematic_pull_out",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic astrophysical documentary shot of an ultra-bright Gamma-Ray Burst explosion in distant deep space, relativistic jet cutting through cosmic darkness, detected by deep space satellite network, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, explosion, flicker, jitter",
                    "seed": 907,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-08-philosophical-climax",
                "image": "images/scene-08-philosophical-climax.png",
                "narration": "การก้าวออกจากโลกสู่ดวงจันทร์ จะไม่ได้มีเพียงผู้กล้าลำพังอีกต่อไป แต่มีโครงข่ายความร่วมมือของมวลมนุษยชาติ คอยส่องทางและปกป้องพวกเราอยู่เสมอครับ",
                "tts_text": "การก้าวออกจากโลกสู่ดวงจันทร์ จะไม่ได้มีเพียงผู้กล้าลำพังอีกต่อไป แต่มีโครงข่ายความร่วมมือของมวลมนุษยชาติ คอยส่องทางและปกป้องพวกเราอยู่เสมอครับ",
                "subtitle": "ก้าวสู่ดวงจันทร์ด้วยความร่วมมือของมนุษยชาติ",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "none",
                "wan": {
                    "prompt": "Sublime, peaceful, inspiring space documentary shot of planet Earth and Moon floating together in cosmic space, subtle interconnected golden orbital network, human unity and achievement, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, flicker, jitter",
                    "seed": 908,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-09-mamase-outro",
                "image": "images/scene-09-mamase-outro.png",
                "narration": "ค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ",
                "tts_text": "ค้นพบโลก ค้นพบใจ กับ มามาเซ่ จักรวาลของใจ",
                "subtitle": "ค้นพบโลก ค้นพบใจ\nMamase จักรวาลของใจ",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.1,
                "focus": "center",
                "transition": "none",
                "wan": {
                    "prompt": "Mamase brand outro, glowing cyan orbiting planet in dark navy space, peaceful and contemplative.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, extra planet, extra stars, flicker, jitter",
                    "seed": 98,
                    "frames": 81,
                    "lip_sync": False
                }
            }
        ]
    }
    with open(staging_dir / "script.json", "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print("Created script.json")

    print("=== 5. Assembling ZIP package ===")
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root_dir, _, files in os.walk(staging_dir):
            for file in files:
                full_path = Path(root_dir) / file
                rel_path = full_path.relative_to(staging_dir)
                zf.write(full_path, arcname=str(rel_path))
    print(f"Created ZIP package: {zip_path} ({zip_path.stat().st_size:,} bytes)")

    print("=== 6. Validating package with PackageService ===")
    val_extract = root / "scratch" / "validate_c3_package"
    if val_extract.exists():
        shutil.rmtree(val_extract)
    val_extract.mkdir(parents=True, exist_ok=True)
    
    service = PackageService(50_000_000)
    script, bgm = service.extract_and_validate(zip_path, val_extract)
    print("Package successfully validated!")
    print(f"Project ID: {script.project.id}")
    print(f"Project Title: {script.project.title}")
    print(f"Total Scenes: {len(script.scenes)}")
    print("All validations passed successfully!")

if __name__ == "__main__":
    create_complete_package()
