import json
import random
import shutil
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

def process_scene_01(out_path):
    # Caltech official Planet Nine artwork (Robert Hurt / Caltech-IPAC)
    p9 = Image.open("dist/test_crop3_p9.jpg")
    p9.save(out_path, quality=95)
    print("Saved Scene 01 (Caltech Planet Nine)")

def process_scene_02(out_path):
    # James Webb First Deep Field
    webb = Image.open("dist/test_crop_webb.jpg")
    webb.save(out_path, quality=95)
    print("Saved Scene 02 (James Webb Deep Field)")

def process_scene_03(out_path):
    # NASA Ice Giant Globe with starry space background
    neptune = Image.open("dist/test_neptune_full.jpg")
    # Add subtle distant stars in the black void around Neptune
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
    print("Saved Scene 03 (NASA Ice Giant + Starfield)")

def process_scene_04(out_path):
    # ESO Very Large Telescope Laser Guide Star towards Milky Way
    laser = Image.open("dist/test_crop_laser.jpg")
    laser.save(out_path, quality=95)
    print("Saved Scene 04 (ESO VLT Laser into Milky Way)")

def main():
    root = Path(__file__).resolve().parents[1]
    dist_dir = root / "dist"
    package_dir = dist_dir / "planet-nine-5scenes"
    images_dir = package_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 1. Process 4 authentic masterwork space visuals
    process_scene_01(images_dir / "scene-01.jpg")
    process_scene_02(images_dir / "scene-02.jpg")
    process_scene_03(images_dir / "scene-03.jpg")
    process_scene_04(images_dir / "scene-04.jpg")

    # 2. Copy Scene 05 from official Mamase brand outro
    src_scene_05 = root / "sample-package" / "lake-natron-mamase-v3" / "images" / "scene-08-brand-outro.png"
    shutil.copy2(src_scene_05, images_dir / "scene-05.png")
    print("Copied scene 5 brand outro")

    # 3. Update script.json with cinematic motion instructions
    script = {
        "project": {
            "id": "planet-nine-5scenes",
            "title": "Planet Nine มีจริงไหม? ดาวเคราะห์ยักษ์ดวงที่ 9 ที่ซ่อนอยู่ในความมืด (39 วินาที)",
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
                "narration": "คุณรู้ไหมครับว่า... ที่ขอบนอกสุดของระบบสุริยะ อาจมีดาวเคราะห์ขนาดยักษ์ดวงที่เก้า ซ่อนตัวอยู่ในความมืดมิด",
                "subtitle": "ดาวเคราะห์ดวงที่ 9\\nซ่อนตัวอยู่นอกระบบสุริยะ?",
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
                "narration": "ในปีสองพันสิบหก นักดาราศาสตร์พบว่า วัตถุขอบน้ำแข็งหลายชิ้น มีวงโคจรเอียงไปในทิศทางเดียวกัน เหมือนถูกแรงโน้มถ่วงมหาศาลดึงไว้",
                "tts_text": "ในปี สอง-พัน-สิบ-หก นักดาราศาสตร์พบว่า วัตถุขอบน้ำแข็งหลายชิ้น มีวงโคจรเอียงไปในทิศทางเดียวกัน เหมือนถูกแรงโน้มถ่วงมหาศาลดึงไว้",
                "subtitle": "แรงโน้มถ่วงลึกลับ\\nดึงวงโคจรให้เอียงทิศเดียวกัน",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "James Webb First Deep Field, thousands of distant galaxies in deep cosmic void, gravitational lensing arcs, celestial wonder.",
                    "negative_prompt": "watermark, blur, jitter, text",
                    "seed": 92,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-03",
                "image": "images/scene-03.jpg",
                "narration": "การคำนวณชี้ว่า มันน่าจะมีมวลใหญ่กว่าโลกถึงห้าถึงสิบเท่า และอยู่ไกลกว่าดาวพลูโตกว่ายี่สิบเท่า ใช้เวลานับหมื่นปีโคจรรอบดวงอาทิตย์",
                "subtitle": "มวลใหญ่กว่าโลก 5-10 เท่า\\nไกลกว่าพลูโต 20 เท่า",
                "motion": "drift_top_right",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "NASA Ice Giant planet globe suspended in starry space void, deep blue swirling atmosphere, cinematic slow drift.",
                    "negative_prompt": "watermark, blur, jitter, text",
                    "seed": 93,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-04",
                "image": "images/scene-04.jpg",
                "narration": "ที่ยังมองไม่เห็น เพราะมันสะท้อนแสงอาทิตย์น้อยมากในความมืด แต่นักดาราศาสตร์กำลังใช้กล้องโทรทรรศน์รุ่นใหม่ตามล่าตัวมันอยู่",
                "subtitle": "สะท้อนแสงน้อยมาก\\nกล้องรุ่นใหม่กำลังตามล่า",
                "motion": "zoom_out",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Astronomical observatory firing powerful laser guide star towards the radiant core of the Milky Way, star studded night sky.",
                    "negative_prompt": "watermark, blur, jitter, text",
                    "seed": 94,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-05",
                "image": "images/scene-05.png",
                "narration": "บ้านของเราอาจกว้างใหญ่กว่าที่คิด... ค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ",
                "tts_text": "บ้านของเราอาจกว้างใหญ่กว่าที่คิด... ค้นพบโลก ค้นพบใจ กับ มามาเซ่ จักรวาลของใจ",
                "subtitle": "จักรวาลยังมีเรื่องน่าค้นหา\\nMamase จักรวาลของใจ",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.10,
                "focus": "center",
                "transition": "fade_black",
                "wan": {
                    "prompt": "Mamase brand outro, glowing cyan orbiting planet in dark navy space, peaceful and contemplative.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 95,
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

    # 4. Write video-metadata.json
    metadata = {
        "title": "Planet Nine มีจริงไหม? ดาวเคราะห์ยักษ์ดวงที่ 9 ที่ซ่อนอยู่ในความมืด 🪐🔭",
        "description": "คุณรู้ไหมว่า... ที่ขอบนอกสุดของระบบสุริยะ อาจมีดาวเคราะห์ยักษ์ดวงที่เก้าซ่อนตัวอยู่?\n\nในปี 2016 นักดาราศาสตร์จาก Caltech พบความผิดปกติครั้งใหญ่ เมื่อวัตถุขอบน้ำแข็งหลายชิ้น (eTNOs) มีวงโคจรเอียงไปในทิศทางเดียวกันอย่างน่าประหลาด ซึ่งโอกาสที่จะเกิดเรื่องนี้โดยบังเอิญมีไม่ถึง 0.001%\n\nแบบจำลองชี้ว่า มันคือ 'Planet Nine' ดาวเคราะห์ยักษ์น้ำแข็งที่มีมวลมากกว่าโลก 5-10 เท่า และอยู่ไกลกว่าดาวพลูโตถึง 20 เท่า ใช้เวลานับหมื่นปีโคจรรอบดวงอาทิตย์ 1 รอบ\n\nทำไมเราถึงยังมองไม่เห็น? และกล้องโทรทรรศน์รุ่นใหม่อย่าง Vera C. Rubin กำลังตามหามันอย่างไร?\n\nเพราะบ้านของเราอาจกว้างใหญ่กว่าที่เราเคยคิด\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#PlanetNine #ดาวเคราะห์ดวงที่เก้า #ดาราศาสตร์ #อวกาศ #ระบบสุริยะ #วิทยาศาสตร์ #สารคดี #พลูโต #Astronomy #Space #SolarSystem #Caltech #NASA #JamesWebb #Mamase #จักรวาลของใจ #Shorts #YouTubeShorts #Reels #TikTok"
    }
    meta_path = package_dir / "video-metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Created {meta_path}")

    # 5. Build clean ZIP
    zip_path = dist_dir / "planet-nine-5scenes.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file() and not file_path.name.startswith("."):
                archive.write(file_path, file_path.relative_to(package_dir).as_posix())
    print(f"Created ZIP archive: {zip_path}")

if __name__ == "__main__":
    main()
