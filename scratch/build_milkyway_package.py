import json
import os
import shutil
import zipfile
from pathlib import Path
from PIL import Image
from app.services.package_service import PackageService

ASSETS_DIR = Path("assets/milky_way_names_reel")
STAGING_DIR = Path("dist/mamase-milky-way-names-reel-v1")
ZIP_PATH = Path("dist/mamase-milky-way-names-reel-v1.zip")
MANIFEST_PATH = Path("docs/milky-way-names-reel-asset-manifest.md")

ASSETS_DIR.mkdir(parents=True, exist_ok=True)
STAGING_DIR.mkdir(parents=True, exist_ok=True)
images_staging = STAGING_DIR / "images"
images_staging.mkdir(parents=True, exist_ok=True)

scene_files = [
    "scene-01-hook.png",
    "scene-02-thailand-white-elephant.png",
    "scene-03-west-milky-way.png",
    "scene-04-east-asia-silver-river.png",
    "scene-05-sweden-vintergatan.png",
    "scene-06-finland-birds-pathway.png",
    "scene-07-arabic-haymakers-way.png",
    "scene-08-milky-way-our-home.png",
    "scene-09-mamase-outro.png",
]

print("1. Copying durable master assets...")
for fname in scene_files:
    src = Path("scratch/milkyway_preview") / fname
    dst_asset = ASSETS_DIR / fname
    dst_staging = images_staging / fname
    shutil.copy2(src, dst_asset)
    shutil.copy2(src, dst_staging)
    im = Image.open(dst_staging)
    print(f"  [OK] {fname}: {im.size} {im.mode} ({dst_staging.stat().st_size:,} bytes)")

