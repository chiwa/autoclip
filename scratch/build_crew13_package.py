import json
import os
import shutil
import zipfile
from pathlib import Path
from PIL import Image

ASSETS_DIR = Path("assets/crew13_oxidizer_leak_reel")
STAGING_DIR = Path("dist/mamase-crew13-oxidizer-leak-reel-v1")
ZIP_PATH = Path("dist/mamase-crew13-oxidizer-leak-reel-v1.zip")
MANIFEST_PATH = Path("docs/crew13-oxidizer-leak-reel-asset-manifest.md")

ASSETS_DIR.mkdir(parents=True, exist_ok=True)
STAGING_DIR.mkdir(parents=True, exist_ok=True)
images_staging = STAGING_DIR / "images"
images_staging.mkdir(parents=True, exist_ok=True)

scene_files = [
    "scene-01-hook.png",
    "scene-02-crew-13-scrub.png",
    "scene-03-what-is-oxidizer.png",
    "scene-04-hypergolic-ignition.png",
    "scene-05-leak-consequences.png",
    "scene-06-astronaut-safety.png",
    "scene-07-cleanroom-inspection.png",
    "scene-08-philosophical-climax.png",
    "scene-09-mamase-outro.png",
]

print("1. Copying durable master assets...")
for fname in scene_files:
    src = Path("scratch/crew13_preview") / fname
    dst_asset = ASSETS_DIR / fname
    dst_staging = images_staging / fname
    shutil.copy2(src, dst_asset)
    shutil.copy2(src, dst_staging)
    im = Image.open(dst_staging)
    print(f"  [OK] {fname}: {im.size} {im.mode} ({dst_staging.stat().st_size:,} bytes)")

