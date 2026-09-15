# Jupiter as a Star Reel — Asset Manifest & Visual Audit

- **Project ID**: `mamase-jupiter-as-a-star-reel-v1`
- **Topic**: ถ้าดาวพฤหัสกลายเป็นดาวฤกษ์ — โลกจะมีดวงอาทิตย์สองดวงไหม? (Jupiter as a Star)
- **Target Runtime**: ~53 วินาที (45–60 วินาทีตามข้อกำหนด)
- **Scenes Count**: 8 ซีน (7 ซีนเนื้อหา + 1 ซีน Mamase Locked Outro)
- **Format**: 9:16 Vertical (`1080x1920`, 30 FPS)
- **Voice Profile**: Google Gemini TTS `Fenrir` (speed=1.0)
- **Renderer Compatibility**: Single ZIP รองรับทั้ง FFmpeg Motion (Default) และ Wan 2.2 Image-to-Video

---

## 1. ผลการตรวจรับรองคุณภาพงานภาพ (Visual Quality QA)
- **Hero Dominance**: ซีน 1 (Master Cover) และซีน 2, 4, 5, 7 มีวัตถุดาวเคราะห์/ดาวฤกษ์เป็นพระเอกครองพื้นที่ 60–70% ของเฟรมอย่างโดดเด่น
- **Human + Dog Anchor**: ซีน 1 นั่งชมความมหัศจรรย์บนชะง่อนผายอดเขา (Mountain Summit Overlook) ท่ามกลางทะเลหมอกและแสงไฟเมืองยามสนธยา ปราศจากขอบหลุมอุกกาบาตเดิม
- **Cinematic Lighting & Depth**: ทุกภาพไร้กรอบดำตัดทอน (Zero Black Edge Box), มิติ 3 เลเยอร์ (Foreground / Midground / Deep Space Starfield)
- **Official Branding**: ซีน 01 วางโลโก้ Mamase Podcast และวงกลมแท้จาก `assets/branding/mamase/logo.png`, ซีน 02–07 ใส่ Mamase Round Corner Logo ขวาบน, และซีน 08 ใช้ Locked Branded Outro ขนาด `1080x1920` เต็มบาน
- **No Text Artifacts**: ซีน 02–07 ไม่มีตัวอักษรภาษาอังกฤษ ขอบตัด หรือลายน้ำปลอมใดๆ

---

## 2. รายการไฟล์ภาพในแพ็กเกจ (`images/`)

| ซีนที่ | ชื่อไฟล์ | ความละเอียด | คำอธิบายภาพ |
| :---: | :--- | :---: | :--- |
| **01** | `scene-01-hook.png` | 1080×1920 | Master Key Art Cover บนยอดเขา ดาวพฤหัสฯ ยักษ์เปล่งประกายไฟดาวฤกษ์ พร้อมชายหนุ่มและสุนัขคู่ใจ |
| **02** | `scene-02-chemical-composition.png` | 1080×1920 | ดาวพฤหัสบดี Hubble 4K หมุนวนอวดพายุแถบก๊าซและจุดแดงใหญ่ Great Red Spot บนพื้นดาวฤกษ์ลึก |
| **03** | `scene-03-mass-reality-check.png` | 1080×1920 | ฟองสุริยะ Heliosphere ดวงอาทิตย์มหึมาสีทองอร่ามเทียบกับจุดวงโคจรดาวเคราะห์ในระบบสุริยะ |
| **04** | `scene-04-brown-dwarf-threshold.png` | 1080×1920 | ดาวแคระน้ำตาล Brown Dwarf เรืองแสงอินฟราเรดสีม่วงแดงเข้มจากข้อมูล NASA Spitzer |
| **05** | `scene-05-true-star-limit.png` | 1080×1920 | ดาวแคระแดง Red Dwarf ปะทุเปลวสุริยะ Solar Flare และพวยพลาสมาส้มทองอลังการ |
| **06** | `scene-06-earth-orbit-chaos.png` | 1080×1920 | โครงข่ายกาล-อวกาศ 3D และลำแสงแรงโน้มถ่วงที่บิดเบี้ยววงโคจรดาวเคราะห์อย่างรุนแรง |
| **07** | `scene-07-guardian-shield-payoff.png` | 1080×1920 | ดาวพฤหัสบดีทำหน้าที่เกราะพิทักษ์แรงโน้มถ่วง ดึงดูดและเบี่ยงวิถีฝูงดาวหาง/ดาวเคราะห์น้อย |
| **08** | `scene-08-brand-outro.png` | 1080×1920 | Mamase Locked Outro Master ขยายสัดส่วนเป็น `1080x1920` พร้อม CTA ทางการ |

---

## 3. สถานะไฟล์แพ็กเกจ ZIP
- **ที่อยู่ไฟล์**: `dist/mamase-jupiter-as-a-star-reel-v1.zip`
- **ขนาดไฟล์**: 23.77 MB
- **ผลการทดสอบ PackageService**: 100% Validated (สคริปต์ถูกต้องตาม Schema, ภาพครบทุกซีน, พร้อมเรนเดอร์ทันที)
