import json
import shutil
import zipfile
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1]
    dist_dir = root / "dist"
    package_dir = dist_dir / "origin-of-universe"
    images_dir = package_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Source generated images from brain directory
    brain_dir = Path("/Users/zengcode/.gemini/antigravity-cli/brain/1be832f4-a6aa-4da5-9403-915429a3bf86")
    image_mappings = [
        ("cosmic_singularity_1788403796036.jpg", "scene-01.jpg"),
        ("big_bang_inflation_1788403810988.jpg", "scene-02.jpg"),
        ("first_stars_ignite_1788403827708.jpg", "scene-03.jpg"),
        ("supernova_stardust_1788403846588.jpg", "scene-04.jpg"),
        ("cosmos_within_us_1788403867777.jpg", "scene-05.jpg"),
    ]

    for src_name, dst_name in image_mappings:
        src = brain_dir / src_name
        dst = images_dir / dst_name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"Copied {src_name} -> {dst_name}")
        else:
            raise FileNotFoundError(f"Source image not found: {src}")

    script = {
        "project": {
            "id": "origin-of-universe",
            "title": "กำเนิดจักรวาล — ก่อนจะมีทุกสิ่ง จักรวาลเริ่มต้นอย่างไร?",
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
                "narration": "เคยสงสัยไหมครับว่า... ก่อนที่จะมีดวงดาว ก่อนที่จะมีโลก หรือแม้กระทั่งก่อนที่จะมีเวลา จักรวาลของเราเคยเป็นอย่างไร? ย้อนกลับไปเมื่อหนึ่งหมื่นสามพันแปดร้อยล้านปีก่อน ทุกสิ่งทุกอย่างในจักรวาลอันไพศาล ถูกอัดแน่นรวมกันอยู่ในจุดเล็กๆ จุดเดียว ที่ทั้งร้อนและหนาแน่นเกินกว่าจินตนาการ",
                "subtitle": "ก่อนจะมีทุกสิ่ง...\\nจักรวาลเริ่มต้นอย่างไร?",
                "motion": "cinematic_push_in",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic space documentary shot of primordial origin of the universe, a microscopic glowing point of infinite energy and light floating in dark cosmic void, subtle quantum fluctuations, mysterious atmosphere, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 101,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-02",
                "image": "images/scene-02.jpg",
                "narration": "แล้วจุดเปลี่ยนครั้งใหญ่ก็เกิดขึ้น... 'บิกแบง' ไม่ได้เป็นการระเบิดตูมตามในพื้นที่ว่าง แต่มันคือการพองตัวขยายออกอย่างรวดเร็วของพื้นที่และเวลาเอง ภายในเศษเสี้ยววินาที จักรวาลได้ถือกำเนิดและขยายตัวอย่างมหาศาล พร้อมกับการปลดปล่อยแสงสว่างแรกผ่านทะเลหมอกของอนุภาคพลังงาน",
                "tts_text": "แล้วจุดเปลี่ยนครั้งใหญ่ก็เกิดขึ้น... บิกแบง ไม่ได้เป็นการระเบิดตูมตามในพื้นที่ว่าง แต่มันคือการพองตัวขยายออกอย่างรวดเร็วของพื้นที่และเวลาเอง ภายในเศษเสี้ยววินาที จักรวาลได้ถือกำเนิดและขยายตัวอย่างมหาศาล พร้อมกับการปลดปล่อยแสงสว่างแรกผ่านทะเลหมอกของอนุภาคพลังงาน",
                "subtitle": "บิกแบง การพองตัว\\nของพื้นที่และเวลา",
                "motion": "zoom_out",
                "motion_speed": "normal",
                "motion_intensity": 0.18,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Cinematic space documentary shot of the Big Bang cosmic inflation, rapid expansion of vibrant plasma energy filaments, gold and violet shockwaves expanding outward across spacetime, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 202,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-03",
                "image": "images/scene-03.jpg",
                "narration": "หลังจากนั้น จักรวาลเข้าสู่ยุคมืดมิดยาวนานนับร้อยล้านปี ท่ามกลางหมอกก๊าซที่ล่องลอย จนกระทั่งแรงโน้มถ่วงเริ่มดึงมวลสารให้รวมตัวกัน และจุดประกายไฟแห่งแรกขึ้น... นั่นคือรุ่งอรุณแห่งจักรวาล เมื่อดาวฤกษ์รุ่นแรกได้กำเนิดขึ้นมาส่องสว่าง ขับไล่ความมืดมิดให้หมดสิ้นไป",
                "subtitle": "รุ่งอรุณจักรวาล\\nดาวฤกษ์รุ่นแรกส่องสว่าง",
                "motion": "drift_top_right",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cosmic Dawn, dense dark indigo hydrogen nebula condensing under gravity, first luminous blue-white supergiant star ignites and pierces darkness with brilliant starlight, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 303,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-04",
                "image": "images/scene-04.jpg",
                "narration": "ดาวฤกษ์เหล่านั้นไม่ได้มีอยู่เพียงเพื่อให้แสงสว่าง แต่ใจกลางของพวกมันเปรียบเหมือนเตาหลอมที่สร้างธาตุต่างๆ ทั้งคาร์บอน ออกซิเจน และเหล็ก เมื่อดาวสิ้นอายุขัยและแตกดับลง มันได้หว่านโปรยละอองธาตุเหล่านี้ไปทั่วอวกาศ กลายมาเป็นวัตถุดิบในการสร้างดาวเคราะห์ โลกใบนี้... และสิ่งมีชีวิต",
                "subtitle": "เตาหลอมแห่งดวงดาว\\nผู้สร้างสารตั้งต้นชีวิต",
                "motion": "pan_left_to_right_zoom_in",
                "motion_speed": "normal",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Colossal supernova explosion dispersing glowing cosmic dust, gold and ruby nebula filaments spreading stardust that forms solar systems and life, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 404,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-05",
                "image": "images/scene-05.jpg",
                "narration": "ดังนั้น ทุกอะตอมในตัวเรา เหล็กในเลือด หรือแคลเซียมในกระดูก ล้วนกำเนิดมาจากเศษซากของดวงดาวทั้งสิ้น เราไม่ได้เป็นเพียงสิ่งมีชีวิตที่ยืนอยู่ใต้จักรวาล แต่จักรวาลกำลังมองดูตัวเองผ่านดวงตาของเรา... ค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ",
                "tts_text": "ดังนั้น ทุกอะตอมในตัวเรา เหล็กในเลือด หรือแคลเซียมในกระดูก ล้วนกำเนิดมาจากเศษซากของดวงดาวทั้งสิ้น เราไม่ได้เป็นเพียงสิ่งมีชีวิตที่ยืนอยู่ใต้จักรวาล แต่จักรวาลกำลังมองดูตัวเองผ่านดวงตาของเรา... ค้นพบโลก ค้นพบใจ กับ มามาเซ่ จักรวาลของใจ",
                "subtitle": "ทุกอะตอมในตัวเรา\\nกำเนิดจากดวงดาว",
                "motion": "cinematic_pull_out",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Planet Earth viewed from deep space with magnificent glowing spiral Milky Way galaxy arching across starfield, soft stardust particles, profound cosmic wonder, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 505,
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

    # Build ZIP archive
    zip_path = dist_dir / "origin-of-universe.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(package_dir).as_posix())
    print(f"Created ZIP archive: {zip_path}")

if __name__ == "__main__":
    main()
