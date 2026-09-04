import json
import random
import shutil
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def make_scene_01(out_path):
    # Scene 1: Caltech Planet Nine with Documentary Hook Title
    img = Image.open("dist/test_crop3_p9.jpg").convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_en = ImageFont.truetype("/System/Library/Fonts/Supplemental/SukhumvitSet.ttc", 72, index=5)
    font_th = ImageFont.truetype("/System/Library/Fonts/Supplemental/SukhumvitSet.ttc", 40, index=4)

    title_en = "THE HUNT FOR PLANET NINE"
    title_th = "ทำไมกล้องระดับโลก ถึงยังหามันไม่เจอ?"

    draw.text((542, 262), title_en, font=font_en, fill=(0, 0, 0, 220), anchor="mm")
    draw.text((540, 260), title_en, font=font_en, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((542, 342), title_th, font=font_th, fill=(0, 0, 0, 220), anchor="mm")
    draw.text((540, 340), title_th, font=font_th, fill=(215, 235, 255, 240), anchor="mm")

    res = Image.alpha_composite(img, overlay).convert("RGB")
    res.save(out_path, quality=95)
    print("Saved Scene 01 (Planet Nine Hook Title)")

def make_scene_02(out_path):
    # Scene 2: Hubble/STScI Kuiper belt object in deep space
    img = Image.open("dist/full_kuiper_belt.jpg")
    box = (170, 230, 2230, 2430)
    inner = img.crop(box)
    iw, ih = inner.size
    target_w = int(ih * 9 / 16)
    left = (iw - target_w) // 2
    crop_kuiper = inner.crop((left, 0, left + target_w, ih)).resize((1080, 1920), Image.Resampling.LANCZOS)
    crop_kuiper.save(out_path, quality=95)
    print("Saved Scene 02 (Kuiper Belt / Sedna)")

def make_scene_03(out_path):
    # Scene 3: James Webb First Deep Field
    webb = Image.open("dist/test_crop_webb.jpg")
    webb.save(out_path, quality=95)
    print("Saved Scene 03 (James Webb Deep Field)")

def make_scene_04(out_path):
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

def make_scene_05(out_path):
    # Scene 5: Distant Sun and Solar System Orbits in Starry Deep Space
    sun = Image.open("dist/test_scene5_distant_sun.jpg")
    sun.save(out_path, quality=95)
    print("Saved Scene 05 (Distant Sun Twilight Realm)")

def make_scene_06(out_path):
    # Scene 6: Fiery Swirling Black Hole accretion disk with Title
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
    print("Saved Scene 06 (Primordial Black Hole + Title)")

def make_scene_07(out_path):
    # Scene 7: ESO VLT Laser Guide Star into Milky Way
    laser = Image.open("dist/test_crop_laser.jpg")
    laser.save(out_path, quality=95)
    print("Saved Scene 07 (ESO VLT Laser into Milky Way)")

def make_scene_08(out_path):
    # Scene 8: Contemplative Human under starry night sky
    person = Image.open("dist/test_crop_person.jpg")
    person.save(out_path, quality=95)
    print("Saved Scene 08 (Human Contemplation under Stars)")

def main():
    root = Path(__file__).resolve().parents[1]
    dist_dir = root / "dist"
    package_dir = dist_dir / "planet-nine-the-hunt-9scenes"
    images_dir = package_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate 8 visual scenes
    make_scene_01(images_dir / "scene-01.jpg")
    make_scene_02(images_dir / "scene-02.jpg")
    make_scene_03(images_dir / "scene-03.jpg")
    make_scene_04(images_dir / "scene-04.jpg")
    make_scene_05(images_dir / "scene-05.jpg")
    make_scene_06(images_dir / "scene-06.jpg")
    make_scene_07(images_dir / "scene-07.jpg")
    make_scene_08(images_dir / "scene-08.jpg")

    # 2. Copy Scene 09 from official Mamase brand outro
    src_scene_09 = root / "sample-package" / "lake-natron-mamase-v3" / "images" / "scene-08-brand-outro.png"
    shutil.copy2(src_scene_09, images_dir / "scene-09.png")
    print("Copied Scene 09 (Mamase Brand Outro)")

    # 3. Create script.json (9 scenes, ~78s, full mini-documentary)
    script = {
        "project": {
            "id": "planet-nine-the-hunt-9scenes",
            "title": "ตามล่า Planet Nine: ทำไมกล้องอวกาศระดับโลก ถึงยังหามันไม่เจอ? (78 วินาที)",
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
                "narration": "ทั้งที่มีกล้องโทรทรรศน์อวกาศมูลค่าแสนล้านอย่าง James Webb และ Hubble... แต่ทำไมนักวิทยาศาสตร์ถึงยังหา ดาวเคราะห์ดวงที่เก้า ไม่เจอ?",
                "tts_text": "ทั้งที่มีกล้องโทรทรรศน์อวกาศมูลค่าแสนล้านอย่าง เจมส์-เว็บบ์ และ ฮับ-เบิล... แต่ทำไมนักวิทยาศาสตร์ถึงยังหา ดาวเคราะห์ดวงที่เก้า ไม่เจอ?",
                "subtitle": "ทั้งที่มีกล้องอวกาศระดับโลก...\\nทำไมยังหาดาวเคราะห์ดวงที่ 9 ไม่เจอ?",
                "motion": "cinematic_push_in",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Caltech official Planet Nine in deep space eclipsing the Milky Way galaxy, starry cosmos, cinematic space documentary.",
                    "negative_prompt": "watermark, blur, jitter, text",
                    "seed": 101,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-02",
                "image": "images/scene-02.jpg",
                "narration": "หลักฐานไม่ได้มาจากการมองเห็น... แต่มาจากพฤติกรรมแปลกประหลาดของวัตถุน้ำแข็งนับสิบชิ้นในแถบไคเปอร์ ที่วงโคจรถูกดึงให้เอียงทำมุมสามสิบองศาไปในทิศทางเดียวกันทั้งหมด",
                "tts_text": "หลักฐานไม่ได้มาจากการมองเห็น... แต่มาจากพฤติกรรมแปลกประหลาดของวัตถุน้ำแข็งนับสิบชิ้นในแถบ ไค-เปอร์ ที่วงโคจรถูกดึงให้เอียงทำมุม สาม-สิบ องศาไปในทิศทางเดียวกันทั้งหมด",
                "subtitle": "หลักฐานมาจากพฤติกรรมประหลาด\\nของวัตถุน้ำแข็งในแถบไคเปอร์",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Kuiper Belt frozen asteroid tumbling through deep space, distant Sun starburst glinting on icy cratered surface.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 102,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-03",
                "image": "images/scene-03.jpg",
                "narration": "โอกาสที่เรื่องนี้จะเกิดขึ้นโดยความบังเอิญมีเพียงศูนย์จุดศูนย์ศูนย์หนึ่งเปอร์เซ็นต์ แปลว่ามีแรงโน้มถ่วงมหาศาล กำลังทำหน้าที่เป็นผู้บงการอยู่เบื้องหลังความมืด",
                "tts_text": "โอกาสที่เรื่องนี้จะเกิดขึ้นโดยความบังเอิญมีเพียง ศูนย์-จุด-ศูนย์-ศูนย์-หนึ่ง เปอร์เซ็นต์ แปลว่ามีแรงโน้มถ่วงมหาศาล กำลังทำหน้าที่เป็นผู้บงการอยู่เบื้องหลังความมืด",
                "subtitle": "โอกาสบังเอิญมีไม่ถึง 0.001%\\nต้องมีแรงโน้มถ่วงยักษ์อยู่เบื้องหลัง",
                "motion": "cinematic_push_in",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "James Webb First Deep Field, thousands of distant galaxies in deep cosmic void, gravitational lensing arcs, celestial wonder.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 103,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-04",
                "image": "images/scene-04.jpg",
                "narration": "การคำนวณชี้ว่า มันคือดาวยักษ์น้ำแข็ง มวลมากกว่าโลกถึงห้าถึงสิบเท่า แต่ที่ยากยิ่งกว่างมเข็มในมหาสมุทร คือระยะห่าง... มันอยู่ไกลกว่าดาวพลูโตถึงยี่สิบเท่า",
                "tts_text": "การคำนวณชี้ว่า มันคือดาวยักษ์น้ำแข็ง มวลมากกว่าโลกถึง ห้า ถึง สิบ เท่า แต่ที่ยากยิ่งกว่างมเข็มในมหาสมุทร คือระยะห่าง... มันอยู่ไกลกว่าดาวพลูโตถึง ยี่-สิบ เท่า",
                "subtitle": "มวลมากกว่าโลก 5-10 เท่า\\nแต่อยู่ไกลกว่าพลูโตถึง 20 เท่า",
                "motion": "drift_top_right",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "NASA Ice Giant planet globe suspended in starry space void, deep blue swirling atmosphere, cinematic slow drift.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 104,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-05",
                "image": "images/scene-05.jpg",
                "narration": "ที่ระยะห่างระดับนั้น แสงอาทิตย์แทบส่องไปไม่ถึง และแสงสะท้อนกลับมายังโลกจะลดลงตามกฎกำลังสี่ ทำให้มันมืดสนิทจนกล้องทั่วไปมองแทบไม่เห็น",
                "subtitle": "แสงอาทิตย์ส่องไปแทบไม่ถึง\\nทำให้มันมืดสนิทจนมองแทบไม่เห็น",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Tiny distant pinprick Sun with orbital rings glowing faintly in pitch black cosmic void, deep space solitude.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 105,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-06",
                "image": "images/scene-06.jpg",
                "narration": "ยิ่งไปกว่านั้น บางทฤษฎียังเสนอว่า มันอาจไม่ใช่ดาวเคราะห์เลยด้วยซ้ำ แต่อาจเป็น หลุมดำดึกดำบรรพ์ ขนาดเท่าลูกเทนนิส ที่มีมวลเท่าดาวเคราะห์ทั้งดวง!",
                "tts_text": "ยิ่งไปกว่านั้น บางทฤษฎียังเสนอว่า มันอาจไม่ใช่ดาวเคราะห์เลยด้วยซ้ำ แต่อาจเป็น หลุมดำดึกดำบรรพ์ ขนาดเท่าลูกเทนนิส ที่มีมวลเท่าดาวเคราะห์ทั้งดวง!",
                "subtitle": "หรือมันอาจไม่ใช่ดาวเคราะห์...\\nแต่อาจเป็นหลุมดำดึกดำบรรพ์?",
                "motion": "cinematic_push_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Primordial black hole accretion disk with relativistic glowing plasma in deep space, cosmic event horizon, awe inspiring.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 106,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-07",
                "image": "images/scene-07.jpg",
                "narration": "แต่การค้นหาใกล้ถึงจุดสิ้นสุดแล้ว เมื่อกล้องโทรทรรศน์ Vera C. Rubin พร้อมเซนเซอร์สามพันสองร้อยล้านพิกเซล จะเริ่มกวาดสแกนทั้งท้องฟ้า เพื่อไขความลับนี้ให้กระจ่าง",
                "tts_text": "แต่การค้นหาใกล้ถึงจุดสิ้นสุดแล้ว เมื่อกล้องโทรทรรศน์ วี-รา ซี รู-บิน พร้อมเซนเซอร์ สาม-พัน-สอง-ร้อย ล้านพิกเซล จะเริ่มกวาดสแกนทั้งท้องฟ้า เพื่อไขความลับนี้ให้กระจ่าง",
                "subtitle": "กล้องโทรทรรศน์รุ่นใหม่\\nพร้อมเซนเซอร์ 3,200 ล้านพิกเซล",
                "motion": "zoom_out",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Astronomical observatory firing powerful laser guide star towards the radiant core of the Milky Way, star studded night sky.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 107,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-08",
                "image": "images/scene-08.jpg",
                "narration": "ไม่ว่ามันจะเป็นดาวเคราะห์ยักษ์ หรือหลุมดำจิ๋ว... มันก็พิสูจน์แล้วว่า จักรวาลยังมีสิ่งมหัศจรรย์ รอให้หัวใจของเราออกไปค้นพบเสมอ",
                "subtitle": "จักรวาลยังมีสิ่งมหัศจรรย์\\nรอให้หัวใจของเราออกไปค้นพบ",
                "motion": "gentle_float",
                "motion_speed": "slow",
                "motion_intensity": 0.10,
                "focus": "center",
                "transition": "fade_black",
                "wan": {
                    "prompt": "A contemplative person standing in a quiet field looking up at the vast starry cosmos, Milky Way galaxy, wonder and awe.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 108,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-09",
                "image": "images/scene-09.png",
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
                    "seed": 109,
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
        "title": "ตามล่า Planet Nine: ทำไมกล้องอวกาศระดับโลก ถึงยังหามันไม่เจอ? 🪐🔭",
        "description": "ทั้งที่มีกล้องโทรทรรศน์อวกาศระดับตำนานอย่าง James Webb และ Hubble... แต่ทำไมนักดาราศาสตร์ถึงยังหา 'ดาวเคราะห์ดวงที่ 9' ไม่เจอ?\n\nคำตอบคือหลักฐานไม่ได้มาจากการมองเห็น แต่มาจากแรงโน้มถ่วงมหาศาลที่ดึงดูดวัตถุน้ำแข็งในแถบไคเปอร์ (eTNOs) ให้โคจรเอียงไปในทิศทางเดียวกันอย่างน่าอัศจรรย์ โอกาสที่จะเกิดเรื่องนี้โดยบังเอิญมีไม่ถึง 0.001%\n\nมันอยู่ไกลกว่าดาวพลูโตถึง 20 เท่า แสงอาทิตย์ส่องไปไม่ถึง และแสงสะท้อนกลับมาแทบเป็นศูนย์!\n\nและทฤษฎีที่ชวนขนลุกยิ่งกว่า... มันอาจไม่ใช่ดาวเคราะห์ แต่เป็น 'หลุมดำดึกดำบรรพ์' (Primordial Black Hole) ขนาดเท่าลูกเทนนิสที่หลงเหลือมาจากยุคบิ๊กแบง!\n\nกล้องโทรทรรศน์ Vera C. Rubin พร้อมเซนเซอร์ 3,200 ล้านพิกเซล กำลังจะเปิดม่านกวาดสแกนหาคำตอบในเร็วๆ นี้\n\nเพราะไม่ว่ามันจะเป็นอะไร จักรวาลก็ยังคงเตือนเราเสมอ... ว่าความรู้ของมนุษย์เราเพิ่งเริ่มต้นขึ้นเท่านั้น\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#PlanetNine #ดาวเคราะห์ดวงที่เก้า #ดาราศาสตร์ #อวกาศ #ระบบสุริยะ #วิทยาศาสตร์ #สารคดี #หลุมดำ #Astronomy #Space #SolarSystem #Caltech #NASA #JamesWebb #ESO #Mamase #จักรวาลของใจ #Shorts #YouTubeShorts #Reels #TikTok"
    }
    meta_path = package_dir / "video-metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Created {meta_path}")

    # 5. Build clean ZIP archive
    zip_path = dist_dir / "planet-nine-the-hunt-9scenes.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file() and not file_path.name.startswith("."):
                archive.write(file_path, file_path.relative_to(package_dir).as_posix())
    print(f"Created ZIP archive: {zip_path}")

if __name__ == "__main__":
    main()