print("\n2. Writing script.json...")
script_data = {
  "project": {
    "id": "mamase-milky-way-names-reel-v1",
    "title": "แต่ละประเทศเรียก \"ทางช้างเผือก\" ว่าอะไรบ้าง? ความลับบนผืนฟ้าที่น่าทึ่ง",
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
      "narration": "สวัสดีครับ ยินดีต้อนรับสู่ Mamase จักรวาลของใจ รู้ไหมครับว่า ทางช้างเผือก แถบดาวสีขาวพาดผ่านฟ้ายามค่ำคืน แต่ละประเทศทั่วโลก... มีชื่อเรียกและตำนานที่ไม่เหมือนกันเลย?",
      "tts_text": "สวัสดีครับ ยินดีต้อนรับสู่ มามาเซ่ จักรวาลของใจ รู้ไหมครับว่า ทางช้างเผือก แถบดาวสีขาวพาดผ่านฟ้ายามค่ำคืน แต่ละประเทศทั่วโลก... มีชื่อเรียกและตำนานที่ไม่เหมือนกันเลย?",
      "subtitle": "แต่ละประเทศเรียกทางช้างเผือกว่าอะไร?",
      "motion": "slow_zoom_in",
      "motion_speed": "slow",
      "motion_intensity": 0.1,
      "focus": "right",
      "transition": "dissolve",
      "wan": {
        "prompt": "Use the canonical Mamase anime presenter identity, friendly Thai male with tousled black hair, thin rectangular glasses and navy blazer, face-forward on the right for a talking shot. Majestic glowing Milky Way galactic core rising over astronomical observatory domes under dark night sky, Thai typography in upper left. Subtle natural head movement and gentle hand gesture, stable composition.",
        "negative_prompt": "extra person, extra text, watermark, logo, distorted face, distorted hands, duplicated fingers, blurry stars, flicker, jitter, sudden camera movement",
        "seed": 801,
        "frames": 81,
        "steps": 25,
        "lip_sync": True,
        "character_id": "mamase-presenter-v1"
      }
    },
    {
      "id": "scene-02-thailand-white-elephant",
      "image": "images/scene-02-thailand-white-elephant.png",
      "narration": "เริ่มที่เมืองไทย คนโบราณมองเห็นเป็น ทางช้างเผือก เส้นทางเดินอันศักดิ์สิทธิ์ของช้างทรงคู่บารมีพระราชา พาดผ่านสรวงสวรรค์",
      "tts_text": "เริ่มที่เมืองไทย คนโบราณมองเห็นเป็น ทางช้างเผือก เส้นทางเดินอันศักดิ์สิทธิ์ของช้างทรงคู่บารมีพระราชา พาดผ่านสรวงสวรรค์",
      "subtitle": "ไทย: ทางช้างเผือก\n(เส้นทางช้างเผือกศักดิ์สิทธิ์)",
      "motion": "pan_up",
      "motion_speed": "slow",
      "motion_intensity": 0.15,
      "focus": "center",
      "transition": "fade",
      "wan": {
        "prompt": "Cinematic documentary night view of Sukhothai ancient stone Buddha and historic temple pillars under radiant starry night sky, luminous Milky Way arching overhead, tranquil sacred atmosphere, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, distortion, flicker, jitter",
        "seed": 802,
        "frames": 81,
        "lip_sync": False
      }
    },
    {
      "id": "scene-03-west-milky-way",
      "image": "images/scene-03-west-milky-way.png",
      "narration": "แถบตะวันตก โรมันและกรีกโบราณเรียกว่า Via Lactea หรือ Milky Way แปลตรงตัวว่า ทางน้ำนม ตามตำนานน้ำนมของเทพีฮีราที่พุ่งกระจายเต็มท้องฟ้า",
      "tts_text": "แถบตะวันตก โรมันและกรีกโบราณเรียกว่า เวีย ลักเตีย หรือ มิลกี เวย์ แปลตรงตัวว่า ทางน้ำนม ตามตำนานน้ำนมของเทพีฮีราที่พุ่งกระจายเต็มท้องฟ้า",
      "subtitle": "ละติน/อังกฤษ: Via Lactea / Milky Way\n(ทางน้ำนม)",
      "motion": "slow_zoom_in",
      "motion_speed": "slow",
      "motion_intensity": 0.12,
      "focus": "center",
      "transition": "dissolve",
      "wan": {
        "prompt": "Cinematic historical documentary of classical marble Temple of Poseidon at Cape Sounion perched on sea cliff, bathed in warm amber illumination, Milky Way galactic core billowing behind ancient columns, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, distortion, flicker, jitter",
        "seed": 803,
        "frames": 81,
        "lip_sync": False
      }
    },
    {
      "id": "scene-04-east-asia-silver-river",
      "image": "images/scene-04-east-asia-silver-river.png",
      "narration": "ข้ามมาฝั่งเอเชียตะวันออก คนจีนเรียกว่า 銀河 หรือ หยินเหอ ส่วนญี่ปุ่นเรียกว่า 天の川 หรือ อามาโนะกาวะ ทั้งคู่แปลเหมือนกันว่า แม่น้ำสีเงิน หรือ แม่น้ำสวรรค์ ที่คั่นความรักของหนุ่มเลี้ยงวัวกับสาวทอผ้า",
      "tts_text": "ข้ามมาฝั่งเอเชียตะวันออก คนจีนเรียกว่า หยินเหอ ส่วนญี่ปุ่นเรียกว่า อามาโนะกาวะ ทั้งคู่แปลเหมือนกันว่า แม่น้ำสีเงิน หรือ แม่น้ำสวรรค์ ที่คั่นความรักของหนุ่มเลี้ยงวัวกับสาวทอผ้า",
      "subtitle": "จีน/ญี่ปุ่น: 銀河 (หยินเหอ) / 天の川 (อามาโนะกาวะ)\n(แม่น้ำสีเงิน / แม่น้ำสวรรค์)",
      "motion": "pan_up",
      "motion_speed": "slow",
      "motion_intensity": 0.14,
      "focus": "center",
      "transition": "fade",
      "wan": {
        "prompt": "Cinematic East Asian night landscape, tranquil lake mirroring a radiant river of silver stars stretching across the indigo heavens, silhouettes gazing upward in awe, poetic and romantic atmosphere, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, distortion, flicker, jitter",
        "seed": 804,
        "frames": 81,
        "lip_sync": False
      }
    },
    {
      "id": "scene-05-sweden-vintergatan",
      "image": "images/scene-05-sweden-vintergatan.png",
      "narration": "ในสวีเดน แถบสแกนดิเนเวีย จะเห็นทางช้างเผือกได้ชัดเฉพาะฤดูหนาวที่มืดมิด เขาจึงเรียกว่า Vintergatan หรือ วินเทอร์กาทัน แปลว่า ทางแห่งฤดูหนาว",
      "tts_text": "ในสวีเดน แถบสแกนดิเนเวีย จะเห็นทางช้างเผือกได้ชัดเฉพาะฤดูหนาวที่มืดมิด เขาจึงเรียกว่า วินเทอร์กาทัน แปลว่า ทางแห่งฤดูหนาว",
      "subtitle": "สวีเดน: Vintergatan (วินเทอร์กาทัน)\n(ทางแห่งฤดูหนาว)",
      "motion": "slow_zoom_in",
      "motion_speed": "slow",
      "motion_intensity": 0.12,
      "focus": "center",
      "transition": "dissolve",
      "wan": {
        "prompt": "Cinematic documentary of sharp snow-covered alpine mountain peaks under crystalline frosty winter night sky, winter Milky Way arch glowing with sharp icy brilliance, quiet Scandinavian winter wilderness, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, distortion, flicker, jitter",
        "seed": 805,
        "frames": 81,
        "lip_sync": False
      }
    },
    {
      "id": "scene-06-finland-birds-pathway",
      "image": "images/scene-06-finland-birds-pathway.png",
      "narration": "ส่วนเพื่อนบ้านอย่างฟินแลนด์ เรียกว่า Linnunrata หรือ ลินนุนราตา แปลว่า เส้นทางของนก เพราะเชื่อว่าฝูงนกอพยพจะบินตามแถบดาวนี้ มุ่งหน้าสู่ดินแดนอันอบอุ่นทางทิศใต้",
      "tts_text": "ส่วนเพื่อนบ้านอย่างฟินแลนด์ เรียกว่า ลินนุนราตา แปลว่า เส้นทางของนก เพราะเชื่อว่าฝูงนกอพยพจะบินตามแถบดาวนี้ มุ่งหน้าสู่ดินแดนอันอบอุ่นทางทิศใต้",
      "subtitle": "ฟินแลนด์: Linnunrata (ลินนุนราตา)\n(เส้นทางของนกอพยพ)",
      "motion": "pan_up",
      "motion_speed": "slow",
      "motion_intensity": 0.15,
      "focus": "center",
      "transition": "fade",
      "wan": {
        "prompt": "Cinematic northern boreal forest in deep winter, snow laden pine trees, flock of wild migrating birds in graceful silhouette flying upward along the glowing cosmic Milky Way band towards the south, mystical Nordic folklore, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, distortion, flicker, jitter",
        "seed": 806,
        "frames": 81,
        "lip_sync": False
      }
    },
    {
      "id": "scene-07-arabic-haymakers-way",
      "image": "images/scene-07-arabic-haymakers-way.png",
      "narration": "ในภาษาอาหรับเรียกว่า Darb al-Tabbāna หรือ ดาร์บ อัล ตับบานะฮ์ แปลว่า ทางของคนขนฟาง เปรียบเศษฟางข้าวที่ร่วงหล่นจากเกวียน กลายเป็นละอองดาวสีทองกลางทะเลทราย",
      "tts_text": "ในภาษาอาหรับเรียกว่า ดาร์บ อัล ตับบานะฮ์ แปลว่า ทางของคนขนฟาง เปรียบเศษฟางข้าวที่ร่วงหล่นจากเกวียน กลายเป็นละอองดาวสีทองกลางทะเลทราย",
      "subtitle": "อาหรับ: درب التبانة (ดาร์บ อัล ตับบานะฮ์)\n(ทางของคนขนฟาง)",
      "motion": "slow_zoom_in",
      "motion_speed": "slow",
      "motion_intensity": 0.12,
      "focus": "center",
      "transition": "fade",
      "wan": {
        "prompt": "Cinematic desert nightscape, vast sweeping golden sand dunes beneath a magnificent arching Milky Way galaxy, warm golden stellar dust lanes billowing across the sky like dropped straw in the desert night, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, distortion, flicker, jitter",
        "seed": 807,
        "frames": 81,
        "lip_sync": False
      }
    },
    {
      "id": "scene-08-milky-way-our-home",
      "image": "images/scene-08-milky-way-our-home.png",
      "narration": "ไม่ว่าจะถูกเรียกว่าอะไร... แท้จริงแล้ว แถบดาวนี้คือกาแล็กซีก้นหอยขนาดมหึมา ที่มีดวงดาวกว่าสี่แสนล้านดวง และเป็นบ้านร่วมกันของมนุษยชาติทุกคนในเอกภพ",
      "tts_text": "ไม่ว่าจะถูกเรียกว่าอะไร... แท้จริงแล้ว แถบดาวนี้คือกาแล็กซีก้นหอยขนาดมหึมา ที่มีดวงดาวกว่าสี่แสนล้านดวง และเป็นบ้านร่วมกันของมนุษยชาติทุกคนในเอกภพ",
      "subtitle": "บ้านร่วมกันของมนุษยชาติ: กาแล็กซีทางช้างเผือก",
      "motion": "slow_zoom_in",
      "motion_speed": "slow",
      "motion_intensity": 0.12,
      "focus": "center",
      "transition": "none",
      "wan": {
        "prompt": "Majestic Hubble Space Telescope view of a grand barred spiral galaxy resembling our Milky Way, bright luminous galactic core, sweeping pinwheel spiral arms glowing with blue star clusters and pink interstellar nebulae, infinite cosmic wonder, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, distortion, flicker, jitter",
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
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, extra planet, extra stars, flicker, jitter",
        "seed": 98,
        "frames": 81,
        "lip_sync": False
      }
    }
  ]
}

