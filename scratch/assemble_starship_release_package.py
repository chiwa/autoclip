import json
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path(".")
SOURCE_DIR = Path("scratch/starship_master_final")
ASSET_DIR = Path("assets/starship_v3_flight_12_reel")
ASSET_DIR.mkdir(parents=True, exist_ok=True)

DIST_DIR = Path("dist/mamase-starship-v3-flight-12-reel-v1")
DIST_IMAGES = DIST_DIR / "images"
DIST_IMAGES.mkdir(parents=True, exist_ok=True)

scenes = [
    "scene-01-hook.png",
    "scene-02-v3-debut-liftoff.png",
    "scene-03-raptor3-fury.png",
    "scene-04-staging-anomaly.png",
    "scene-05-booster-splashdown.png",
    "scene-06-starship-orbital-insertion.png",
    "scene-07-starlink-payload-deploy.png",
    "scene-08-hypersonic-plasma-reentry.png",
    "scene-09-moon-mars-refueling-future.png",
    "scene-10-mamase-outro.png"
]

# 1. Copy images to dist/images/ and assets/
for sc in scenes:
    src = SOURCE_DIR / sc
    assert src.exists(), f"Missing {src}"
    shutil.copy2(src, DIST_IMAGES / sc)
    shutil.copy2(src, ASSET_DIR / sc)

print(f"Copied {len(scenes)} images to {DIST_IMAGES} and {ASSET_DIR}")

# 2. Build video-metadata.json
video_metadata = {
    "title": "SpaceX เปิดตัว Starship V3 และบิน Flight 12: ก้าวประวัติศาสตร์สู่ดาวอังคาร",
    "description": "ก้าวสำคัญของมนุษยชาติสู่การเป็นสิ่งมีชีวิตหลายดาวเคราะห์! สรุปภารกิจประวัติศาสตร์ SpaceX เปิดตัว Starship V3 และบินทดสอบ Integrated Flight Test 12 (Flight 12)\n\nเจาะลึกการอัปเกรดครั้งยิ่งใหญ่:\n- ยาน Starship และบูสเตอร์ Super Heavy รุ่น V3 สูงทะลุ 124 เมตร ทรงพลังที่สุดในโลก\n- ขุมพลังเครื่องยนต์ Raptor 3 รวม 33 ตัว ดีไซน์ท่อและระบบหล่อเย็นใหม่หมด\n- วินาทีระทึก Hot-Staging แยกตัวสำเร็จ ก่อนบูสเตอร์เครื่องยนต์ดับและดิ่งลงสู่อ่าวเม็กซิโก\n- ความสำเร็จในการปล่อยเพย์โหลดจำลอง Starlink 20 ดวง พร้อมดาวเทียมสื่อสารจริง 2 ดวงในวงโคจร\n- การฝ่าชั้นบรรยากาศด้วยพลาสมาสีม่วงห่อหุ้มลำยาน Starship\n\nทุกความล้มเหลวคือบันไดสู่ความสำเร็จ! ติดตามเรื่องราวอวกาศและจักรวาลไปกับเรา\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#Starship #StarshipV3 #SpaceX #Flight12 #ElonMusk #อวกาศ #ดาราศาสตร์ #สารคดี #วิทยาศาสตร์ #ดาวอังคาร #Raptor3 #Starlink #Mamase #จักรวาลของใจ"
}

with open(DIST_DIR / "video-metadata.json", "w", encoding="utf-8") as f:
    json.dump(video_metadata, f, ensure_ascii=False, indent=2)

with open(ASSET_DIR / "video-metadata.json", "w", encoding="utf-8") as f:
    json.dump(video_metadata, f, ensure_ascii=False, indent=2)

