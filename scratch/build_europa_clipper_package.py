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
    canvas = Image.new("RGBA", (w, h), (4, 6, 15, 255))
    base = Image.open("scratch/europa_downloads/Europa_Clipper_artist_s_concept.jpg").convert("RGBA")
    scale = 1080 / base.width
    nh = int(base.height * scale)
    base_fit = base.resize((1080, nh), Image.Resampling.LANCZOS)
    
    arr = np.array(base_fit, dtype=np.float32)
    fade = 120
    arr[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(faded, (0, 140), faded)
    
    canvas.alpha_composite(create_starfield(w, h, seed=901))
    
    cutout = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/scratch/mamase_presenter_cutout.png").convert("RGBA")
    target_h = 1320
    scale_p = target_h / cutout.height
    target_w = int(cutout.width * scale_p)
    presenter_fit = cutout.resize((target_w, target_h), Image.Resampling.LANCZOS)
    canvas.paste(presenter_fit, (w - target_w + 60, h - target_h), presenter_fit)
    
    font_path = "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc"
    f_topic = ImageFont.truetype(font_path, 42, index=0)
    f_hook = ImageFont.truetype(font_path, 72, index=0)
    draw = ImageDraw.Draw(canvas)
    
    tx, ty = 60, 110
    draw.text((tx + 2, ty + 2), "ดวงจันทร์ยูโรปา", font=f_topic, fill=(0, 0, 0, 220))
    draw.text((tx, ty), "ดวงจันทร์ยูโรปา", font=f_topic, fill=(255, 209, 102, 255))
    
    hy = ty + 68
    draw.text((tx + 3, hy + 3), "ถ้ามีสิ่งมีชีวิต...\nอยู่ใต้เปลือกน้ำแข็ง?", font=f_hook, fill=(0, 0, 0, 220))
    draw.text((tx, hy), "ถ้ามีสิ่งมีชีวิต...\nอยู่ใต้เปลือกน้ำแข็ง?", font=f_hook, fill=(255, 255, 255, 255))
    
    final_rgb = canvas.convert("RGB")
    final_rgb.save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 01: {out_path} ({final_rgb.size})")

def build_scene_02(out_path):
    w, h = 1080, 1920
    canvas = Image.new("RGBA", (w, h), (2, 4, 12, 255))
    im = Image.open("scratch/europa_downloads/Enceladus_interior.jpg").convert("RGBA")
    scale = 1080 / im.width
    nh = int(im.height * scale)
    im_fit = im.resize((1080, nh), Image.Resampling.LANCZOS)
    arr = np.array(im_fit, dtype=np.float32)
    fade = 120
    arr[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(faded, (0, 420), faded)
    canvas.alpha_composite(create_starfield(w, h, seed=902))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 02: {out_path}")

def build_scene_03(out_path):
    w, h = 1080, 1920
    canvas = Image.new("RGBA", (w, h), (3, 5, 14, 255))
    im = Image.open("scratch/europa_downloads/Juice_flyby_of_Europa_artist_s_impression.jpg").convert("RGBA")
    scale = 1080 / im.width
    nh = int(im.height * scale)
    im_fit = im.resize((1080, nh), Image.Resampling.LANCZOS)
    arr = np.array(im_fit, dtype=np.float32)
    fade = 120
    arr[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(faded, (0, 360), faded)
    
    draw = ImageDraw.Draw(canvas)
    cx, cy = 540, 720
    for r in range(240, 440, 40):
        draw.arc([cx - r, cy - int(r*0.6), cx + r, cy + int(r*0.6)], start=30, end=150, fill=(255, 200, 100, 120), width=2)
    
    canvas.alpha_composite(create_starfield(w, h, seed=903))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 03: {out_path}")

def build_scene_04(out_path):
    w, h = 1080, 1920
    canvas = Image.new("RGBA", (w, h), (2, 3, 10, 255))
    im = Image.open("scratch/europa_downloads/Hydrothermal_activity_on_Enceladus.jpg").convert("RGBA")
    scale = 1080 / im.width
    nh = int(im.height * scale)
    im_fit = im.resize((1080, nh), Image.Resampling.LANCZOS)
    arr = np.array(im_fit, dtype=np.float32)
    fade = 120
    arr[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(faded, (0, 440), faded)
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 04: {out_path}")

def build_scene_05(out_path):
    w, h = 1080, 1920
    im = Image.open("scratch/europa_downloads/New_evidence_of_watery_plumes_on_Jupiter_s_moon_Europa.jpg").convert("RGB")
    scale = 1920 / im.height
    nw = int(im.width * scale)
    im_scaled = im.resize((nw, 1920), Image.Resampling.LANCZOS)
    x0 = (nw - 1080) // 2
    crop = im_scaled.crop((x0, 0, x0 + 1080, 1920))
    arr = np.array(crop, dtype=np.float32)
    safe_fade = 320
    arr[-safe_fade:, :] *= np.linspace(1.0, 0.15, safe_fade)[:, None, None]
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 05: {out_path}")

def build_scene_06(out_path):
    w, h = 1080, 1920
    canvas = Image.new("RGBA", (w, h), (3, 5, 14, 255))
    im = Image.open("scratch/europa_downloads/Europa_Clipper_artist_s_concept.jpg").convert("RGBA")
    scale = 1080 / im.width
    nh = int(im.height * scale)
    im_fit = im.resize((1080, nh), Image.Resampling.LANCZOS)
    arr = np.array(im_fit, dtype=np.float32)
    fade = 120
    arr[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(faded, (0, 420), faded)
    canvas.alpha_composite(create_starfield(w, h, seed=906))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 06: {out_path}")

def build_scene_07(out_path):
    w, h = 1080, 1920
    canvas = Image.new("RGBA", (w, h), (3, 5, 15, 255))
    im = Image.open("scratch/europa_downloads/New_evidence_of_watery_plumes_on_Jupiter_s_moon_Europa.jpg").convert("RGBA")
    scale = 1080 / im.width
    nh = int(im.height * scale)
    im_fit = im.resize((1080, nh), Image.Resampling.LANCZOS)
    arr = np.array(im_fit, dtype=np.float32)
    fade = 120
    arr[:fade, :, 3] *= np.linspace(0.0, 1.0, fade)[:, None]
    arr[-fade:, :, 3] *= np.linspace(1.0, 0.0, fade)[:, None]
    faded = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    canvas.paste(faded, (0, 380), faded)
    canvas.alpha_composite(create_starfield(w, h, seed=907))
    canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 07: {out_path}")

def build_scene_08(out_path):
    w, h = 1080, 1920
    im = Image.open("scratch/europa_downloads/Hubble_finds_evidence_of_persistent_water_vapour_atmosphere_on_Europa.jpg").convert("RGB")
    x0 = (im.width - 1080) // 2
    crop = im.crop((x0, 0, x0 + 1080, 1920))
    enh = ImageEnhance.Contrast(crop).enhance(1.15)
    arr = np.array(enh, dtype=np.float32)
    safe_fade = 320
    arr[-safe_fade:, :] *= np.linspace(1.0, 0.2, safe_fade)[:, None, None]
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(out_path, format="PNG", optimize=True)
    print(f"Generated Scene 08: {out_path}")

def build_scene_09(out_path):
    src = "dist/mamase-james-webb-time-machine-reel-v1/images/scene-11-mamase-outro.png"
    shutil.copy(src, out_path)
    im = Image.open(out_path)
    print(f"Copied Scene 09 Outro: {out_path} ({im.size})")

def main():
    assets_dir = Path("assets/europa_clipper_reel")
    stage_dir = Path("dist/mamase-europa-clipper-reel-v1")
    stage_images_dir = stage_dir / "images"
    zip_path = Path("dist/mamase-europa-clipper-reel-v1.zip")
    
    assets_dir.mkdir(parents=True, exist_ok=True)
    stage_images_dir.mkdir(parents=True, exist_ok=True)
    
    scenes_info = [
        ("scene-01-hook.png", build_scene_01),
        ("scene-02-ocean-paradox.png", build_scene_02),
        ("scene-03-tidal-heating.png", build_scene_03),
        ("scene-04-hydrothermal-vents.png", build_scene_04),
        ("scene-05-water-plumes.png", build_scene_05),
        ("scene-06-europa-clipper.png", build_scene_06),
        ("scene-07-tasting-plumes.png", build_scene_07),
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
            "id": "mamase-europa-clipper-reel-v1",
            "title": "Europa — ถ้ามีชีวิตอยู่ใต้ดวงจันทร์ของ Jupiter ล่ะ?",
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
                "narration": "สวัสดีครับ ยินดีต้อนรับสู่ Mamase จักรวาลของใจ วันนี้เราจะมาตั้งคำถามว่า... ถ้าเอเลียนในระบบสุริยะไม่ได้อยู่บนดาวอังคาร แต่อยู่ใต้ผืนน้ำแข็งของยูโรปาล่ะครับ?",
                "tts_text": "สวัสดีครับ ยินดีต้อนรับสู่ มามาเซ่ จักรวาลของใจ วันนี้เราจะมาตั้งคำถามว่า... ถ้าเอเลียนในระบบสุริยะไม่ได้อยู่บนดาวอังคาร แต่อยู่ใต้ผืนน้ำแข็งของ ยูโรปา ล่ะครับ?",
                "subtitle": "สิ่งมีชีวิตใต้ผืนน้ำแข็งยูโรปา?",
                "motion": "cinematic_push_in",
                "motion_speed": "normal",
                "motion_intensity": 0.2,
                "focus": "right",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Use the canonical Mamase anime presenter identity, friendly Thai male with tousled black hair, thin rectangular glasses and navy blazer, face-forward on the right for a talking shot. Premium science-documentary book-cover composition: icy moon Europa with orange-brown fractures, Jupiter glowing in background, Europa Clipper spacecraft, elegant Thai hook text in upper left. Subtle natural head movement and gentle pointing gesture, stable composition.",
                    "negative_prompt": "extra person, extra text, watermark, logo, distorted face, distorted hands, duplicated fingers, blurry spacecraft, flicker, jitter, sudden camera movement",
                    "seed": 901,
                    "frames": 81,
                    "steps": 25,
                    "lip_sync": True,
                    "character_id": "mamase-presenter-v1"
                }
            },
            {
                "id": "scene-02-ocean-paradox",
                "image": "images/scene-02-ocean-paradox.png",
                "narration": "ยูโรปา ดวงจันทร์ขนาดพอ ๆ กับดวงจันทร์ของเรา แต่ใต้เปลือกน้ำแข็งหนายี่สิบกิโลเมตร กลับซ่อน 'มหาสมุทรน้ำเหลว' ที่มีน้ำมากกว่าโลกทั้งใบรวมกันถึง 2 เท่า!",
                "tts_text": "ยูโรปา ดวงจันทร์ขนาดพอ ๆ กับดวงจันทร์ของเรา แต่ใต้เปลือกน้ำแข็งหนายี่สิบกิโลเมตร กลับซ่อน มหาสมุทรน้ำเหลว ที่มีน้ำมากกว่าโลกทั้งใบรวมกันถึง สอง เท่า!",
                "subtitle": "มหาสมุทรซ่อนเร้น มากกว่าโลก 2 เท่า",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic cross-section of Europa's interior structure, thick outer ice crust over a vast luminous deep blue global liquid ocean, rocky core at the center, scientifically accurate educational space documentary, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, aliens, flicker, jitter",
                    "seed": 902,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-03-tidal-heating",
                "image": "images/scene-03-tidal-heating.png",
                "narration": "ไกลจากดวงอาทิตย์ขนาดนั้น น้ำไม่แข็งหมดได้ยังไง? คำตอบคือ 'แรงดึงดูดไทดัล' ของดาวพฤหัสบดี ที่คอยบีบนวดยูโรปาจนเกิดความร้อนจากแกนในครับ",
                "tts_text": "ไกลจากดวงอาทิตย์ขนาดนั้น น้ำไม่แข็งหมดได้ยังไง? คำตอบคือ แรงดึงดูดไทดัล ของดาวพฤหัสบดี ที่คอยบีบนวดยูโรปาจนเกิดความร้อนจากแกนในครับ",
                "subtitle": "ดาวพฤหัสบดีบีบนวดให้เกิดความร้อน",
                "motion": "documentary_pan",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Massive banded planet Jupiter exerting immense gravitational tidal forces on orbiting icy moon Europa, gentle rhythmic flexing and heating of Europa's core, calm planetary motion in space, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, aliens, explosions, flicker, jitter",
                    "seed": 903,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-04-hydrothermal-vents",
                "image": "images/scene-04-hydrothermal-vents.png",
                "narration": "ที่ก้นมหาสมุทรลึก จึงอาจมีปล่องน้ำพุร้อนเหมือนก้นทะเลลึกบนโลก แหล่งพลังงานบริสุทธิ์ที่ทำให้สิ่งมีชีวิตถือกำเนิดได้... แม้ไม่เคยเห็นแสงอาทิตย์เลยสักครั้ง",
                "tts_text": "ที่ก้นมหาสมุทรลึก จึงอาจมีปล่องน้ำพุร้อนเหมือนก้นทะเลลึกบนโลก แหล่งพลังงานบริสุทธิ์ที่ทำให้สิ่งมีชีวิตถือกำเนิดได้... แม้ไม่เคยเห็นแสงอาทิตย์เลยสักครั้ง",
                "subtitle": "ปล่องน้ำร้อนก้นสมุทร แหล่งกำเนิดชีวิต",
                "motion": "gentle_float",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Dark abyss of Europa's subsurface ocean floor, active hydrothermal vents spewing warm mineral-rich black smoke, faint blue bioluminescent alien microbes drifting in warm thermal currents, majestic deep-sea astrobiology, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, monster, bright sunlight, flicker, jitter",
                    "seed": 904,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-05-water-plumes",
                "image": "images/scene-05-water-plumes.png",
                "narration": "และบางครั้ง แรงดันมหาศาลก็ระเบิดเป็น 'ไอน้ำพุพุ่งทะลุรอยแตก' ขึ้นสู่อวกาศ เป็นหลักฐานชัดเจนว่าข้างใต้มีของเหลวที่ยังมีชีวิตชีวาอยู่จริง ๆ",
                "tts_text": "และบางครั้ง แรงดันมหาศาลก็ระเบิดเป็น ไอน้ำพุพุ่งทะลุรอยแตก ขึ้นสู่อวกาศ เป็นหลักฐานชัดเจนว่าข้างใต้มีของเหลวที่ยังมีชีวิตชีวาอยู่จริง ๆ",
                "subtitle": "น้ำพุพุ่งทะลุรอยแตกสู่อวกาศ",
                "motion": "cinematic_pull_out",
                "motion_speed": "slow",
                "motion_intensity": 0.16,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Spectacular geysers and plumes of water vapor erupting from icy fractures on Europa high into space vacuum, glistening ice crystals against dark Jupiter backdrop, cinematic scientific realism, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, violent fireball explosion, flicker, jitter",
                    "seed": 905,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-06-europa-clipper",
                "image": "images/scene-06-europa-clipper.png",
                "narration": "นี่คือเหตุผลที่ NASA ส่งพระเอกอย่าง Europa Clipper ยานสำรวจดาวเคราะห์ที่ใหญ่ที่สุด ออกเดินทางไปพิสูจน์ความลับนี้ด้วยเรดาร์ส่องทะลุน้ำแข็ง",
                "tts_text": "นี่คือเหตุผลที่ นาซา ส่งพระเอกอย่าง ยูโรปา คลิปเปอร์ ยานสำรวจดาวเคราะห์ที่ใหญ่ที่สุด ออกเดินทางไปพิสูจน์ความลับนี้ด้วยเรดาร์ส่องทะลุน้ำแข็ง",
                "subtitle": "ยาน Europa Clipper บินสำรวจเจาะลึก",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "NASA Europa Clipper spacecraft in deep space, giant 30-meter solar arrays fully deployed, high-gain antenna and radar booms glinting in sunlight, approaching the cracked ice world Europa, high-detail aerospace engineering, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, cartoon, aliens, flicker, jitter",
                    "seed": 906,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-07-tasting-plumes",
                "image": "images/scene-07-tasting-plumes.png",
                "narration": "ยานไม่ต้องลงจอด แต่จะบินเฉียดผ่านละอองน้ำพุเพื่อ 'ชิม' สารอินทรีย์และเกลือแร่ ว่าที่นั่นมีองค์ประกอบที่พร้อมสำหรับสิ่งมีชีวิตหรือไม่",
                "tts_text": "ยานไม่ต้องลงจอด แต่จะบินเฉียดผ่านละอองน้ำพุเพื่อ ชิม สารอินทรีย์และเกลือแร่ ว่าที่นั่นมีองค์ประกอบที่พร้อมสำหรับสิ่งมีชีวิตหรือไม่",
                "subtitle": "บินเฉียด 'ชิม' สารอินทรีย์กลางอวกาศ",
                "motion": "documentary_pan",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Europa Clipper spacecraft performing low-altitude flyby directly through erupting water vapor plume above Europa, mass spectrometer collecting atmospheric dust and organic molecules, scientific drama, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, crash, explosion, cartoon, flicker, jitter",
                    "seed": 907,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-08-philosophical-climax",
                "image": "images/scene-08-philosophical-climax.png",
                "narration": "บางที ชีวิตในจักรวาลอาจไม่ได้เริ่มบนดาวเคราะห์ที่อบอุ่นใต้แสงตะวัน... แต่อาจซ่อนตัวอยู่ในมหาสมุทรอันเงียบสงบ ใต้เกราะน้ำแข็งนับล้านดวงครับ",
                "tts_text": "บางที ชีวิตในจักรวาลอาจไม่ได้เริ่มบนดาวเคราะห์ที่อบอุ่นใต้แสงตะวัน... แต่อาจซ่อนตัวอยู่ในมหาสมุทรอันเงียบสงบ ใต้เกราะน้ำแข็งนับล้านดวงครับ",
                "subtitle": "ชีวิตในมหาสมุทรใต้เกราะน้ำแข็ง",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Contemplative philosophical climax: glowing crescent Europa floating peacefully in vast cosmos beside giant Jupiter, mysterious blue warmth radiating through delicate ice fractures, serene space documentary poetry, no text.",
                    "negative_prompt": "text, subtitle, watermark, logo, flicker, jitter, violent action",
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
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 98,
                    "frames": 81,
                    "lip_sync": False
                }
            }
        ]
    }
    
    metadata_data = {
        "title": "Europa — ถ้ามีชีวิตอยู่ใต้ดวงจันทร์ของ Jupiter ล่ะ?",
        "description": "ใต้เปลือกน้ำแข็งหนา 20 กิโลเมตรของยูโรปา ซ่อนมหาสมุทรน้ำเหลวที่มีน้ำมากกว่าโลกทั้งใบถึง 2 เท่า! ทำไม NASA ถึงส่งยาน Europa Clipper ข้ามอวกาศไปพิสูจน์สิ่งมีชีวิตใต้ผืนน้ำแข็งนี้?\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#Mamase #Europa #EuropaClipper #Jupiter #ดาวพฤหัสบดี #อวกาศ #ดาราศาสตร์ #วิทยาศาสตร์"
    }
    
    script_path = stage_dir / "script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)
    print("Wrote script.json")
    
    meta_path = stage_dir / "video-metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata_data, f, ensure_ascii=False, indent=2)
    print("Wrote video-metadata.json")
    
    print(f"Building ZIP: {zip_path}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(script_path, arcname="script.json")
        zf.write(meta_path, arcname="video-metadata.json")
        for img_file in sorted((stage_dir / "images").glob("*.png")):
            zf.write(img_file, arcname=f"images/{img_file.name}")
            print(f" - Added to ZIP: images/{img_file.name} ({img_file.stat().st_size} bytes)")
    
    print(f"ZIP created: {zip_path.stat().st_size:,} bytes")
    
    print("\n--- Validating with PackageService ---")
    tmp_out = Path("scratch/validate_europa_out")
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