script_path = STAGING_DIR / "script.json"
with open(script_path, "w", encoding="utf-8") as f:
    json.dump(script_data, f, ensure_ascii=False, indent=2)
print(f"  [OK] Saved {script_path}")

print("\n3. Writing video-metadata.json...")
metadata_data = {
  "title": "แต่ละประเทศเรียก \"ทางช้างเผือก\" ว่าอะไรบ้าง? ความลับบนผืนฟ้าที่น่าทึ่ง",
  "description": "เคยสงสัยไหมครับว่า แถบแสงสีขาวพราวระยับที่พาดผ่านฟ้ายามค่ำคืน แต่ละประเทศทั่วโลกเขาเรียกมันว่าอะไร?\n\nตั้งแต่ \"ทางช้างเผือก\" ของไทย สู่ \"Via Lactea / Milky Way\" (ทางน้ำนม) ของชาวโรมันและกรีก, \"銀河 / 天の川\" (แม่น้ำสีเงิน) ในตำนานหนุ่มเลี้ยงวัวกับสาวทอผ้าของจีนและญี่ปุ่น, \"Vintergatan\" (ทางฤดูหนาว) ของสวีเดน, \"Linnunrata\" (เส้นทางของนก) ของฟินแลนด์ ไปจนถึง \"Darb al-Tabbāna\" (ทางของคนขนฟาง) ในภาษาอาหรับ!\n\nและในทางดาราศาสตร์ยุคใหม่... แถบดาวนี้แท้จริงแล้วคืออะไรกันแน่? ร่วมค้นหาคำตอบในคลิปนี้ครับ\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#ทางช้างเผือก #MilkyWay #ดาราศาสตร์ #จักรวาล #อวกาศ #สารคดี #ภาษาศาสตร์ #ตำนาน #วิทยาศาสตร์ #Mamase #จักรวาลของใจ"
}

meta_path = STAGING_DIR / "video-metadata.json"
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(metadata_data, f, ensure_ascii=False, indent=2)
print(f"  [OK] Saved {meta_path}")

print("\n4. Building release ZIP package...")
if ZIP_PATH.exists():
    ZIP_PATH.unlink()

with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
    for item in sorted(STAGING_DIR.rglob("*")):
        if item.is_file():
            arcname = item.relative_to(STAGING_DIR).as_posix()
            z.write(item, arcname=arcname)
            print(f"  + {arcname}")

print(f"\n[SUCCESS] Built {ZIP_PATH} ({ZIP_PATH.stat().st_size:,} bytes)")

print("\n5. Validating package with PackageService...")
val_dir = Path("scratch/val_milkyway")
if val_dir.exists():
    shutil.rmtree(val_dir)
val_dir.mkdir(parents=True, exist_ok=True)

svc = PackageService(50_000_000)
script, bgm = svc.extract_and_validate(ZIP_PATH, val_dir)
print(f"PackageService validation passed! Validated project: {script.project.id}")
print(f"Total scenes validated: {len(script.scenes)}")
