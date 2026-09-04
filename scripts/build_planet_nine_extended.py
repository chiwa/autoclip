import json
import random
import shutil
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_scene_01(out_path):
    # Scene 1: Caltech Planet Nine with Documentary Hook Title
    img = Image.open("dist/test_crop3_p9.jpg").convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_en = ImageFont.truetype("/System/Library/Fonts/Supplemental/SukhumvitSet.ttc", 76, index=5)
    font_th = ImageFont.truetype("/System/Library/Fonts/Supplemental/SukhumvitSet.ttc", 44, index=4)

    title_en = "PLANET NINE"
    title_th = "ดาวเคราะห์ดวงที่ 9 มีจริงไหม?"

    # Drop shadow & title
    draw.text((542, 262), title_en, font=font_en, fill=(0, 0, 0, 220), anchor="mm")
    draw.text((540, 260), title_en, font=font_en, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((542, 342), title_th, font=font_th, fill=(0, 0, 0, 220), anchor="mm")
    draw.text((540, 340), title_th, font=font_th, fill=(215, 235, 255, 240), anchor="mm")

    res = Image.alpha_composite(img, overlay).convert("RGB")
    res.save(out_path, quality=95)
    print("Saved Scene 01 (Caltech P9 + Title)")

def create_scene_02(out_path):
    # Scene 2: Hubble/STScI Kuiper belt object drifting in starry space
    img = Image.open("dist/full_kuiper_belt.jpg")
    # Crop clean inner space art without any borders
    box = (170, 230, 2230, 2430)
    inner = img.crop(box)
    iw, ih = inner.size
    target_w = int(ih * 9 / 16)
    left = (iw - target_w) // 2
    crop_kuiper = inner.crop((left, 0, left + target_w, ih)).resize((1080, 1920), Image.Resampling.LANCZOS)
    crop_kuiper.save(out_path, quality=95)
    print("Saved Scene 02 (Kuiper Belt / Sedna)")

def create_scene_03(out_path):
    # Scene 3: James Webb First Deep Field (Gravitational lensing / Deep Math)
    webb = Image.open("dist/test_crop_webb.jpg")
    webb.save(out_path, quality=95)
    print("Saved Scene 03 (James Webb Deep Field)")

def create_scene_04(out_path):
    # Scene 4: NASA Voyager 2 Ice Giant Globe with Starfield
    neptune = Image.open("dist/test_neptune_full.jpg")
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    random.seed(99)
    cx, cy, radius = 540, 960, 480
    for _ in range(250):
        sx = random.randint(0, 1080)
        sy = random.randint(0, 1920)
        dist = ((sx - cx)**2 + (sy - cy)**2)**0.5
        if dist > radius + 20:
            r = random.choice([1, 1, 1, 2])
            bright = random.randint(120, 240)
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(bright, bright, min(255, bright + 40), 200))
    res = Image.alpha_composite(neptune.convert("RGBA"), overlay).convert("RGB")
    res.save(out_path, quality=95)
    print("Saved Scene 04 (NASA Ice Giant + Starfield)")

def create_scene_05(out_path):
    # Scene 5: Fiery Swirling Black Hole accretion disk with Documentary Title
    img = Image.open("dist/test_crop_bh_direct.jpg").convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_en = ImageFont.truetype("/System/Library/Fonts/Supplemental/SukhumvitSet.ttc", 60, index=5)
    font_th = ImageFont.truetype("/System/Library/Fonts/Supplemental/SukhumvitSet.ttc", 38, index=4)

    title_en = "A PRIMORDIAL BLACK HOLE?"
    title_th = "หรือแท้จริงคือ... หลุมดำดึกดำบรรพ์?"

    draw.text((542, 232), title_en, font=font_en, fill=(0, 0, 0, 220), anchor="mm")
    draw.text((540, 230), title_en, font=font_en, fill=(255, 220, 150, 255), anchor="mm")
    draw.text((542, 302), title_th, font=font_th, fill=(0, 0, 0, 220), anchor="mm")
    draw.text((540, 300), title_th, font=font_th, fill=(255, 255, 255, 230), anchor="mm")

    res = Image.alpha_composite(img, overlay).convert("RGB")
    res.save(out_path, quality=95)
    print("Saved Scene 05 (Primordial Black Hole + Title)")

