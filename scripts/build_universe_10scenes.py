import json
import shutil
import zipfile
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1]
    dist_dir = root / "dist"
    package_dir = dist_dir / "origin-of-universe-10scenes"
    images_dir = package_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    brain_dir = Path("/Users/zengcode/.gemini/antigravity-cli/brain/1be832f4-a6aa-4da5-9403-915429a3bf86")

    # 10 Scene image mappings
    mappings = [
        (brain_dir / "cosmic_void_time_1788404990016.jpg", "scene-01.jpg"),
        (brain_dir / "primordial_singularity_1788405323340.jpg", "scene-02.jpg"),
        (brain_dir / "big_bang_spacetime_1788405345479.jpg", "scene-03.jpg"),
        (brain_dir / "primordial_plasma_soup_1788405372267.jpg", "scene-04.jpg"),
        (brain_dir / "cosmic_dark_ages_1788405397193.jpg", "scene-05.jpg"),
        (brain_dir / "cosmic_web_gravity_1788405423558.jpg", "scene-06.jpg"),
        (brain_dir / "first_star_ignites_1788405448925.jpg", "scene-07.jpg"),
        (brain_dir / "supernova_elements_1788405478185.jpg", "scene-08.jpg"),
        (brain_dir / "cosmos_within_us_1788403867777.jpg", "scene-09.jpg"),
        (root / "sample-package" / "lake-natron-mamase-v3" / "images" / "scene-08-brand-outro.png", "scene-10.png"),
    ]

    for src, dst_name in mappings:
        dst = images_dir / dst_name
        if src.is_file():
            shutil.copy2(src, dst)
            print(f"Copied {src.name} -> {dst_name}")
        else:
            raise FileNotFoundError(f"Missing image: {src}")

    script = {
        "project": {
            "id": "origin-of-universe-10scenes",
            "title": "กำเนิดจักรวาล (10 ซีน 90 วินาที) — ก่อนจะมีทุกสิ่ง จักรวาลเริ่มต้นอย่างไร?",
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
                "narration": "เคยสงสัยไหมครับว่า... ก่อนที่จะมีโลก หรือแม้แต่เวลา จักรวาลของเราเคยเป็นอย่างไร?",
                "subtitle": "ก่อนจะมีทุกสิ่ง...\\nจักรวาลเริ่มต้นอย่างไร?",
                "motion": "cinematic_push_in",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic space documentary shot of infinite dark cosmic void before time and space existed, subtle deep indigo mist, contemplative atmosphere, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 11,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-02",
                "image": "images/scene-02.jpg",
                "narration": "ย้อนไปหนึ่งหมื่นสามพันแปดร้อยล้านปีก่อน ทุกสิ่งถูกอัดแน่นอยู่ในจุดจิ๋วเพียงจุดเดียว ที่ร้อนและหนาแน่นเป็นอนันต์",
                "subtitle": "จุดซิงกูลาริตี\\nร้อนและหนาแน่นเป็นอนันต์",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Cinematic space documentary shot of primordial cosmic singularity, ultra dense microscopic glowing pinpoint of blinding golden light and infinite energy, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 22,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-03",
                "image": "images/scene-03.jpg",
                "narration": "แล้วบิกแบงก็เกิดขึ้น... มันไม่ใช่การระเบิดในอวกาศ แต่คือกาลอวกาศที่พองตัวขยายออกอย่างฉับพลัน",
                "tts_text": "แล้ว บิกแบง ก็เกิดขึ้น... มันไม่ใช่การระเบิดในอวกาศ แต่คือกาลอวกาศที่พองตัวขยายออกอย่างฉับพลัน",
                "subtitle": "บิกแบง การพองตัว\\nของพื้นที่และเวลา",
                "motion": "zoom_out",
                "motion_speed": "normal",
                "motion_intensity": 0.18,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "The Big Bang cosmic inflation, radiant bursts of primordial plasma stretching spacetime, golden and violet energy shockwaves, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 33,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-04",
                "image": "images/scene-04.jpg",
                "narration": "ภายในเศษเสี้ยววินาที ทะเลหมอกพลังงานอันร้อนจัด ค่อยๆ เย็นตัวลงจนกลายเป็นอะตอมแรกของเอกภพ",
                "subtitle": "ทะเลหมอกพลังงาน\\nก่อตัวเป็นอะตอมแรก",
                "motion": "gentle_float",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Primordial soup of particles, glowing sea of hot plasma cooling into first hydrogen and helium atoms, golden amber particles, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 44,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-05",
                "image": "images/scene-05.jpg",
                "narration": "จากนั้น จักรวาลเข้าสู่ 'ยุคมืด' ยาวนานนับร้อยล้านปี ท่ามกลางหมอกก๊าซที่ลอยอยู่อย่างเงียบงัน ไร้แสงดาว",
                "subtitle": "ยุคมืดร้อยล้านปี\\nไร้แสงแห่งดวงดาว",
                "motion": "pan_left_to_right",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cosmic Dark Ages, deep indigo hydrogen gas clouds drifting in silent space, pitch dark cosmos without stars, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 55,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-06",
                "image": "images/scene-06.jpg",
                "narration": "จนกระทั่งแรงโน้มถ่วง ดึงมวลก๊าซให้ค่อยๆ ยุบรวมตัวกัน เกิดเป็นโครงข่ายจักรวาลอันไพศาล",
                "subtitle": "แรงโน้มถ่วงดึงดูด\\nโครงข่ายจักรวาล",
                "motion": "drift_top_right",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Cosmic web forming under gravity, spiderweb filaments of gas condensing and interconnecting, galactic seeds, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 66,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-07",
                "image": "images/scene-07.jpg",
                "narration": "นั่นคือรุ่งอรุณแห่งจักรวาล... เมื่อดาวฤกษ์ดวงแรกจุดประกายขึ้น เปล่งแสงสว่างแรกขับไล่ความมืดมิด",
                "subtitle": "รุ่งอรุณจักรวาล\\nดาวฤกษ์ดวงแรกส่องสว่าง",
                "motion": "cinematic_push_in",
                "motion_speed": "normal",
                "motion_intensity": 0.16,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cosmic Dawn, first massive blue-white supergiant star ignites, piercing starlight tearing through dark nebulae, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 77,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-08",
                "image": "images/scene-08.jpg",
                "narration": "ใจกลางดาวหลอมธาตุสำคัญอย่างเหล็กและคาร์บอน ก่อนจะระเบิดเป็นซูเปอร์โนวา หว่านโปรยสู่ห้วงอวกาศ",
                "tts_text": "ใจกลางดาวหลอมธาตุสำคัญอย่างเหล็กและคาร์บอน ก่อนจะระเบิดเป็น ซูเปอร์โนวา หว่านโปรยสู่ห้วงอวกาศ",
                "subtitle": "เตาหลอมธาตุ\\nระเบิดเป็นซูเปอร์โนวา",
                "motion": "pan_left_to_right_zoom_in",
                "motion_speed": "normal",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Massive star exploding as supernova, dispersing stardust heavy elements ruby red and gold into cosmos, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 88,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-09",
                "image": "images/scene-09.jpg",
                "narration": "เศษซากฝุ่นดาวเหล่านั้น ก่อตัวขึ้นใหม่เป็นระบบสุริยะ กลายมาเป็นโลก... และสารตั้งต้นของชีวิต",
                "subtitle": "กำเนิดระบบสุริยะ\\nโลก และสารตั้งต้นชีวิต",
                "motion": "zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Planet Earth forming in solar system viewed from space, blue ocean world, swirling clouds and stardust, no text.",
                    "negative_prompt": "text, watermark, flicker, jitter, blurry",
                    "seed": 99,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-10",
                "image": "images/scene-10.png",
                "narration": "ทุกอะตอมในตัวเรา จึงเกิดจากดวงดาวทั้งสิ้น... ค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ",
                "tts_text": "ทุกอะตอมในตัวเรา จึงเกิดจากดวงดาวทั้งสิ้น... ค้นพบโลก ค้นพบใจ กับ มามาเซ่ จักรวาลของใจ",
                "subtitle": "ทุกอะตอมในตัวเรา\\nกำเนิดจากดวงดาว",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.10,
                "focus": "center",
                "transition": "fade_black",
                "wan": {
                    "prompt": "Mamase brand outro, glowing cyan orbiting planet in dark navy space, peaceful and contemplative, no text.",
                    "negative_prompt": "flicker, jitter, blurry",
                    "seed": 100,
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

    metadata = {
        "title": "ก่อนจะมีทุกสิ่ง... จักรวาลเริ่มต้นอย่างไร? (90 วินาที) 🌌",
        "description": "เคยสงสัยไหมครับว่า... ก่อนที่จะมีโลก หรือแม้แต่เวลา จักรวาลของเราเคยเป็นอย่างไร?\n\nคลิป 90 วินาทีนี้จะพาคุณเดินทางย้อนเวลากลับไป 13,800 ล้านปีก่อน ตั้งแต่จุดซิงกูลาริตีที่อัดแน่นอย่างมหาศาล สู่การพองตัวของกาลอวกาศใน 'บิกแบง' ทะเลหมอกอนุภาคปฐมกาล ยุคมืดร้อยล้านปี การก่อกำเนิดดาวฤกษ์ดวงแรก และการระเบิดซูเปอร์โนวาที่หว่านโปรยธาตุสารตั้งต้นของชีวิตมาสู่โลกใบนี้\n\nทุกอะตอมในร่างกายของเรา ล้วนมาจากฝุ่นผงของดวงดาวทั้งสิ้น\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#กำเนิดจักรวาล #บิกแบง #ดาราศาสตร์ #วิทยาศาสตร์ #สารคดี #ฟิสิกส์ #ซูเปอร์โนวา #BigBang #Universe #Cosmology #Astronomy #Science #Stardust #Mamase #จักรวาลของใจ #Shorts #YouTubeShorts #Reels #TikTok"
    }
    metadata_path = package_dir / "video-metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Created {metadata_path}")

    # Build ZIP
    zip_path = dist_dir / "origin-of-universe-10scenes.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file() and not file_path.name.startswith("."):
                archive.write(file_path, file_path.relative_to(package_dir).as_posix())
    print(f"Created ZIP archive: {zip_path}")

if __name__ == "__main__":
    main()
