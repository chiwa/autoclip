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

def create_starfield(w=TARGET_W, h=TARGET_H, seed=42, num_stars=380, max_y=1500):
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
    """Scene 01: Narrative Key Art (BepiColombo, Mercury, blazing Sun, Mamase presenter, and Thai typography)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    # 1. Base arrival & Mercury scene
    base = Image.open("scratch/bepi_esa/BepiColombo_approaches_Mercury.png").convert("RGBA")
    scale = 1350 / base.height
    bw = int(base.width * scale)
    base_fit = base.resize((bw, 1350), Image.Resampling.LANCZOS)
    
    crop_x = int((bw - w) * 0.35)
    base_cropped = base_fit.crop((crop_x, 0, crop_x + w, 1350))
    
    arr = np.array(base_cropped, dtype=np.float32)
    fade_bot = 260
    arr[-fade_bot:, :, 3] *= np.linspace(1.0, 0.0, fade_bot)[:, None]
    fade_top = 80
    arr[:fade_top, :, 3] *= np.linspace(0.0, 1.0, fade_top)[:, None]
    base_faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(base_faded, (0, 80), base_faded)
    
    # 2. Add dramatic solar flare in upper left
    flare = Image.open("assets/solar_storm_documentary/scene_04_solar_flare.png").convert("RGBA")
    flare_crop = flare.crop((0, 0, 1080, 750)).resize((780, 540), Image.Resampling.LANCZOS)
    arr_f = np.array(flare_crop, dtype=np.float32)
    fade_fx = 240
    arr_f[:, -fade_fx:, 3] *= np.linspace(1.0, 0.0, fade_fx)[None, :]
    fade_fy = 220
    arr_f[-fade_fy:, :, 3] *= np.linspace(1.0, 0.0, fade_fy)[:, None]
    flare_faded = Image.fromarray(np.clip(arr_f, 0, 255).astype(np.uint8))
    canvas.paste(flare_faded, (0, 0), flare_faded)
    
    # 3. Cosmic stars
    canvas.alpha_composite(create_starfield(w, h, seed=101, num_stars=300))
    
    # 4. Presenter Cutout on the Right
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
    
    # Directional rim lighting matching solar glare
    p_arr = np.array(presenter_scaled, dtype=np.float32)
    rim_w = int(target_w * 0.25)
    rim_gradient = np.linspace(1.0, 0.0, rim_w)[None, :, None]
    p_arr[:, :rim_w, 0] = np.clip(p_arr[:, :rim_w, 0] + 30 * rim_gradient[:, :, 0], 0, 255)
    p_arr[:, :rim_w, 1] = np.clip(p_arr[:, :rim_w, 1] + 18 * rim_gradient[:, :, 0], 0, 255)
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
    f_topic = ImageFont.truetype(font_path, 44, index=0)
    f_hook = ImageFont.truetype(font_path, 76, index=0)
    
    tx, ty = 60, 110
    draw_styled_text(canvas, "ความลับดาวพุธ", f_topic, (tx, ty), fill_color=(255, 214, 102, 255))
    
    hy = ty + 68
    draw_styled_text(canvas, "ทำไมไปดาวพุธ...\nยากกว่าที่คิด?", f_hook, (tx, hy), fill_color=(255, 255, 255, 255))
    
    final_rgb = canvas.convert("RGB")
    final_rgb.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 01: {out_path} ({final_rgb.size}, {os.path.getsize(out_path):,} bytes)")

def build_scene_02(out_path):
    """Scene 02: Only 3 missions in human history (Spacecraft traversing interplanetary space to Mercury)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    base = Image.open("scratch/bepi_esa/BepiColombo_and_Solar_Orbiter_flyby_illustration.png").convert("RGBA")
    scale = 1600 / base.height
    bw = int(base.width * scale)
    base_fit = base.resize((bw, 1600), Image.Resampling.LANCZOS)
    
    cx = int((bw - w) * 0.45)
    base_cropped = base_fit.crop((cx, 0, cx + w, 1600))
    
    arr = np.array(base_cropped, dtype=np.float32)
    fade_bot = 320
    arr[-fade_bot:, :, 3] *= np.linspace(1.0, 0.0, fade_bot)[:, None]
    fade_top = 100
    arr[:fade_top, :, 3] *= np.linspace(0.0, 1.0, fade_top)[:, None]
    faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    
    canvas.paste(faded, (0, 60), faded)
    canvas.alpha_composite(create_starfield(w, h, seed=202, num_stars=420))
    
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 02: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_03(out_path):
    """Scene 03: The Solar Furnace (+430°C solar radiation blasting Mercury's scorched surface)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (4, 4, 10, 255))
    
    sun = Image.open("assets/solar_storm_documentary/scene_02_serene_sun.png").convert("RGBA")
    scale_s = (w + 200) / sun.width
    sh = int(sun.height * scale_s)
    sun_fit = sun.resize((w + 200, sh), Image.Resampling.LANCZOS).crop((100, 0, 100 + w, sh))
    
    arr_s = np.array(sun_fit, dtype=np.float32)
    fade_sb = 340
    arr_s[-fade_sb:, :, 3] *= np.linspace(1.0, 0.0, fade_sb)[:, None]
    sun_faded = Image.fromarray(np.clip(arr_s, 0, 255).astype(np.uint8))
    canvas.paste(sun_faded, (0, 0), sun_faded)
    
    merc = Image.open("scratch/bepi_esa/BepiColombo_hugs_Mercury.png").convert("RGBA")
    scale_m = 1450 / merc.height
    mw = int(merc.width * scale_m)
    merc_fit = merc.resize((mw, 1450), Image.Resampling.LANCZOS)
    
    cx = (mw - w) // 2
    merc_crop = merc_fit.crop((cx, 0, cx + w, 1450))
    
    arr_m = np.array(merc_crop, dtype=np.float32)
    arr_m[:260, :, 3] *= np.linspace(0.0, 1.0, 260)[:, None]
    arr_m[-350:, :, 3] *= np.linspace(1.0, 0.0, 350)[:, None]
    
    arr_m[:700, :, 0] = np.clip(arr_m[:700, :, 0] * 1.3 + 35, 0, 255)
    arr_m[:700, :, 1] = np.clip(arr_m[:700, :, 1] * 1.15 + 18, 0, 255)
    
    merc_faded = Image.fromarray(np.clip(arr_m, 0, 255).astype(np.uint8))
    canvas.paste(merc_faded, (0, 480), merc_faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=303, num_stars=300, max_y=1400))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 03: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_04(out_path):
    """Scene 04: Spacecraft Engineering - Ceramic Heat Shield and Giant Radiators."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    mtm = Image.open("scratch/bepi_esa/Mercury_Transfer_Module_with_integrated_ion_thrusters.jpg").convert("RGBA")
    scale = w / mtm.width
    mh = int(mtm.height * scale)
    mtm_fit = mtm.resize((w, mh), Image.Resampling.LANCZOS)
    
    mtm_crop = mtm_fit.crop((0, 120, w, 120 + 1600))
    
    arr = np.array(mtm_crop, dtype=np.float32)
    arr[:140, :, 3] *= np.linspace(0.0, 1.0, 140)[:, None]
    arr[-280:, :, 3] *= np.linspace(1.0, 0.0, 280)[:, None]
    
    mtm_faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(mtm_faded, (0, 100), mtm_faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=404, num_stars=320))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 04: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_05(out_path):
    """Scene 05: Tilted Solar Arrays (Extreme engineering: solar panels angled sharply to graze sunlight)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    base = Image.open("scratch/bepi_esa/End_of_BepiColombo_s_solar_electric_propulsion.jpg").convert("RGBA")
    scale = 1450 / base.height
    bw = int(base.width * scale)
    base_fit = base.resize((bw, 1450), Image.Resampling.LANCZOS)
    
    cx = int((bw - w) * 0.45)
    base_crop = base_fit.crop((cx, 0, cx + w, 1450))
    
    arr = np.array(base_crop, dtype=np.float32)
    arr[:160, :, 3] *= np.linspace(0.0, 1.0, 160)[:, None]
    arr[-300:, :, 3] *= np.linspace(1.0, 0.0, 300)[:, None]
    base_faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(base_faded, (0, 140), base_faded)
    
    beam_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_b = ImageDraw.Draw(beam_layer)
    draw_b.polygon([(0, 0), (600, 0), (1080, 950), (0, 820)], fill=(255, 230, 180, 42))
    beam_blur = beam_layer.filter(ImageFilter.GaussianBlur(45))
    canvas.alpha_composite(beam_blur)
    
    canvas.alpha_composite(create_starfield(w, h, seed=505, num_stars=350))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 05: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_06(out_path):
    """Scene 06: Zero Atmosphere, No Airbrakes (Mercury's cratered, airless surface against stark cosmic black)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 3, 8, 255))
    
    cam = Image.open("scratch/bepi_esa/Mercury_s_sunlit_north_viewed_by_M-CAM_1.jpg").convert("RGBA")
    scale = 1550 / cam.height
    cw = int(cam.width * scale)
    cam_fit = cam.resize((cw, 1550), Image.Resampling.LANCZOS)
    
    cx = (cw - w) // 2
    cam_crop = cam_fit.crop((cx, 0, cx + w, 1550))
    
    arr = np.array(cam_crop, dtype=np.float32)
    arr[-340:, :, 3] *= np.linspace(1.0, 0.0, 340)[:, None]
    arr[:140, :, 3] *= np.linspace(0.0, 1.0, 140)[:, None]
    
    cam_faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(cam_faded, (0, 160), cam_faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=606, num_stars=450, max_y=600))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 06: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_07(out_path):
    """Scene 07: Complex Planetary Arrival Sequence (Dual science orbiters ESA MPO and JAXA Mio)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    # Left half (ESA MPO)
    left = Image.open("scratch/test_arr_left.png").convert("RGBA")
    scale_l = w / left.width
    lh = int(left.height * scale_l)
    left_fit = left.resize((w, lh), Image.Resampling.LANCZOS)

    # Right half (JAXA Mio)
    right = Image.open("scratch/test_arr_right.png").convert("RGBA")
    scale_r = w / right.width
    rh = int(right.height * scale_r)
    right_fit = right.resize((w, rh), Image.Resampling.LANCZOS)

    # Right half (JAXA Mio) in upper section
    arr_r = np.array(right_fit, dtype=np.float32)
    arr_r[:60, :, 3] *= np.linspace(0.0, 1.0, 60)[:, None]
    arr_r[-240:, :, 3] *= np.linspace(1.0, 0.0, 240)[:, None]
    mio_faded = Image.fromarray(np.clip(arr_r, 0, 255).astype(np.uint8))
    canvas.paste(mio_faded, (0, 40), mio_faded)

    # Left half (ESA MPO) in lower-mid section
    arr_l = np.array(left_fit, dtype=np.float32)
    arr_l[:200, :, 3] *= np.linspace(0.0, 1.0, 200)[:, None]
    arr_l[-450:, :, 3] *= np.linspace(1.0, 0.0, 450)[:, None]
    mpo_faded = Image.fromarray(np.clip(arr_l, 0, 255).astype(np.uint8))
    canvas.paste(mpo_faded, (0, 520), mpo_faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=707, num_stars=380))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 07: {out_path} ({os.path.getsize(out_path):,} bytes)")

def build_scene_08(out_path):
    """Scene 08: Philosophical Climax (Sublime view of BepiColombo hovering gracefully over Mercury)."""
    w, h = TARGET_W, TARGET_H
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    
    base = Image.open("scratch/bepi_esa/BepiColombo_hugs_Mercury.png").convert("RGBA")
    scale = 1450 / base.height
    bw = int(base.width * scale)
    base_fit = base.resize((bw, 1450), Image.Resampling.LANCZOS)
    
    cx = (bw - w) // 2
    base_crop = base_fit.crop((cx, 0, cx + w, 1450))
    
    arr = np.array(base_crop, dtype=np.float32)
    arr[:180, :, 3] *= np.linspace(0.0, 1.0, 180)[:, None]
    arr[-320:, :, 3] *= np.linspace(1.0, 0.0, 320)[:, None]
    
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.12 + 12, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.06 + 6, 0, 255)
    
    base_faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(base_faded, (0, 180), base_faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=808, num_stars=400))
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
    asset_dir = root / "assets" / "bepicolombo_extreme_mercury_reel"
    staging_dir = root / "dist" / "mamase-bepicolombo-extreme-mercury-reel-v1"
    staging_images = staging_dir / "images"
    zip_path = root / "dist" / "mamase-bepicolombo-extreme-mercury-reel-v1.zip"
    
    asset_dir.mkdir(parents=True, exist_ok=True)
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_images.mkdir(parents=True, exist_ok=True)
    
    print("=== 2. Generating Master Assets ===")
    builders = [
        ("scene-01-hook.png", build_scene_01),
        ("scene-02-only-three-missions.png", build_scene_02),
        ("scene-03-solar-furnace.png", build_scene_03),
        ("scene-04-ceramic-heat-shield.png", build_scene_04),
        ("scene-05-tilted-solar-arrays.png", build_scene_05),
        ("scene-06-no-atmosphere-airbrakes.png", build_scene_06),
        ("scene-07-planetary-arrival.png", build_scene_07),
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
        "title": "ทำไมไปดาวพุธ... ถึงยากกว่าที่หลายคนคิด? (BepiColombo เผชิญนรกสุริยะ)",
        "description": "ทั้งที่ดาวพุธอยู่ใกล้โลกมากกว่าดาวพฤหัสบดี แต่ทำไมการส่งยานไปที่นั่นถึงเป็นหนึ่งในภารกิจที่ยากที่สุดในประวัติศาสตร์มนุษยชาติ?\n\nตลอดประวัติศาสตร์ มีเพียง 3 ภารกิจเท่านั้นที่เคยเดินทางไปถึงดาวพุธ! เจาะลึกความท้าทายสุดขั้วในแดนนรกสุริยะ แสงแดดแรงกว่าโลก 10 เท่า อุณหภูมิพุ่งสูง 430 องศาเซลเซียส ไร้ชั้นบรรยากาศช่วยเบรก และเกราะฉนวนเซรามิกกันความร้อนพิเศษของยาน BepiColombo ก่อนเข้าสู่ขั้นตอน Planetary Arrival ที่ซับซ้อนที่สุดของ ESA\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#BepiColombo #Mercury #ดาวพุธ #ดาราศาสตร์ #อวกาศ #วิทยาศาสตร์ #ESA #JAXA #Mamase #จักรวาลของใจ"
    }
    with open(staging_dir / "video-metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print("Created video-metadata.json")

    print("=== 4. Writing script.json ===")
    script = {
        "project": {
            "id": "mamase-bepicolombo-extreme-mercury-reel-v1",
            "title": "ทำไมไปดาวพุธ... ถึงยากกว่าที่หลายคนคิด?",
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
                "narration": "สวัสดีครับ ยินดีต้อนรับสู่ Mamase จักรวาลของใจ รู้ไหมครับว่า... ทั้งที่ดาวพุธอยู่ใกล้โลกมากกว่าดาวพฤหัสบดี แต่การส่งยานไปที่นั่น กลับยากกว่าการไปสุดขอบระบบสุริยะเสียอีก!",
                "tts_text": "สวัสดีครับ ยินดีต้อนรับสู่ มามาเซ่ จักรวาลของใจ รู้ไหมครับว่า... ทั้งที่ดาวพุธอยู่ใกล้โลกมากกว่าดาวพฤหัสบดี แต่การส่งยานไปที่นั่น กลับยากกว่าการไปสุดขอบระบบสุริยะเสียอีก!",
                "subtitle": "ไปดาวพุธ... ยากกว่าสุดขอบระบบสุริยะ?",
                "motion": "cinematic_push_in",
                "motion_speed": "normal",
                "motion_intensity": 0.2,
                "focus": "right",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Use the canonical Mamase anime presenter identity, friendly Thai male with tousled black hair, thin rectangular glasses and navy blazer, face-forward on the right for a talking shot. BepiColombo spacecraft clad in white ceramic thermal shields approaching scorched cratered Mercury under the blazing radiant Sun, elegant Thai hook text in upper left. Subtle natural head movement and gentle pointing gesture, stable composition.",
                    "negative_prompt": "extra person, extra text, watermark, logo, distorted face, distorted hands, duplicated fingers, blurry spacecraft, flicker, jitter, sudden camera movement",
                    "seed": 901,
                    "frames": 81,
                    "steps": 25,
                    "lip_sync": True,
                    "character_id": "mamase-presenter-v1"
                }
            },
            {
                "id": "scene-02-only-three-missions",
                "image": "images/scene-02-only-three-missions.png",
                "narration": "ในประวัติศาสตร์มนุษยชาติ เราส่งยานไปดาวอังคารหลายสิบลำ แต่กลับมียานที่เดินทางไปถึงดาวพุธเพียงแค่ 3 ลำเท่านั้นครับ!",
                "tts_text": "ในประวัติศาสตร์มนุษยชาติ เราส่งยานไปดาวอังคารหลายสิบลำ แต่กลับมียานที่เดินทางไปถึงดาวพุธเพียงแค่ สาม ลำเท่านั้นครับ!",
                "subtitle": "มนุษย์ส่งยานไปดาวพุธ แค่ 3 ลำในประวัติศาสตร์",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic space documentary photography of deep solar system exploration, spacecraft traversing the deep cosmic void toward the inner solar system, authentic ESA space science aesthetics, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, flicker, jitter",
                    "seed": 902,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-03-solar-furnace",
                "image": "images/scene-03-solar-furnace.png",
                "narration": "เพราะดาวพุธเปรียบเหมือน 'เตาอบสุริยะ' แสงแดดที่นี่แผดเผาแรงกว่าบนโลกถึง 10 เท่า กลางวันร้อนทะลุ 430 องศาเซลเซียส ร้อนจนตะกั่วละลายได้ทันที",
                "tts_text": "เพราะดาวพุธเปรียบเหมือน เตาอบสุริยะ แสงแดดที่นี่แผดเผาแรงกว่าบนโลกถึง สิบ เท่า กลางวันร้อนทะลุ สี่ร้อยสามสิบ องศาเซลเซียส ร้อนจนตะกั่วละลายได้ทันที",
                "subtitle": "เตาอบสุริยะ ร้อนกว่าโลก 10 เท่า (430°C)",
                "motion": "cinematic_pull_out",
                "motion_speed": "slow",
                "motion_intensity": 0.16,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic space documentary shot of planet Mercury orbiting in extreme proximity to the colossal roaring Sun, blistering solar flare and golden coronal plasma blasting across the cratered planetary surface, extreme contrast between burning sunlit side and dark night side, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, explosion, flicker, jitter",
                    "seed": 903,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-04-ceramic-heat-shield",
                "image": "images/scene-04-ceramic-heat-shield.png",
                "narration": "BepiColombo จึงต้องสวมเสื้อเกราะฉนวนกันความร้อนสีขาวพิเศษ ทำจากเซรามิกและไททาเนียม พร้อมแผงระบายความร้อนขนาดยักษ์ที่ต้องหันหลบแดดตลอดเวลา",
                "tts_text": "เบปิโคลอมโบ จึงต้องสวมเสื้อเกราะฉนวนกันความร้อนสีขาวพิเศษ ทำจากเซรามิกและไททาเนียม พร้อมแผงระบายความร้อนขนาดยักษ์ที่ต้องหันหลบแดดตลอดเวลา",
                "subtitle": "เกราะเซรามิกกันความร้อนพิเศษ",
                "motion": "gentle_float",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Macro engineering aerospace documentary view of BepiColombo Mercury Transfer Module, pristine white multi-layer ceramic insulation blankets, gleaming titanium structure, and heat-rejection radiator panels in cosmic space, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, damage, flicker, jitter",
                    "seed": 904,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-05-tilted-solar-arrays",
                "image": "images/scene-05-tilted-solar-arrays.png",
                "narration": "แม้แต่แผงโซลาร์เซลล์ก็หันรับแดดตรง ๆ ไม่ได้นะครับ! วิศวกรต้องสั่งให้แผงเอียงทำมุมแคบ เพื่อรับแสงแค่นิดเดียว ไม่อย่างนั้นแผงจะไหม้เกรียมทันที",
                "tts_text": "แม้แต่แผงโซลาร์เซลล์ก็หันรับแดดตรง ๆ ไม่ได้นะครับ! วิศวกรต้องสั่งให้แผงเอียงทำมุมแคบ เพื่อรับแสงแค่นิดเดียว ไม่อย่างนั้นแผงจะไหม้เกรียมทันที",
                "subtitle": "แผงโซลาร์ต้องเอียงหลบแดด",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic space documentary view of BepiColombo large solar array wing tilted at an acute grazing angle relative to blinding directional sunlight, specular golden sun reflections along the panel edge, cool shadow behind, authentic spacecraft engineering, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, fire, explosion, flicker, jitter",
                    "seed": 905,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-06-no-atmosphere-airbrakes",
                "image": "images/scene-06-no-atmosphere-airbrakes.png",
                "narration": "ที่สำคัญ ดาวพุธแทบไม่มีชั้นบรรยากาศ ยานจึงไม่สามารถใช้ 'แอร์เบรก' หรือกางร่มชูชีพช่วยลดความเร็วเหมือนตอนลงดาวอังคารได้เลย ต้องพึ่งพาการคำนวณวงโคจรล้วน ๆ",
                "tts_text": "ที่สำคัญ ดาวพุธแทบไม่มีชั้นบรรยากาศ ยานจึงไม่สามารถใช้ แอร์เบรก หรือกางร่มชูชีพช่วยลดความเร็วเหมือนตอนลงดาวอังคารได้เลย ต้องพึ่งพาการคำนวณวงโคจรล้วน ๆ",
                "subtitle": "ไร้บรรยากาศ ไร้ร่มชูชีพเบรก",
                "motion": "cinematic_pull_out",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Authentic space documentary camera view of Mercury airless cratered surface, stark lunar-like jagged craters and ridges under a pitch-black vacuum sky, zero atmospheric haze, stark scientific realism, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, clouds, blue sky, atmosphere, flicker, jitter",
                    "seed": 906,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-07-planetary-arrival",
                "image": "images/scene-07-planetary-arrival.png",
                "narration": "และตอนนี้ ESA ยืนยันว่า ยานกำลังเข้าสู่ขั้นตอน Planetary Arrival ที่ซับซ้อนที่สุด เพื่อส่งคู่หู MPO และ Mio แยกย้ายสำรวจดาวพุธในแบบที่ไม่เคยมีใครทำได้",
                "tts_text": "และตอนนี้ อีเอสเอ ยืนยันว่า ยานกำลังเข้าสู่ขั้นตอน แพลเน็ตทารี อะไรวัล ที่ซับซ้อนที่สุด เพื่อส่งคู่หู เอ็มพีโอ และ มิโอะ แยกย้ายสำรวจดาวพุธในแบบที่ไม่เคยมีใครทำได้",
                "subtitle": "ขั้นตอนเข้าวงโคจรที่ซับซ้อนที่สุด",
                "motion": "documentary_pan",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Cinematic space documentary view of BepiColombo planetary arrival sequence, dual science orbiters ESA MPO and JAXA Mio operating in separate orbital paths around cratered Mercury, orbital trajectories in deep space, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, explosion, flicker, jitter",
                    "seed": 907,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-08-philosophical-climax",
                "image": "images/scene-08-philosophical-climax.png",
                "narration": "การพิชิตดินแดนที่ร้อนจัดและอยู่ใกล้เปลวไฟที่สุด พิสูจน์ว่าความฉลาดและความเพียรของมนุษย์ สามารถเอาชนะขีดจำกัดที่โหดร้ายที่สุดของธรรมชาติได้เสมอครับ",
                "tts_text": "การพิชิตดินแดนที่ร้อนจัดและอยู่ใกล้เปลวไฟที่สุด พิสูจน์ว่าความฉลาดและความเพียรของมนุษย์ สามารถเอาชนะขีดจำกัดที่โหดร้ายที่สุดของธรรมชาติได้เสมอครับ",
                "subtitle": "ความเพียรที่เอาชนะขีดจำกัด",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "none",
                "wan": {
                    "prompt": "Sublime and inspiring space documentary finale, BepiColombo spacecraft soaring gracefully above the curved horizon of cratered Mercury, radiant golden solar rim light illuminating the spacecraft in deep cosmos, poetic and heroic human achievement, no text.",
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
    val_extract = root / "scratch" / "validate_extreme_bepi"
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