def create_scene_06(out_path):
    # Scene 6: ESO VLT Laser Guide Star into Milky Way
    laser = Image.open("dist/test_crop_laser.jpg")
    laser.save(out_path, quality=95)
    print("Saved Scene 06 (ESO VLT Laser into Milky Way)")

def create_scene_07(out_path):
    # Scene 7: Contemplative Human under starry night sky
    person = Image.open("dist/test_crop_person.jpg")
    person.save(out_path, quality=95)
    print("Saved Scene 07 (Human Contemplation under Stars)")

def main():
    root = Path(__file__).resolve().parents[1]
    dist_dir = root / "dist"
    package_dir = dist_dir / "planet-nine-extended"
    images_dir = package_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate 7 authentic visual scenes
    create_scene_01(images_dir / "scene-01.jpg")
    create_scene_02(images_dir / "scene-02.jpg")
    create_scene_03(images_dir / "scene-03.jpg")
    create_scene_04(images_dir / "scene-04.jpg")
    create_scene_05(images_dir / "scene-05.jpg")
    create_scene_06(images_dir / "scene-06.jpg")
    create_scene_07(images_dir / "scene-07.jpg")

    # 2. Copy Scene 08 from official Mamase brand outro
    src_scene_08 = root / "sample-package" / "lake-natron-mamase-v3" / "images" / "scene-08-brand-outro.png"
    shutil.copy2(src_scene_08, images_dir / "scene-08.png")
    print("Copied Scene 08 (Mamase Brand Outro)")

    # 3. Create script.json (8 scenes, ~64s, rich documentary pacing)
    script = {
        "project": {
            "id": "planet-nine-extended",
            "title": "Planet Nine มีจริงไหม? ดาวเคราะห์ยักษ์ดวงที่ 9 หรือหลุมดำจิ๋วที่ซ่อนอยู่ในความมืด (64 วินาที)",
            "language": "th-TH",
            "resolution": "1080x1920",
            "fps": 30
        },
        "voice": {
            "provider": "local",
            "voice": "thai-male-01",
            "speed": 0.95
        },
        "scenes": [
            {
                "id": "scene-01",
                "image": "images/scene-01.jpg",
                "narration": "ที่ขอบนอกสุดอันมืดมิดของระบบสุริยะ... นักดาราศาสตร์อาจกำลังเข้าใกล้การค้นพบดาวเคราะห์ขนาดยักษ์ดวงใหม่ ที่ซ่อนตัวอยู่มานานนับพันล้านปี",
                "subtitle": "ขอบนอกสุดของระบบสุริยะ...\\nอาจมีดาวเคราะห์ยักษ์ซ่อนอยู่",
                "motion": "cinematic_push_in",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Caltech official Planet Nine in deep space eclipsing the Milky Way galaxy, starry cosmos, cinematic space documentary.",
                    "negative_prompt": "watermark, blur, jitter, text",
                    "seed": 91,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-02",
                "image": "images/scene-02.jpg",
                "narration": "จุดเริ่มต้นเกิดจากการพบวัตถุขอบน้ำแข็งอย่าง เซดนา หลายชิ้น มีวงโคจรเอียงไปในทิศทางเดียวกันอย่างน่าประหลาด โอกาสที่จะเกิดเรื่องนี้โดยบังเอิญมีไม่ถึงศูนย์จุดศูนย์ศูนย์หนึ่งเปอร์เซ็นต์",
                "tts_text": "จุดเริ่มต้นเกิดจากการพบวัตถุขอบน้ำแข็งอย่าง เซด-นา หลายชิ้น มีวงโคจรเอียงไปในทิศทางเดียวกันอย่างน่าประหลาด โอกาสที่จะเกิดเรื่องนี้โดยบังเอิญมีไม่ถึง ศูนย์-จุด-ศูนย์-ศูนย์-หนึ่ง เปอร์เซ็นต์",
                "subtitle": "วงโคจรของวัตถุขอบน้ำแข็ง\\nเอียงไปทิศเดียวกันอย่างประหลาด",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Kuiper Belt frozen asteroid tumbling through deep space, distant Sun starburst glinting on icy cratered surface.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 92,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-03",
                "image": "images/scene-03.jpg",
                "narration": "ในปีสองพันสิบหก สองนักดาราศาสตร์จาก Caltech คำนวณพบว่า มีเพียงสิ่งเดียวที่อธิบายสิ่งนี้ได้ นั่นคือดาวเคราะห์ขนาดยักษ์ ที่มีแรงโน้มถ่วงมหาศาลคอยดึงพวกมันไว้",
                "tts_text": "ในปี สอง-พัน-สิบ-หก สองนักดาราศาสตร์จาก แคล-เทค คำนวณพบว่า มีเพียงสิ่งเดียวที่อธิบายสิ่งนี้ได้ นั่นคือดาวเคราะห์ขนาดยักษ์ ที่มีแรงโน้มถ่วงมหาศาลคอยดึงพวกมันไว้",
                "subtitle": "แบบจำลองทางฟิสิกส์ชี้ชัด\\nมีแรงโน้มถ่วงมหาศาลคอยควบคุม",
                "motion": "cinematic_push_in",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "James Webb First Deep Field, thousands of distant galaxies in deep cosmic void, gravitational lensing arcs, celestial wonder.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 93,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-04",
                "image": "images/scene-04.jpg",
                "narration": "แบบจำลองชี้ว่า มันคือดาวยักษ์น้ำแข็ง มวลมากกว่าโลกห้าถึงสิบเท่า อยู่ไกลกว่าดาวพลูโตถึงยี่สิบเท่า และใช้เวลานับหมื่นปีในการโคจรรอบดวงอาทิตย์เพียงหนึ่งรอบ",
                "tts_text": "แบบจำลองชี้ว่า มันคือดาวยักษ์น้ำแข็ง มวลมากกว่าโลก ห้า ถึง สิบ เท่า อยู่ไกลกว่าดาวพลูโตถึง ยี่-สิบ เท่า และใช้เวลานับหมื่นปีในการโคจรรอบดวงอาทิตย์เพียงหนึ่งรอบ",
                "subtitle": "มวลใหญ่กว่าโลก 5-10 เท่า\\nไกลกว่าดาวพลูโตถึง 20 เท่า",
                "motion": "drift_top_right",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "NASA Ice Giant planet globe suspended in starry space void, deep blue swirling atmosphere, cinematic slow drift.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 94,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-05",
                "image": "images/scene-05.jpg",
                "narration": "และทฤษฎีที่ชวนขนลุกยิ่งกว่า... นักฟิสิกส์บางกลุ่มเสนอว่า มันอาจไม่ใช่ดาวเคราะห์ แต่เป็นหลุมดำดึกดำบรรพ์ ขนาดเท่าผลส้มโอ ที่กำเนิดขึ้นตั้งแต่ยุคบิ๊กแบง!",
                "subtitle": "หรือแท้จริงแล้ว...\\nมันคือหลุมดำยุคบิ๊กแบง?",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Primordial black hole accretion disk with relativistic glowing plasma in deep space, cosmic event horizon, awe inspiring.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 95,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-06",
                "image": "images/scene-06.jpg",
                "narration": "เหตุผลที่เรายังมองไม่เห็น เพราะมันสะท้อนแสงอาทิตย์น้อยมาก แต่กล้องโทรทรรศน์รุ่นใหม่อย่าง Vera C. Rubin ที่ชิลี กำลังจะเปิดม่านสแกนหาคำตอบในเร็วๆ นี้",
                "tts_text": "เหตุผลที่เรายังมองไม่เห็น เพราะมันสะท้อนแสงอาทิตย์น้อยมาก แต่กล้องโทรทรรศน์รุ่นใหม่อย่าง วี-รา ซี รู-บิน ที่ชิลี กำลังจะเปิดม่านสแกนหาคำตอบในเร็วๆ นี้",
                "subtitle": "กล้องโทรทรรศน์รุ่นใหม่\\nกำลังจะเปิดม่านไขความลับนี้",
                "motion": "zoom_out",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Astronomical observatory firing powerful laser guide star towards the radiant core of the Milky Way, star studded night sky.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 96,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-07",
                "image": "images/scene-07.jpg",
                "narration": "ในวันที่เราคิดว่ารู้จักระบบสุริยะดีแล้ว จักรวาลก็ยังคงเตือนเราเสมอ... ว่าความรู้ของมนุษย์เรา เพิ่งจะเริ่มต้นขึ้นเท่านั้น",
                "subtitle": "จักรวาลยังคงเตือนเราเสมอ...\\nว่าความรู้ของเราเพิ่งเริ่มต้น",
                "motion": "gentle_float",
                "motion_speed": "slow",
                "motion_intensity": 0.10,
                "focus": "center",
                "transition": "fade_black",
                "wan": {
                    "prompt": "A contemplative person standing in a quiet field looking up at the vast starry cosmos, Milky Way galaxy, wonder and awe.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 97,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-08",
                "image": "images/scene-08.png",
                "narration": "ค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ",
                "tts_text": "ค้นพบโลก ค้นพบใจ กับ มามาเซ่ จักรวาลของใจ",
                "subtitle": "ค้นพบโลก ค้นพบใจ\\nMamase จักรวาลของใจ",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.10,
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

    script_path = package_dir / "script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print(f"Created {script_path}")

    # 4. Create video-metadata.json
    metadata = {
        "title": "Planet Nine มีจริงไหม? ดาวเคราะห์ยักษ์ดวงที่ 9 หรือหลุมดำจิ๋วที่ซ่อนอยู่ในความมืด 🪐🔭",
        "description": "ที่ขอบนอกสุดอันมืดมิดของระบบสุริยะ... มีอะไรซ่อนอยู่?\n\nในปี 2016 สองนักดาราศาสตร์จาก Caltech พบความผิดปกติครั้งประวัติศาสตร์ เมื่อวัตถุขอบน้ำแข็งอย่าง Sedna และวัตถุไกลโพ้นหลายชิ้น (eTNOs) มีวงโคจรเอียงไปในทิศทางเดียวกันอย่างน่าประหลาด ซึ่งโอกาสเกิดจากความบังเอิญมีไม่ถึง 0.001%\n\nแบบจำลองชี้ว่า มันคือ 'Planet Nine' ดาวเคราะห์ยักษ์น้ำแข็งที่มีมวลมากกว่าโลก 5-10 เท่า และอยู่ไกลกว่าดาวพลูโตถึง 20 เท่า ใช้เวลาโคจรรอบดวงอาทิตย์นานนับ 10,000–20,000 ปี\n\nแต่ที่น่าทึ่งยิ่งกว่า บางทฤษฎีเสนอว่า มันอาจไม่ใช่ดาวเคราะห์... แต่อาจเป็น 'หลุมดำดึกดำบรรพ์' (Primordial Black Hole) ขนาดเท่าผลส้มโอ ที่กำเนิดขึ้นตั้งแต่ยุคบิ๊กแบง!\n\nทำไมเราถึงยังมองไม่เห็น? และกล้องโทรทรรศน์รุ่นใหม่อย่าง Vera C. Rubin กำลังจะเปิดม่านตามล่าหาความจริงอย่างไร?\n\nในวันที่เราคิดว่ารู้จักบ้านหลังนี้ดีแล้ว จักรวาลก็ยังเตือนเราเสมอ... ว่าความรู้ของเราเพิ่งจะเริ่มต้นขึ้นเท่านั้น\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#PlanetNine #ดาวเคราะห์ดวงที่เก้า #ดาราศาสตร์ #อวกาศ #ระบบสุริยะ #วิทยาศาสตร์ #สารคดี #พลูโต #หลุมดำ #Astronomy #Space #SolarSystem #Caltech #NASA #JamesWebb #ESO #Mamase #จักรวาลของใจ #Shorts #YouTubeShorts #Reels #TikTok"
    }
    meta_path = package_dir / "video-metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Created {meta_path}")

    # 5. Build clean ZIP
    zip_path = dist_dir / "planet-nine-extended.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file() and not file_path.name.startswith("."):
                archive.write(file_path, file_path.relative_to(package_dir).as_posix())
    print(f"Created ZIP archive: {zip_path}")

if __name__ == "__main__":
    main()
