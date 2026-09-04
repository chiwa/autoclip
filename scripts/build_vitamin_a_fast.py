import json
import shutil
import zipfile
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1]
    dist_dir = root / "dist"
    src_dir = dist_dir / "vitamin-a-collagen-10scenes" / "images"
    package_dir = dist_dir / "vitamin-a-collagen-fast"
    images_dir = package_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 5 scene image mappings from the perfected 10-scene assets
    mappings = [
        (src_dir / "scene-01.jpg", "scene-01.jpg"),
        (src_dir / "scene-03.jpg", "scene-02.jpg"),
        (src_dir / "scene-04.jpg", "scene-03.jpg"),
        (src_dir / "scene-08.jpg", "scene-04.jpg"),
        (src_dir / "scene-10.png", "scene-05.png"),
    ]

    for src, dst_name in mappings:
        dst = images_dir / dst_name
        shutil.copy2(src, dst)
        print(f"Copied {src.name} -> {dst_name}")

    script = {
        "project": {
            "id": "vitamin-a-collagen-fast",
            "title": "วิตามินเอ กู้คอลลาเจนได้จริงไหม? สรุปใน 38 วินาที",
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
                "narration": "ในโลกสกินแคร์ มีสารเพียงกลุ่มเดียวที่งานวิจัยทั่วโลกยืนยันว่า 'กู้คอลลาเจนได้จริง' นั่นคือ เรตินอยด์ หรือวิตามินเอ",
                "tts_text": "ในโลกสกินแคร์ มีสารเพียงกลุ่มเดียวที่งานวิจัยทั่วโลกยืนยันว่า กู้คอลลาเจนได้จริง นั่นคือ เร-ติ-นอยด์ หรือวิตามินเอ",
                "subtitle": "สารกลุ่มเดียว...\\nที่กู้คอลลาเจนได้จริง",
                "motion": "cinematic_push_in",
                "motion_speed": "normal",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Clinical dermatology gold standard card, Vitamin A Retinoids, clean dark background, no flicker.",
                    "negative_prompt": "blur, jitter, watermark",
                    "seed": 10,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-02",
                "image": "images/scene-02.jpg",
                "narration": "หลังอายุยี่สิบ ผิวสูญเสียคอลลาเจนปีละหนึ่งเปอร์เซ็นต์ แต่เรตินอยด์สามารถสั่งงานระดับยีน ให้เซลล์สร้างคอลลาเจนใหม่ขึ้นมาทดแทน",
                "subtitle": "สั่งงานระดับยีน\\nกระตุ้นสร้างคอลลาเจนใหม่",
                "motion": "drift_top_right",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Cellular messenger diagram, RAR receptor pathway, activating collagen gene in skin cell nucleus.",
                    "negative_prompt": "blur, jitter, watermark",
                    "seed": 20,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-03",
                "image": "images/scene-03.jpg",
                "narration": "เซลล์ผิวจะตอบสนองต่อกรดเรติโนอิกเท่านั้น เรตินอลจึงต้องแปลงสภาพสองขั้น ส่วนเรตินัลแปลงเพียงขั้นเดียว จึงออกฤทธิ์ไวกว่า",
                "tts_text": "เซลล์ผิวจะตอบสนองต่อ กรด-เร-ติ-โน-อิก เท่านั้น เร-ติ-นอล จึงต้องแปลงสภาพสองขั้น ส่วน เร-ติ-นัล แปลงเพียงขั้นเดียว จึงออกฤทธิ์ไวกว่า",
                "subtitle": "เรตินัลแปลงขั้นเดียว\\nออกฤทธิ์ไวกว่าเรตินอล",
                "motion": "zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "The Retinoid Cascade diagram, step by step conversion to Retinoic Acid active form.",
                    "negative_prompt": "blur, jitter, watermark",
                    "seed": 30,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-04",
                "image": "images/scene-04.jpg",
                "narration": "ความลับคือมันมีพลังสองด้าน ทั้งกระตุ้นการสร้างคอลลาเจนใหม่ และช่วยบล็อกเอนไซม์ไม่ให้มาย่อยสลายคอลลาเจนเก่า",
                "subtitle": "พลังสองด้าน\\nสร้างใหม่ + หยุดการทำลาย",
                "motion": "pan_left_to_right_zoom_in",
                "motion_speed": "normal",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Dual action mechanism diagram, boost collagen and block MMP enzyme breakdown.",
                    "negative_prompt": "blur, jitter, watermark",
                    "seed": 40,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-05",
                "image": "images/scene-05.png",
                "narration": "เริ่มใช้จากความเข้มข้นต่ำ และทากันแดดทุกเช้า... ค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ",
                "tts_text": "เริ่มใช้จากความเข้มข้นต่ำ และทากันแดดทุกเช้า... ค้นพบโลก ค้นพบใจ กับ มามาเซ่ จักรวาลของใจ",
                "subtitle": "ความงามที่ยั่งยืน\\nMamase จักรวาลของใจ",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.10,
                "focus": "center",
                "transition": "fade_black",
                "wan": {
                    "prompt": "Mamase brand outro, glowing cyan orbiting planet in dark navy space, peaceful and contemplative.",
                    "negative_prompt": "blur, jitter, watermark",
                    "seed": 50,
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
        "title": "วิตามินเอ กู้คอลลาเจนได้จริงไหม? สรุปใน 38 วินาที 🧬✨",
        "description": "ในโลกสกินแคร์ มีสารเพียงกลุ่มเดียวที่งานวิจัยทางการแพทย์ทั่วโลกยืนยันตรงกันว่า 'กู้คอลลาเจนได้จริง' นั่นคือ วิตามินเอและกลุ่มเรตินอยด์ (Retinoids)\n\nสรุปกลไกชีววิทยาความงามใน 38 วินาที:\n• ผิวสูญเสียคอลลาเจนปีละ 1% หลังอายุ 20\n• เรตินอยด์ส่งสัญญาณระดับยีน สั่งเซลล์ไฟโบรบลาสต์ให้สร้างคอลลาเจนใหม่\n• เซลล์ผิวตอบสนองต่อกรดเรติโนอิก: เรตินอลแปลง 2 ขั้น ส่วนเรตินัลแปลงขั้นเดียวออกฤทธิ์ไวกว่า\n• พลังสองด้าน: สั่งสร้าง Pro-Collagen ใหม่ พร้อมบล็อกเอนไซม์ MMP ไม่ให้ทำลายคอลลาเจนเดิม\n• เริ่มจากความเข้มข้นต่ำ และทากันแดดทุกเช้า\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#วิทยาศาสตร์และความงาม #วิตามินเอ #เรตินอล #เรตินัล #คอลลาเจน #สกินแคร์ #Retinol #Retinal #Retinoids #SkincareScience #Dermatology #AntiAging #Collagen #Mamase #จักรวาลของใจ #Shorts #YouTubeShorts #Reels #TikTok"
    }
    meta_path = package_dir / "video-metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Created {meta_path}")

    zip_path = dist_dir / "vitamin-a-collagen-fast.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file() and not file_path.name.startswith("."):
                archive.write(file_path, file_path.relative_to(package_dir).as_posix())
    print(f"Created ZIP archive: {zip_path}")

if __name__ == "__main__":
    main()