# 3. Build script.json with valid motion presets and focus values
script_data = {
    "project": {
        "id": "mamase-starship-v3-flight-12-reel-v1",
        "title": "SpaceX เปิดตัว Starship V3 และบิน Flight 12: ก้าวประวัติศาสตร์สู่ดาวอังคาร",
        "language": "th-TH",
        "resolution": "1080x1920",
        "fps": 30
    },
    "voice": {
        "provider": "google-gemini",
        "voice": "Fenrir",
        "speed": 1.0,
        "style_prompt": "Read aloud in a natural, playful, conversational Thai voice. Sound relaxed, confident, and slightly cheeky, like you're casually telling a fascinating story to a close friend. Keep the energy lively but effortless — never sound like a news presenter, announcer, or formal narrator. Use natural changes in pitch and rhythm. Occasionally stretch or emphasize important words for personality. Add small pauses before surprising or funny moments, as if you're building anticipation. The delivery should feel spontaneous and human, with a subtle smile in the voice. Let some sentences start softly and then become more animated when the story gets interesting. Keep the pacing medium to slightly fast, but don't rush. Avoid perfectly even timing between sentences. For surprising facts, sound genuinely impressed or amused, as if you're thinking: 'เฮ้ย... จริงดิ?' Overall personality: friendly, curious, mischievous, charming, expressive, slightly teasing, and naturally excited. Think of a charismatic Thai content creator explaining something interesting on TikTok or Reels — casual, fun, and easy to listen to. Never sound robotic, overly dramatic, overly cute, or like you're reading from a script."
    },
    "scenes": [
        {
            "id": "scene-01-hook",
            "image": "images/scene-01-hook.png",
            "narration": "SpaceX เปิดตัว Starship V3 ยานอวกาศที่จะพาเราไปดาวอังคาร และเตรียมบินทดสอบใน Flight 12!",
            "tts_text": "สเปซเอ็กซ์ เปิดตัว สตาร์ชิป วีทรี ยานอวกาศที่จะพาเราไปดาวอังคาร และเตรียมบินทดสอบใน ไฟลต์ ทเวลฟ์!",
            "subtitle": "SpaceX เปิดตัว Starship V3 เตรียมบิน Flight 12!",
            "motion": "slow_zoom_in",
            "motion_speed": "slow",
            "motion_intensity": 0.10,
            "focus": "right",
            "transition": "dissolve",
            "wan": {
                "prompt": "Use the canonical Mamase anime presenter identity, friendly Thai male with tousled black hair, thin rectangular glasses and navy blazer, talking enthusiastically on the right side of the frame. On the left is the colossal Starship V3 full stack rocket standing on the orbital launch pad with Mechazilla catch tower under blue sky with gold Thai typography in upper left. Subtle natural head movement, expressive speaking gestures, stable composition.",
                "negative_prompt": "extra person, extra text, watermark, logo, distorted face, distorted hands, duplicated fingers, blurry, flicker, jitter",
                "seed": 801,
                "frames": 81,
                "steps": 25,
                "lip_sync": True,
                "character_id": "mamase-presenter-v1"
            }
        },
        {
            "id": "scene-02-v3-debut-liftoff",
            "image": "images/scene-02-v3-debut-liftoff.png",
            "narration": "Starship และ Super Heavy รุ่น V3 มีความสูงทะลุ 124 เมตร ทรงพลังที่สุดในประวัติศาสตร์มนุษยชาติ ทะยานขึ้นจากฐานปล่อยอย่างสง่างาม",
            "tts_text": "สตาร์ชิป และ ซูเปอร์เฮฟวี รุ่น วีทรี มีความสูงทะลุ หนึ่งร้อยยี่สิบสี่เมตร ทรงพลังที่สุดในประวัติศาสตร์มนุษยชาติ ทะยานขึ้นจากฐานปล่อยอย่างสง่างาม",
            "subtitle": "Starship V3 สูง 124 เมตร ทรงพลังที่สุดในประวัติศาสตร์",
            "motion": "pan_up",
            "motion_speed": "slow",
            "motion_intensity": 0.12,
            "focus": "bottom",
            "transition": "fade",
            "wan": {
                "prompt": "Ultra realistic cinematic footage of Starship V3 and Super Heavy lifting off from Starbase launch pad, towering columns of roaring orange rocket fire and billowing white deluge steam clouds expanding outwards, rocket ascending powerfully into the sky, no text.",
                "negative_prompt": "text, watermark, logo, cartoon, blurry, distortion, flicker, jitter",
                "seed": 802,
                "frames": 81,
                "steps": 22,
                "lip_sync": False
            }
        },
        {
            "id": "scene-03-raptor3-fury",
            "image": "images/scene-03-raptor3-fury.png",
            "narration": "ใต้ฐานติดตั้งเครื่องยนต์ Raptor 3 รวม 33 ตัว พัฒนาท่อส่งและระบบหล่อเย็นใหม่หมด เพิ่มแรงขับมหาศาลและลดน้ำหนักโครงสร้าง",
            "tts_text": "ใต้ฐานติดตั้งเครื่องยนต์ แร็ปเตอร์ ทรี รวม สามสิบสาม ตัว พัฒนาท่อส่งและระบบหล่อเย็นใหม่หมด เพิ่มแรงขับมหาศาลและลดน้ำหนักโครงสร้าง",
            "subtitle": "ขุมพลัง 33 เครื่องยนต์ Raptor 3 ดีไซน์ท่อส่งใหม่หมด",
            "motion": "slow_zoom_in",
            "motion_speed": "slow",
            "motion_intensity": 0.10,
            "focus": "center",
            "transition": "dissolve",
            "wan": {
                "prompt": "Cinematic close-up high speed shot of SpaceX Raptor 3 rocket engine firing, glowing purple and magenta supersonic shock diamonds visible inside the incandescent methane flame plume, violent atmospheric turbulence and smoke, no text.",
                "negative_prompt": "text, watermark, logo, cartoon, blurry, distortion, flicker, jitter",
                "seed": 803,
                "frames": 81,
                "steps": 22,
                "lip_sync": False
            }
        },
        {
            "id": "scene-04-staging-anomaly",
            "image": "images/scene-04-staging-anomaly.png",
            "narration": "แต่นาทีสำคัญมาถึง... หลัง Hot-Staging แยกตัวสำเร็จ เกิดปัญหาเครื่องยนต์บูสเตอร์ดับก่อนกำหนด จึงต้องยกเลิกการบินกลับฐาน",
            "tts_text": "แต่นาทีสำคัญมาถึง... หลัง ฮ็อต สเตจจิง แยกตัวสำเร็จ เกิดปัญหาเครื่องยนต์บูสเตอร์ดับก่อนกำหนด จึงต้องยกเลิกการบินกลับฐาน",
            "subtitle": "Hot-Staging สำเร็จ แต่เครื่องยนต์บูสเตอร์มีปัญหา",
            "motion": "pan_left_to_right",
            "motion_speed": "slow",
            "motion_intensity": 0.12,
            "focus": "center",
            "transition": "fade",
            "wan": {
                "prompt": "Cinematic space shot of Starship upper stage separating from Super Heavy booster high above Earth curvature in outer space, cold gas attitude thrusters venting white gas jets, golden sunlight flaring off the spacecraft hull against the dark cosmos, no text.",
                "negative_prompt": "text, watermark, logo, cartoon, blurry, distortion, flicker, jitter",
                "seed": 804,
                "frames": 81,
                "steps": 22,
                "lip_sync": False
            }
        },
        {
            "id": "scene-05-booster-splashdown",
            "image": "images/scene-05-booster-splashdown.png",
            "narration": "ทีมควบคุมตัดสินใจเปลี่ยนแผน นำ Super Heavy ดิ่งลงสู่ผืนน้ำในอ่าวเม็กซิโก กระแทกผิวน้ำอย่างรุนแรง แต่ได้ข้อมูลวิกฤตเพียบ",
            "tts_text": "ทีมควบคุมตัดสินใจเปลี่ยนแผน นำ ซูเปอร์เฮฟวี ดิ่งลงสู่ผืนน้ำในอ่าวเม็กซิโก กระแทกผิวน้ำอย่างรุนแรง แต่ได้ข้อมูลวิกฤตเพียบ",
            "subtitle": "เปลี่ยนแผนนำ Super Heavy ลงทะเลในอ่าวเม็กซิโก",
            "motion": "pan_down",
            "motion_speed": "slow",
            "motion_intensity": 0.12,
            "focus": "top",
            "transition": "dissolve",
            "wan": {
                "prompt": "Dramatic cinematic shot of the massive Super Heavy booster descending vertically through warm sunset dusk sky towards coastal waters, rocket engines firing a brilliant landing burn illuminating the water surface below, no text.",
                "negative_prompt": "text, watermark, logo, cartoon, blurry, distortion, flicker, jitter",
                "seed": 805,
                "frames": 81,
                "steps": 22,
                "lip_sync": False
            }
        },
        {
            "id": "scene-06-starship-orbital-insertion",
            "image": "images/scene-06-starship-orbital-insertion.png",
            "narration": "ส่วนตัวยาน Starship ยังคงทะยานต่อไป เข้าสู่วงโคจรระดับต่ำของโลกได้อย่างสมบูรณ์แบบ ท่ามกลางภาพอวกาศที่งดงามเกินบรรยาย",
            "tts_text": "ส่วนตัวยาน สตาร์ชิป ยังคงทะยานต่อไป เข้าสู่วงโคจรระดับต่ำของโลกได้อย่างสมบูรณ์แบบ ท่ามกลางภาพอวกาศที่งดงามเกินบรรยาย",
            "subtitle": "ยาน Starship เข้าสู่วงโคจรระดับต่ำของโลกสมบูรณ์แบบ",
            "motion": "pan_left_to_right",
            "motion_speed": "slow",
            "motion_intensity": 0.10,
            "focus": "center",
            "transition": "dissolve",
            "wan": {
                "prompt": "Cinematic documentary shot of Starship spacecraft gliding gracefully in low Earth orbit, radiant sunlight gleaming across curved stainless steel heat shield tiles, vibrant electric blue atmospheric limb glowing below in dark starry space, no text.",
                "negative_prompt": "text, watermark, logo, cartoon, blurry, distortion, flicker, jitter",
                "seed": 806,
                "frames": 81,
                "steps": 22,
                "lip_sync": False
            }
        },
        {
            "id": "scene-07-starlink-payload-deploy",
            "image": "images/scene-07-starlink-payload-deploy.png",
            "narration": "และนี่คือไฮไลต์! การทดสอบปล่อยดาวเทียม Starlink จำลอง 20 ดวง พร้อมดาวเทียมสื่อสารจริงอีก 2 ดวง สำเร็จลุล่วงตามแผน",
            "tts_text": "และนี่คือไฮไลต์! การทดสอบปล่อยดาวเทียม สตาร์ลิงก์ จำลอง ยี่สิบ ดวง พร้อมดาวเทียมสื่อสารจริงอีก สอง ดวง สำเร็จลุล่วงตามแผน",
            "subtitle": "ไฮไลต์! ปล่อยดาวเทียม Starlink สำเร็จตามเป้า",
            "motion": "slow_zoom_in",
            "motion_speed": "slow",
            "motion_intensity": 0.08,
            "focus": "center",
            "transition": "fade"
            # NOTE: "wan" block omitted intentionally for hybrid mode (falls back to ffmpeg_motion to prevent satellite geometry distortion)
        },
        {
            "id": "scene-08-hypersonic-plasma-reentry",
            "image": "images/scene-08-hypersonic-plasma-reentry.png",
            "narration": "ก่อนที่ Starship จะกลับเข้าสู่ชั้นบรรยากาศ โดนความร้อนเสียดทานเผาไหม้จนเกิดพลาสมาสีม่วงอมชมพูห่อหุ้มลำยาน เป็นภาพที่น่าทึ่งมาก",
            "tts_text": "ก่อนที่ สตาร์ชิป จะกลับเข้าสู่ชั้นบรรยากาศ โดนความร้อนเสียดทานเผาไหม้จนเกิดพลาสมาสีม่วงอมชมพูห่อหุ้มลำยาน เป็นภาพที่น่าทึ่งมาก",
            "subtitle": "ฝ่าชั้นบรรยากาศโลก พลาสมาสีม่วงอมชมพูห่อหุ้มลำยาน",
            "motion": "slow_zoom_in",
            "motion_speed": "slow",
            "motion_intensity": 0.10,
            "focus": "center",
            "transition": "dissolve",
            "wan": {
                "prompt": "Cinematic atmospheric re-entry of Starship belly-flopping through the upper stratosphere at hypersonic speed, glowing magenta and violet ionization plasma sheath streaming along the heat shield tiles, sunset cloud sea below, no text.",
                "negative_prompt": "text, watermark, logo, cartoon, blurry, distortion, flicker, jitter",
                "seed": 808,
                "frames": 81,
                "steps": 22,
                "lip_sync": False
            }
        },
        {
            "id": "scene-09-moon-mars-refueling-future",
            "image": "images/scene-09-moon-mars-refueling-future.png",
            "narration": "Starship V3 คือก้าวสำคัญที่จะทำให้การเดินทางไปดวงจันทร์และดาวอังคารเป็นจริง ด้วยขีดความสามารถในการเติมเชื้อเพลิงในอวกาศ",
            "tts_text": "สตาร์ชิป วีทรี คือก้าวสำคัญที่จะทำให้การเดินทางไปดวงจันทร์และดาวอังคารเป็นจริง ด้วยขีดความสามารถในการเติมเชื้อเพลิงในอวกาศ",
            "subtitle": "Starship V3 ก้าวสำคัญสู่อนาคต ดั่งดวงจันทร์และดาวอังคาร",
            "motion": "pan_left_to_right",
            "motion_speed": "slow",
            "motion_intensity": 0.10,
            "focus": "center",
            "transition": "dissolve",
            "wan": {
                "prompt": "Majestic cinematic vision of Starship spacecraft in deep interplanetary transit, glowing red planet Mars dominating the right of frame with visible canyons and thin blue atmospheric haze, dark void of space, no text.",
                "negative_prompt": "text, watermark, logo, cartoon, blurry, distortion, flicker, jitter",
                "seed": 809,
                "frames": 81,
                "steps": 22,
                "lip_sync": False
            }
        },
        {
            "id": "scene-10-mamase-outro",
            "image": "images/scene-10-mamase-outro.png",
            "narration": "ทุกความล้มเหลวคือบันไดสู่ความสำเร็จ ติดตามความก้าวหน้าของอวกาศไปกับเรา กดไลก์ กดติดตาม มามาเซะ ไว้ได้เลยครับ!",
            "tts_text": "ทุกความล้มเหลวคือบันไดสู่ความสำเร็จ ติดตามความก้าวหน้าของอวกาศไปกับเรา กดไลก์ กดติดตาม มามาเซะ ไว้ได้เลยครับ!",
            "subtitle": "กดไลก์ กดติดตาม Mamase จักรวาลของใจ ไว้นะครับ!",
            "motion": "slow_zoom_in",
            "motion_speed": "slow",
            "motion_intensity": 0.06,
            "focus": "center",
            "transition": "fade",
            "wan": {
                "prompt": "Canonical Mamase outro branding, elegant neon cyan orbital ring circling glowing blue planet silhouette with central bright stellar flare, Mamase English and Thai typography shimmering in deep starry space.",
                "negative_prompt": "blurry, flicker, jitter, distortion, extra text",
                "seed": 810,
                "frames": 81,
                "steps": 22,
                "lip_sync": False
            }
        }
    ]
}