print("\n2. Writing script.json...")
script_data = {
  "project": {
    "id": "mamase-crew13-oxidizer-leak-reel-v1",
    "title": "ทำไมแค่รอยรั่วเล็กๆ ถึงสั่งหยุดภารกิจอวกาศหมื่นล้าน? (SpaceX Crew-13)",
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
      "narration": "สวัสดีครับ ยินดีต้อนรับสู่ Mamase จักรวาลของใจ รู้ไหมครับว่า แค่รอยรั่วของเหลวเล็กๆ เพียงไม่กี่หยด ทำไมถึงสั่งหยุดภารกิจอวกาศมูลค่าหมื่นล้านอย่าง Crew-13 ได้ทันที?",
      "tts_text": "สวัสดีครับ ยินดีต้อนรับสู่ มามาเซ่ จักรวาลของใจ รู้ไหมครับว่า แค่รอยรั่วของเหลวเล็กๆ เพียงไม่กี่หยด ทำไมถึงสั่งหยุดภารกิจอวกาศมูลค่าหมื่นล้านอย่าง ครูว์ สิบสาม ได้ทันที?",
      "subtitle": "แค่รอยรั่วเล็กๆ สั่งหยุดภารกิจหมื่นล้าน?",
      "motion": "slow_zoom_in",
      "motion_speed": "slow",
      "motion_intensity": 0.1,
      "focus": "right",
      "transition": "dissolve",
      "wan": {
        "prompt": "Use the canonical Mamase anime presenter identity, friendly Thai male with tousled black hair, thin rectangular glasses and navy blazer, face-forward on the right for a talking shot. SpaceX Falcon 9 rocket and Crew Dragon spacecraft standing tall at Launch Complex 39A under brilliant night xenon floodlights, white propellant vapor venting, typography in upper left. Subtle natural head movement and gentle pointing gesture, stable composition.",
        "negative_prompt": "extra person, extra text, watermark, logo, distorted face, distorted hands, duplicated fingers, blurry spacecraft, flicker, jitter, sudden camera movement",
        "seed": 911,
        "frames": 81,
        "steps": 25,
        "lip_sync": True,
        "character_id": "mamase-presenter-v1"
      }
    },
    {
      "id": "scene-02-crew-13-scrub",
      "image": "images/scene-02-crew-13-scrub.png",
      "narration": "NASA และ SpaceX เพิ่งประกาศเลื่อนการปล่อยยาน Crew-13 สู่สถานีอวกาศนานาชาติ เพราะตรวจพบรอยรั่วของสารออกซิไดเซอร์ ในระบบขับเคลื่อนของยาน Dragon",
      "tts_text": "นาซา และ สเปซเอกซ์ เพิ่งประกาศเลื่อนการปล่อยยาน ครูว์ สิบสาม สู่สถานีอวกาศนานาชาติ เพราะตรวจพบรอยรั่วของสาร ออกซิไดเซอร์ ในระบบขับเคลื่อนของยาน ดรากอน",
      "subtitle": "ตรวจพบรอยรั่ว เลื่อนปล่อย Crew-13",
      "motion": "pan_up",
      "motion_speed": "slow",
      "motion_intensity": 0.15,
      "focus": "center",
      "transition": "fade",
      "wan": {
        "prompt": "Cinematic aerospace documentary view of Falcon 9 rocket and Crew Dragon spacecraft on launch pad 39A during dramatic sunset twilight, crew access arm extended, high-contrast silhouette against golden sky, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, explosion, flicker, jitter",
        "seed": 912,
        "frames": 81,
        "lip_sync": False
      }
    },
    {
      "id": "scene-03-what-is-oxidizer",
      "image": "images/scene-03-what-is-oxidizer.png",
      "narration": "ในความว่างเปล่าของอวกาศไม่มีอากาศให้หายใจ ยานจึงต้องพกสารช่วยเผาไหม้ หรือ ออกซิไดเซอร์ ไปด้วย ซึ่งในยาน Dragon สารนี้คือ ไดไนโตรเจน เตทรอกไซด์ ที่ทั้งกัดกร่อนและอันตรายสุดขั้ว",
      "tts_text": "ในความว่างเปล่าของอวกาศไม่มีอากาศให้หายใจ ยานจึงต้องพกสารช่วยเผาไหม้ หรือ ออกซิไดเซอร์ ไปด้วย ซึ่งในยาน ดรากอน สารนี้คือ ไดไนโตรเจน เตทรอกไซด์ ที่ทั้งกัดกร่อนและอันตรายสุดขั้ว",
      "subtitle": "สารช่วยเผาไหม้ในอวกาศ: ออกซิไดเซอร์",
      "motion": "slow_zoom_in",
      "motion_speed": "slow",
      "motion_intensity": 0.12,
      "focus": "center",
      "transition": "dissolve",
      "wan": {
        "prompt": "Macro engineering aerospace documentary view of titanium hypergolic propellant tanks, high-pressure tubing, and precision thruster manifold valves inside spacecraft cleanroom assembly, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, damage, flicker, jitter",
        "seed": 913,
        "frames": 81,
        "lip_sync": False
      }
    },
    {
      "id": "scene-04-hypergolic-ignition",
      "image": "images/scene-04-hypergolic-ignition.png",
      "narration": "แต่เดี๋ยวก่อน... ระบบนี้พิเศษกว่ารถยนต์ทั่วไปครับ เพราะเป็นเชื้อเพลิงแบบ ไฮเปอร์กอลิก ที่เพียงแค่สารสองตัวสัมผัสกันปุ๊บ มันจะจุดระเบิดติดไฟทันทีโดยไม่ต้องใช้หัวเทียน!",
      "tts_text": "แต่เดี๋ยวก่อน... ระบบนี้พิเศษกว่ารถยนต์ทั่วไปครับ เพราะเป็นเชื้อเพลิงแบบ ไฮเปอร์กอลิก ที่เพียงแค่สารสองตัวสัมผัสกันปุ๊บ มันจะจุดระเบิดติดไฟทันทีโดยไม่ต้องใช้หัวเทียน!",
      "subtitle": "เชื้อเพลิงไฮเปอร์กอลิก สัมผัสปุ๊บ ติดไฟทันที!",
      "motion": "slow_zoom_out",
      "motion_speed": "slow",
      "motion_intensity": 0.12,
      "focus": "center",
      "transition": "fade",
      "wan": {
        "prompt": "Cinematic slow motion footage of rocket engine hot-fire test, glowing incandescent supersonic rocket exhaust jet firing downwards into flame trench, shimmering thermal heat waves, raw kinetic energy, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, flicker, jitter",
        "seed": 914,
        "frames": 81,
        "lip_sync": False
      }
    },
    {
      "id": "scene-05-leak-consequences",
      "image": "images/scene-05-leak-consequences.png",
      "narration": "ถ้ารอยรั่วนี้ทำให้สารออกซิไดเซอร์ซึมไปโดนท่อเชื้อเพลิง หรือกัดกร่อนวาล์วควบคุม เครื่องยนต์อาจเกิดการจุดระเบิดผิดจังหวะ หรือระเบิดรุนแรงจนยานควบคุมไม่ได้กลางอวกาศ",
      "tts_text": "ถ้ารอยรั่วนี้ทำให้สารออกซิไดเซอร์ซึมไปโดนท่อเชื้อเพลิง หรือกัดกร่อนวาล์วควบคุม เครื่องยนต์อาจเกิดการจุดระเบิดผิดจังหวะ หรือระเบิดรุนแรงจนยานควบคุมไม่ได้กลางอวกาศ",
      "subtitle": "รั่วเพียงนิด เสี่ยงระเบิดรุนแรง",
      "motion": "pan_up",
      "motion_speed": "slow",
      "motion_intensity": 0.14,
      "focus": "center",
      "transition": "fade",
      "wan": {
        "prompt": "Cinematic aerospace documentary of powerful rocket liftoff, colossal pillar of fire and billowing clouds of smoke erupting from the launch mount, intense thrust shaking the air, raw aerospace power, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, flicker, jitter",
        "seed": 915,
        "frames": 81,
        "lip_sync": False
      }
    },
    {
      "id": "scene-06-astronaut-safety",
      "image": "images/scene-06-astronaut-safety.png",
      "narration": "ถ้าเป็นยานขนส่งสัมภาระ ความเสี่ยงนี้อาจยอมรับได้... แต่นี่คือภารกิจที่มีมนุษย์อวกาศสี่ชีวิตนั่งอยู่ข้างใน กฎเหล็กของอวกาศคือ ความปลอดภัยต้องหนึ่งร้อยเปอร์เซ็นต์เต็ม",
      "tts_text": "ถ้าเป็นยานขนส่งสัมภาระ ความเสี่ยงนี้อาจยอมรับได้... แต่นี่คือภารกิจที่มีมนุษย์อวกาศสี่ชีวิตนั่งอยู่ข้างใน กฎเหล็กของอวกาศคือ ความปลอดภัยต้องหนึ่งร้อยเปอร์เซ็นต์เต็ม",
      "subtitle": "กฎเหล็กอวกาศ: ความปลอดภัยต้อง 100%",
      "motion": "slow_zoom_in",
      "motion_speed": "slow",
      "motion_intensity": 0.12,
      "focus": "center",
      "transition": "fade",
      "wan": {
        "prompt": "Cinematic documentary close-up of an astronaut resting inside custom contoured spacecraft seat, wearing white advanced commercial spacesuit and pressurized flight helmet, quiet focus, solemn human determination, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, distortion, flicker, jitter",
        "seed": 916,
        "frames": 81,
        "lip_sync": False
      }
    },
    {
      "id": "scene-07-cleanroom-inspection",
      "image": "images/scene-07-cleanroom-inspection.png",
      "narration": "ทีมวิศวกรจึงตัดสินใจถอดชิ้นส่วนวาล์วออกมาตรวจสอบอย่างละเอียดในห้องปลอดเชื้อ เพื่อเปลี่ยนซีลใหม่ทั้งหมด และเลื่อนกำหนดการปล่อยไปเป็นปลายเดือนกันยายน",
      "tts_text": "ทีมวิศวกรจึงตัดสินใจถอดชิ้นส่วนวาล์วออกมาตรวจสอบอย่างละเอียดในห้องปลอดเชื้อ เพื่อเปลี่ยนซีลใหม่ทั้งหมด และเลื่อนกำหนดการปล่อยไปเป็นปลายเดือนกันยายน",
      "subtitle": "ถอดตรวจเช็กในคลีนรูม เปลี่ยนซีลใหม่ทั้งหมด",
      "motion": "documentary_pan",
      "motion_speed": "slow",
      "motion_intensity": 0.12,
      "focus": "center",
      "transition": "dissolve",
      "wan": {
        "prompt": "High-tech aerospace cleanroom inspection, technicians in clean white bunny suits meticulously examining spacecraft propulsion valves and wiring harnesses on multi-level scaffolding, bright clinical illumination, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, flicker, jitter",
        "seed": 917,
        "frames": 81,
        "lip_sync": False
      }
    },
    {
      "id": "scene-08-philosophical-climax",
      "image": "images/scene-08-philosophical-climax.png",
      "narration": "เพราะในการสำรวจจักรวาล ความกล้าหาญที่จะหยุดและแก้ไข สำคัญไม่แพ้ความกล้าหาญที่จะพุ่งทะยาน... เพราะชีวิตมนุษย์ มีค่ายิ่งกว่ากำหนดการปล่อยใดๆ ในโลก",
      "tts_text": "เพราะในการสำรวจจักรวาล ความกล้าหาญที่จะหยุดและแก้ไข สำคัญไม่แพ้ความกล้าหาญที่จะพุ่งทะยาน... เพราะชีวิตมนุษย์ มีค่ายิ่งกว่ากำหนดการปล่อยใดๆ ในโลก",
      "subtitle": "ความกล้าที่จะหยุด มีค่ายิ่งกว่ากำหนดการปล่อย",
      "motion": "slow_zoom_in",
      "motion_speed": "slow",
      "motion_intensity": 0.12,
      "focus": "center",
      "transition": "none",
      "wan": {
        "prompt": "Majestic cinematic shot of Crew Dragon spacecraft soaring gracefully in low Earth orbit high above illuminated city lights and atmospheric blue limb of Earth, peaceful cosmos with distant stars, awe-inspiring human exploration, no text.",
        "negative_prompt": "text, subtitle, watermark, logo, cartoon, flicker, jitter",
        "seed": 918,
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
  "title": "ทำไมแค่รอยรั่วเล็กๆ ถึงสั่งหยุดภารกิจอวกาศหมื่นล้าน? (SpaceX Crew-13)",
  "description": "เจาะลึกเบื้องหลังที่ NASA และ SpaceX สั่งเลื่อนการปล่อยยาน Crew-13 สู่สถานีอวกาศนานาชาติ (ISS) หลังตรวจพบรอยรั่วของสารออกซิไดเซอร์ (Dinitrogen Tetroxide) ในระบบขับเคลื่อนของยาน Dragon\n\nทำไมแค่รอยรั่วระดับไมครอนถึงต้องสั่งหยุดภารกิจมูลค่าหมื่นล้าน? ทำความรู้จักเชื้อเพลิงไฮเปอร์กอลิก (Hypergolic Propellant) ที่พร้อมระเบิดทันทีเมื่อสัมผัสกัน และทำไมในโลกวิศวกรรมอวกาศ ความกล้าหาญที่จะหยุดและตรวจสอบเพื่อปกป้องชีวิตมนุษย์อวกาศ จึงสำคัญยิ่งกว่ากำหนดการปล่อยใดๆ ในโลก\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#SpaceX #Crew13 #NASA #Dragon #อวกาศ #วิทยาศาสตร์ #ดาราศาสตร์ #สารคดี #วิศวกรรมอวกาศ #Mamase #จักรวาลของใจ"
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
