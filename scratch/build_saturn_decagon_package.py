import json
import os
import shutil
import zipfile
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np
from app.services.package_service import PackageService

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
    canvas = Image.new("RGBA", (w, h), (4, 5, 12, 255))
    base = Image.open("scratch/saturn_downloads/hubble_saturn_2025.jpg").convert("RGBA")
    scale = 1080 / base.width
    nh = int(base.height * scale)
    base_fit = base.resize((1080, nh), Image.Resampling.LANCZOS)
    
    # Feather top and bottom
    arr = np.array(base_fit, dtype=np.float32)
    fade = 120
    arr[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(faded, (0, 180), faded)
    
    # Starfield
    canvas.alpha_composite(create_starfield(w, h, seed=501))
    
    # Presenter Cutout on Right
    cutout = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scratch/mamase_presenter_cutout.png").convert("RGBA")
    target_h = 1320
    scale_p = target_h / cutout.height
    target_w = int(cutout.width * scale_p)
    presenter_fit = cutout.resize((target_w, target_h), Image.Resampling.LANCZOS)
    canvas.paste(presenter_fit, (w - target_w + 60, h - target_h), presenter_fit)
    
    # Typography in Upper-Left
    font_path = "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc"
    f_topic = ImageFont.truetype(font_path, 42, index=0)
    f_hook = ImageFont.truetype(font_path, 74, index=0)
    draw = ImageDraw.Draw(canvas)
    
    tx, ty = 60, 110
    draw.text((tx + 2, ty + 2), "ความลับขั้วดาวเสาร์", font=f_topic, fill=(0, 0, 0, 220))
    draw.text((tx, ty), "ความลับขั้วดาวเสาร์", font=f_topic, fill=(255, 209, 102, 255))
    
    hy = ty + 68
    draw.text((tx + 3, hy + 3), "10 เหลี่ยมปริศนา\nที่ Cassini ไม่เคยเห็น!", font=f_hook, fill=(0, 0, 0, 220))
    draw.text((tx, hy), "10 เหลี่ยมปริศนา\nที่ Cassini ไม่เคยเห็น!", font=f_hook, fill=(255, 255, 255, 255))
    
    final_rgb = canvas.convert("RGB")
    final_rgb.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 01: {out_path} ({final_rgb.size})")

def build_scene_02(out_path):
    # Sourced from Cassini North Hexagon
    src = "dist/mamase-cassini-saturn-wan-v2/images/scene-06-hexagon.png"
    shutil.copy(src, out_path)
    print(f"Generated Scene 02: {out_path}")

def build_scene_03(out_path):
    # Cassini 13 Years & Grand Finale / South Pole
    src = "dist/mamase-cassini-saturn-wan-v2/images/scene-07-finale.png"
    shutil.copy(src, out_path)
    print(f"Generated Scene 03: {out_path}")

def build_scene_04(out_path):
    # Hubble Decagon Discovery
    w, h = 1080, 1920
    canvas = Image.new("RGBA", (w, h), (3, 5, 14, 255))
    
    # 1. Hubble telescope in upper portion
    ht = Image.open("scratch/saturn_downloads/hubble_telescope.jpg").convert("RGBA")
    scale_ht = 680 / ht.width
    nh_ht = int(ht.height * scale_ht)
    ht_fit = ht.resize((680, nh_ht), Image.Resampling.LANCZOS)
    ht_arr = np.array(ht_fit, dtype=np.float32)
    fade = 60
    ht_arr[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    ht_arr[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    ht_arr[:, :fade, 3] *= np.linspace(0.0, 1.0, fade)[None, :]
    ht_arr[:, -fade:, 3] *= np.linspace(1.0, 0.0, fade)[None, :]
    ht_faded = Image.fromarray(np.clip(ht_arr, 0, 255).astype(np.uint8))
    canvas.paste(ht_faded, (40, 120), ht_faded)
    
    # 2. Decagon South Pole in center/lower-mid portion
    dec = Image.open("scratch/saturn_downloads/decagon_right_panel.png").convert("RGBA")
    dec_fit = dec.resize((880, 880), Image.Resampling.LANCZOS)
    dec_enh = ImageEnhance.Contrast(dec_fit).enhance(1.2)
    
    mask = Image.new("L", (880, 880), 0)
    draw_m = ImageDraw.Draw(mask)
    draw_m.ellipse([40, 40, 840, 840], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(35))
    canvas.paste(dec_enh, (100, 680), mask)
    
    canvas.alpha_composite(create_starfield(w, h, seed=404))
    final_rgb = canvas.convert("RGB")
    final_rgb.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 04: {out_path} ({final_rgb.size})")

def build_scene_05(out_path):
    # Fluid Dynamics & Rossby Waves (10-sided standing wave)
    w, h = 1080, 1920
    canvas = Image.new("RGB", (w, h), (4, 6, 18))
    draw = ImageDraw.Draw(canvas)
    
    # Starfield
    np.random.seed(505)
    for _ in range(400):
        sx = np.random.randint(0, w)
        sy = np.random.randint(0, h)
        sb = np.random.randint(90, 255)
        r = np.random.choice([1, 1, 1, 2])
        draw.ellipse([sx, sy, sx+r, sy+r], fill=(sb, int(sb*0.95), int(sb*1.1)))
    
    cx, cy = 540, 820
    
    # 1. Background rotating zonal shear streamlines
    for rad_base in range(120, 480, 24):
        pts = []
        for deg in range(0, 360, 3):
            th = math.radians(deg)
            r = rad_base + 8 * math.sin(10 * th + rad_base * 0.05)
            x = cx + r * math.cos(th)
            y = cy + r * math.sin(th)
            pts.append((x, y))
        intensity = max(30, min(180, int(220 - rad_base * 0.35)))
        draw.line(pts + [pts[0]], fill=(20, int(intensity*0.6), intensity), width=1)
    
    # 2. Hero 10-sided Rossby Wave Jet Stream
    r_decagon = 320
    decagon_pts = []
    for deg in range(0, 360, 1):
        th = math.radians(deg)
        r = r_decagon + 28 * math.cos(10 * th)
        x = cx + r * math.cos(th)
        y = cy + r * math.sin(th)
        decagon_pts.append((x, y))
    
    draw.line(decagon_pts + [decagon_pts[0]], fill=(40, 180, 255), width=6)
    draw.line(decagon_pts + [decagon_pts[0]], fill=(180, 240, 255), width=2)
    
    # 3. Highlight the 10 vertices/nodes of the Decagon
    for k in range(10):
        th = k * (2 * math.pi / 10)
        r = r_decagon + 28
        vx = cx + r * math.cos(th)
        vy = cy + r * math.sin(th)
        draw.ellipse([vx-12, vy-12, vx+12, vy+12], fill=(255, 220, 120), outline=(255, 255, 200), width=2)
        ex = cx + (r - 45) * math.cos(th + 0.15)
        ey = cy + (r - 45) * math.sin(th + 0.15)
        draw.arc([ex-18, ey-18, ex+18, ey+18], start=0, end=300, fill=(255, 170, 80), width=2)
    
    # 4. Central polar hurricane vortex
    for r in range(90, 0, -4):
        val = int(255 * (1 - r/90))
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(int(val*0.1), int(val*0.4), int(val*0.7)))
    draw.ellipse([cx-18, cy-18, cx+18, cy+18], fill=(5, 10, 25))
    
    canvas.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 05: {out_path} ({canvas.size})")

def build_scene_06(out_path):
    # 29.5-Year Seasonal Cycle
    w, h = 1080, 1920
    canvas = Image.new("RGBA", (w, h), (3, 4, 14, 255))
    sat = Image.open("scratch/saturn_downloads/decagon_left_panel.png").convert("RGBA")
    scale = 1040 / sat.width
    sat_fit = sat.resize((1040, int(sat.height * scale)), Image.Resampling.LANCZOS)
    sat_enh = ImageEnhance.Contrast(sat_fit).enhance(1.15)
    canvas.paste(sat_enh, (20, 360), sat_enh)
    
    draw = ImageDraw.Draw(canvas)
    sx, sy = 880, 220
    for r in range(70, 0, -4):
        glow_col = (int(255 * (1 - r/90)), int(210 * (1 - r/80)), int(80 * (1 - r/70)), int(220 * (1 - r/70)))
        draw.ellipse([sx - r, sy - r*0.8, sx + r, sy + r*0.8], fill=glow_col)
    
    draw.arc([100, 150, 980, 1300], start=45, end=210, fill=(255, 215, 100, 160), width=3)
    for offset in [-15, 0, 15]:
        draw.line([(sx - 40, sy + 30), (540 + offset, 750)], fill=(255, 235, 140, 60), width=2)
    
    canvas.alpha_composite(create_starfield(w, h, seed=606))
    final_rgb = canvas.convert("RGB")
    final_rgb.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 06: {out_path} ({final_rgb.size})")

def build_scene_07(out_path):
    # Cosmic Dual Geometry (North Hexagon vs South Decagon)
    w, h = 1080, 1920
    canvas = Image.new("RGBA", (w, h), (4, 6, 16, 255))
    
    # Top: North Hexagon
    hex_src = Image.open("dist/mamase-cassini-saturn-wan-v2/images/scene-06-hexagon.png").convert("RGBA")
    hex_crop = hex_src.crop((0, 300, 1080, 1180))
    arr_h = np.array(hex_crop, dtype=np.float32)
    fade = 140
    arr_h[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    hex_faded = Image.fromarray(np.clip(arr_h, 0, 255).astype(np.uint8))
    canvas.paste(hex_faded, (0, 60), hex_faded)
    
    # Bottom: South Decagon
    dec_src = Image.open("scratch/saturn_downloads/decagon_right_panel.png").convert("RGBA")
    dec_fit = dec_src.resize((840, 840), Image.Resampling.LANCZOS)
    dec_enh = ImageEnhance.Contrast(dec_fit).enhance(1.25)
    mask = Image.new("L", (840, 840), 0)
    draw_m = ImageDraw.Draw(mask)
    draw_m.ellipse([30, 30, 810, 810], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(30))
    canvas.paste(dec_enh, (120, 800), mask)
    
    canvas.alpha_composite(create_starfield(w, h, seed=707))
    final_rgb = canvas.convert("RGB")
    final_rgb.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 07: {out_path} ({final_rgb.size})")

def build_scene_08(out_path):
    # Philosophical Climax: Peaceful Saturn view
    w, h = 1080, 1920
    canvas = Image.new("RGBA", (w, h), (3, 4, 12, 255))
    base = Image.open("scratch/saturn_downloads/hubble_saturn_2025.jpg").convert("RGBA")
    scale = 1080 / base.width
    bh = int(base.height * scale)
    base_fit = base.resize((1080, bh), Image.Resampling.LANCZOS)
    base_enh = ImageEnhance.Contrast(base_fit).enhance(1.18)
    
    arr = np.array(base_enh, dtype=np.float32)
    fade = 140
    arr[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(faded, (0, 360), faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=808))
    final_rgb = canvas.convert("RGB")
    final_rgb.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 08: {out_path} ({final_rgb.size})")

def build_scene_09(out_path):
    # Canonical Outro
    src = "dist/mamase-james-webb-time-machine-reel-v1/images/scene-11-mamase-outro.png"
    shutil.copy(src, out_path)
    im = Image.open(out_path)
    print(f"Copied Scene 09 Outro: {out_path} ({im.size})")

def main():
    assets_dir = Path("assets/saturn_decagon_reel")
    stage_dir = Path("dist/mamase-saturn-decagon-reel-v1")
    stage_images_dir = stage_dir / "images"
    zip_path = Path("dist/mamase-saturn-decagon-reel-v1.zip")
    
    assets_dir.mkdir(parents=True, exist_ok=True)
    stage_images_dir.mkdir(parents=True, exist_ok=True)
    
    scenes_info = [
        ("scene-01-hook.png", build_scene_01),
        ("scene-02-north-hexagon.png", build_scene_02),
        ("scene-03-cassini-south-pole.png", build_scene_03),
        ("scene-04-hubble-decagon.png", build_scene_04),
        ("scene-05-fluid-dynamics.png", build_scene_05),
        ("scene-06-seasonal-cycle.png", build_scene_06),
        ("scene-07-cosmic-dual-geometry.png", build_scene_07),
        ("scene-08-philosophical-climax.png", build_scene_08),
        ("scene-09-mamase-outro.png", build_scene_09),
    ]
    
    for filename, builder in scenes_info:
        asset_target = assets_dir / filename
        stage_target = stage_images_dir / filename
        builder(asset_target)
        shutil.copy(asset_target, stage_target)
    
    print("\n--- All 9 Scene Images Generated and Staged ---")
    
    script_data = {
        "project": {
            "id": "mamase-saturn-decagon-reel-v1",
            "title": "ดาวเสาร์มี 10 เหลี่ยมเกิดขึ้นใหม่…และ Cassini ไม่เคยเห็นมัน",
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
                "narration": "สวัสดีครับ ยินดีต้อนรับสู่ Mamase จักรวาลของใจ ยาน Cassini เฝ้าดูดาวเสาร์อยู่นานถึง 13 ปี... แต่รู้ไหมครับว่า ความลับรูปทรงเรขาคณิตชิ้นใหม่นี้ กลับเพิ่งโผล่มาหลังจากยานจากไป!",
                "tts_text": "สวัสดีครับ ยินดีต้อนรับสู่ มามาเซ่ จักรวาลของใจ ยาน คาสซินี เฝ้าดูดาวเสาร์อยู่นานถึง สิบสาม ปี... แต่รู้ไหมครับว่า ความลับรูปทรงเรขาคณิตชิ้นใหม่นี้ กลับเพิ่งโผล่มาหลังจากยานจากไป!",
                "subtitle": "ความลับที่ Cassini ไม่เคยเห็น",
                "motion": "cinematic_push_in",
                "motion_speed": "normal",
                "motion_intensity": 0.2,
                "focus": "right",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Use the canonical Mamase anime presenter identity, friendly Thai male with tousled black hair, thin rectangular glasses and navy blazer, face-forward on the right for a talking shot. Premium science-documentary book-cover composition: golden Saturn with its rings, mysterious geometric atmospheric bands, elegant Thai hook text in upper left. Subtle natural head movement and gentle pointing gesture, stable composition.",
                    "negative_prompt": "extra person, extra text, watermark, logo, distorted face, distorted hands, duplicated fingers, blurry spacecraft, flicker, jitter, sudden camera movement",
                    "seed": 801,
                    "frames": 81,
                    "steps": 25,
                    "lip_sync": True,
                    "character_id": "mamase-presenter-v1"
                }
            },
            {
                "id": "scene-02-north-hexagon",
                "image": "images/scene-02-north-hexagon.png",
                "narration": "เราทุกคนคุ้นเคยกับ 'หกเหลี่ยมยักษ์' ที่ขั้วเหนือ ซึ่งกว้างใหญ่พอจะกลืนโลกเข้าไปได้ทั้งใบ พายุเรขาคณิตที่แปลกประหลาดที่สุดในระบบสุริยะ...",
                "tts_text": "เราทุกคนคุ้นเคยกับ หกเหลี่ยมยักษ์ ที่ขั้วเหนือ ซึ่งกว้างใหญ่พอจะกลืนโลกเข้าไปได้ทั้งใบ พายุเรขาคณิตที่แปลกประหลาดที่สุดในระบบสุริยะ...",
                "subtitle": "หกเหลี่ยมยักษ์ขั้วเหนือ",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic high-detail scientific view of Saturn's North Pole Hexagon, spinning 6-sided jet stream in golden teal atmospheric bands, slow majestic rotation in dark space, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, aliens, flicker, jitter",
                    "seed": 802,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-03-cassini-south-pole",
                "image": "images/scene-03-cassini-south-pole.png",
                "narration": "ตลอด 13 ปีที่ Cassini บันทึกภาพขั้วใต้ ที่นั่นมีเพียงพายุหมุนวงกลมธรรมดา จนกระทั่งยานสั่งลาและดับสลายไปในปี 2017",
                "tts_text": "ตลอด สิบสาม ปีที่ คาสซินี บันทึกภาพขั้วใต้ ที่นั่นมีเพียงพายุหมุนวงกลมธรรมดา จนกระทั่งยานสั่งลาและดับสลายไปในปี สองพันสิบเจ็ด",
                "subtitle": "ขั้วใต้ในยุค Cassini",
                "motion": "documentary_pan",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cassini spacecraft diving into Saturn's golden atmosphere during its Grand Finale, glowing planetary rings in dark cosmic void, scientific realism, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, aliens, explosions, flicker, jitter",
                    "seed": 803,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-04-hubble-decagon",
                "image": "images/scene-04-hubble-decagon.png",
                "narration": "แต่ล่าสุด กล้องโทรทรรศน์อวกาศ Hubble ที่เฝ้ามองต่อ กลับค้นพบสิ่งเหลือเชื่อ... พายุรูป 'สิบเหลี่ยม' หรือ Decagon กำลังหมุนวนล้อมขั้วใต้อย่างสมบูรณ์แบบ!",
                "tts_text": "แต่ล่าสุด กล้องโทรทรรศน์อวกาศ ฮับเบิล ที่เฝ้ามองต่อ กลับค้นพบสิ่งเหลือเชื่อ... พายุรูป สิบเหลี่ยม หรือ เดคากอน กำลังหมุนวนล้อมขั้วใต้อย่างสมบูรณ์แบบ!",
                "subtitle": "Hubble พบ 'สิบเหลี่ยม' ขั้วใต้!",
                "motion": "gentle_float",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Hubble Space Telescope observing Saturn from Earth orbit, revealing a distinct 10-sided atmospheric wave decagon circling Saturn's south pole, high-contrast astronomical discovery, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, flicker, jitter",
                    "seed": 804,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-05-fluid-dynamics",
                "image": "images/scene-05-fluid-dynamics.png",
                "narration": "ดาวเคราะห์ก๊าซสร้างรูปทรงเรขาคณิตได้ยังไง? ฟิสิกส์บอกเราว่า เมื่อกระแสลมกรดพัดสวนทางกันด้วยความเร็วสูง มันจะเกิดคลื่นฟันเฟืองที่ล็อกตัวกันเป็นมุมเหลี่ยมครับ",
                "tts_text": "ดาวเคราะห์ก๊าซสร้างรูปทรงเรขาคณิตได้ยังไง? ฟิสิกส์บอกเราว่า เมื่อกระแสลมกรดพัดสวนทางกันด้วยความเร็วสูง มันจะเกิดคลื่นฟันเฟืองที่ล็อกตัวกันเป็นมุมเหลี่ยมครับ",
                "subtitle": "ฟิสิกส์คลื่นลมกรดเรขาคณิต",
                "motion": "cinematic_pull_out",
                "motion_speed": "slow",
                "motion_intensity": 0.16,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic fluid dynamics visualization of atmospheric jet streams, concentric shear flows locking into geometric polygonal standing Rossby waves, glowing neon streamlines in gas layers, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, violent collision, flicker, jitter",
                    "seed": 805,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-06-seasonal-cycle",
                "image": "images/scene-06-seasonal-cycle.png",
                "narration": "หนึ่งปีบนดาวเสาร์ยาวนานเท่ากับ 29 ปีบนโลก ฤดูกาลที่เปลี่ยนไปอย่างช้า ๆ ทำให้พลังงานความร้อนเปลี่ยนทิศ จนสลับคลื่นลมจากวงกลมกลายร่างเป็นสิบเหลี่ยม!",
                "tts_text": "หนึ่งปีบนดาวเสาร์ยาวนานเท่ากับ ยี่สิบเก้า ปีบนโลก ฤดูกาลที่เปลี่ยนไปอย่างช้า ๆ ทำให้พลังงานความร้อนเปลี่ยนทิศ จนสลับคลื่นลมจากวงกลมกลายร่างเป็นสิบเหลี่ยม!",
                "subtitle": "การเปลี่ยนฤดูกาล 29 ปี",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Saturn orbiting the Sun along its 29.5-year elliptical path, sunlight angle changing across the rings and southern hemisphere, slow graceful orbital drift in deep starry space, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, aliens, flicker, jitter",
                    "seed": 806,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-07-cosmic-dual-geometry",
                "image": "images/scene-07-cosmic-dual-geometry.png",
                "narration": "ลองนึกภาพสิครับ ขั้วเหนือมี 6 เหลี่ยม ขั้วใต้มี 10 เหลี่ยม... ดาวเคราะห์ทั้งดวงกำลังจัดแสดงงานศิลปะคณิตศาสตร์ ขนาดยักษ์กลางอวกาศ",
                "tts_text": "ลองนึกภาพสิครับ ขั้วเหนือมี หก เหลี่ยม ขั้วใต้มี สิบ เหลี่ยม... ดาวเคราะห์ทั้งดวงกำลังจัดแสดงงานศิลปะคณิตศาสตร์ ขนาดยักษ์กลางอวกาศ",
                "subtitle": "หกเหลี่ยมเหนือ สิบเหลี่ยมใต้",
                "motion": "documentary_pan",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Dramatic dual comparison of Saturn's poles: 6-sided hexagon at North Pole and 10-sided decagon at South Pole, beautiful mathematical planetary symmetry in space, documentary realism, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, flicker, jitter",
                    "seed": 807,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-08-philosophical-climax",
                "image": "images/scene-08-philosophical-climax.png",
                "narration": "จักรวาลไม่เคยหยุดสร้างสรรค์ แม้ในจุดที่เราคิดว่ารู้จักมันดีที่สุดแล้ว ธรรมชาติก็ยังพร้อมเผยความลับบทใหม่ ให้เราตื่นเต้นเสมอครับ",
                "tts_text": "จักรวาลไม่เคยหยุดสร้างสรรค์ แม้ในจุดที่เราคิดว่ารู้จักมันดีที่สุดแล้ว ธรรมชาติก็ยังพร้อมเผยความลับบทใหม่ ให้เราตื่นเต้นเสมอครับ",
                "subtitle": "ความลับใหม่ในจักรวาล",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Contemplative philosophical climax: majestic full view of Saturn with radiant rings floating serenely in the deep cosmos, quiet poetic astronomy aesthetic, gentle camera drift, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, flicker, jitter, violent action",
                    "seed": 808,
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
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 98,
                    "frames": 81,
                    "lip_sync": False
                }
            }
        ]
    }
    
    metadata_data = {
        "title": "ดาวเสาร์มี 10 เหลี่ยมเกิดขึ้นใหม่…และ Cassini ไม่เคยเห็นมัน",
        "description": "ยาน Cassini เฝ้าดาวเสาร์อยู่นานถึง 13 ปี แต่ทำไมพายุ 10 เหลี่ยม (Decagon) ขั้วใต้ลูกนี้ กลับเพิ่งปรากฏตัวหลังยานจากไป? กล้องโทรทรรศน์อวกาศ Hubble ค้นพบความลับครั้งประวัติศาสตร์ของระบบสุริยะ\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#Mamase #ดาวเสาร์ #Saturn #Cassini #Hubble #ดาราศาสตร์ #อวกาศ #วิทยาศาสตร์"
    }
    
    # Write script.json
    script_path = stage_dir / "script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)
    print("Wrote script.json")
    
    # Write video-metadata.json
    meta_path = stage_dir / "video-metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata_data, f, ensure_ascii=False, indent=2)
    print("Wrote video-metadata.json")
    
    # Build ZIP package
    print(f"Building ZIP: {zip_path}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(script_path, arcname="script.json")
        zf.write(meta_path, arcname="video-metadata.json")
        for img_file in sorted((stage_dir / "images").glob("*.png")):
            zf.write(img_file, arcname=f"images/{img_file.name}")
            print(f" - Added to ZIP: images/{img_file.name} ({img_file.stat().st_size} bytes)")
    
    print(f"ZIP created: {zip_path.stat().st_size:,} bytes")
    
    # Validate with PackageService
    print("\n--- Validating with PackageService ---")
    tmp_out = Path("scratch/validate_saturn_out")
    if tmp_out.exists():
        shutil.rmtree(tmp_out)
    tmp_out.mkdir(parents=True, exist_ok=True)
    
    svc = PackageService(50_000_000)
    parsed_script, bgm_path = svc.extract_and_validate(zip_path, tmp_out)
    print("Validation SUCCESS!")
    print(f"Parsed project ID: {parsed_script.project.id}")
    print(f"Parsed project title: {parsed_script.project.title}")
    print(f"Total scenes parsed: {len(parsed_script.scenes)}")

if __name__ == "__main__":
    main()