with open(DIST_DIR / "script.json", "w", encoding="utf-8") as f:
    json.dump(script_data, f, ensure_ascii=False, indent=2)

with open(ASSET_DIR / "script.json", "w", encoding="utf-8") as f:
    json.dump(script_data, f, ensure_ascii=False, indent=2)

# 4. Write visual-reference.md
visual_ref = """# SpaceX Starship V3 & Flight 12 Reel Visual Reference

## Topic
SpaceX เปิดตัว Starship V3 และบิน Flight 12 (10 scenes, 60-70s target duration)

## Benchmark Quality Alignment
- Modeled after Parker Solar Probe & Tianwen-2 cinematic visual benchmarks.
- Strictly 1080x1920 24-bit PNG for all 10 scenes.
- Clean master art: Scene 02-09 have zero labels, diagrams, English text, logo, watermark, HUD, or baked subtitles.
- Scene 01 features canonical Mamase presenter character cutout with natural drop shadow, rim lighting, and Thai typography.
- Scene 10 uses canonical Mamase branding outro.
- Subtitle safe zones: Lower 450px softly darkened across all narration scenes.
- Dual-mode Hybrid Wan: Scenes 01-06, 08-10 configured with Wan 2.2 prompts (steps 25 on Scene 01, steps 22 on others); Scene 07 omits Wan block to fall back to ffmpeg_motion to keep satellite geometry pristine.
"""

with open(ASSET_DIR / "visual-reference.md", "w", encoding="utf-8") as f:
    f.write(visual_ref)

print("Created script.json and video-metadata.json in dist/ and assets/")

# 5. Create ZIP package
zip_path = Path("dist/mamase-starship-v3-flight-12-reel-v1.zip")
if zip_path.exists():
    zip_path.unlink()

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    # Root level files
    zf.write(DIST_DIR / "script.json", arcname="script.json")
    zf.write(DIST_DIR / "video-metadata.json", arcname="video-metadata.json")
    # Images in images/
    for sc in scenes:
        zf.write(DIST_IMAGES / sc, arcname=f"images/{sc}")

print(f"Created ZIP archive: {zip_path} ({zip_path.stat().st_size:,} bytes)")
