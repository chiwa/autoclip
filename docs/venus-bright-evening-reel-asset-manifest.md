# Mamase Reel Asset Manifest: ดาวสว่างลึกลับหัวค่ำทางทิศตะวันตก — ดาวศุกร์ & 2 ปรากฏการณ์สำคัญกันยายน

This document describes the visual assets, camera motions, transitions, narration, and technical specifications for the Mamase vertical short-form video package (`mamase-venus-bright-evening-reel-v1.zip`).

---

## 📦 Package Overview

- **Archive**: `dist/mamase-venus-bright-evening-reel-v1.zip`
- **Asset Directory**: `assets/venus_bright_evening_reel/`
- **Resolution**: 1080×1920 (9:16 vertical)
- **Framerate**: 30 FPS
- **Voice Provider**: Google Gemini `Fenrir` (`speed: 1.0`, full phonetic Thai script)
- **Scenes Count**: 9 scenes (~58–63 seconds total)
- **Branding Standard**:
  - Scenes 01–08: Actual Mamase circular logo (`205×205px`) composited at top-right `(x: 839, y: 36)` with soft drop shadow.
  - Scene 09: Locked Mamase Canonical Outro (`reels-end-scene.png`) without duplicate logo, subtitles, or Wan overlay.

---

## 🎬 Scene Breakdown

### Scene 01 — Hook
- **File**: `images/scene-01-hook.png`
- **Motion**: `cinematic_push_in` (Intensity: `0.12`, Speed: `slow`)
- **Transition**: `dissolve`
- **Typography & Key Art**: Title "VENUS" in gold foil Chonburi font, "ดาวสว่างลึกลับหัวค่ำ?" in creamy white with dark outline, accompanied by Mamase presenter pointing toward the dazzling evening star over a scenic twilight city skyline.
- **Wan 2.2**: 81 frames, 25 steps, `lip_sync: true`, `character_id: "mamase-presenter-v1"`.
- **Narration**: ช่วงนี้ใครมองไปทางทิศตะวันตกตอนหัวค่ำ แล้วเห็นดาวดวงหนึ่งส่องสว่างจ้าผิดปกติ จนคิดว่าเป็น UFO จริง ๆ มันคืออะไรครับ?
- **TTS Text**: ช่วงนี้ใครมองไปทางทิศตะวันตกตอนหัวค่ำ แล้วเห็นดาวดวงหนึ่งส่องสว่างจ้าผิดปกติ จนคิดว่าเป็น ยูเอฟโอ จริง ๆ มันคืออะไรครับ?

### Scene 02 — The Evening Star (Venus)
- **File**: `images/scene-02-bright-star.png`
- **Motion**: `documentary_pan` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `smooth_left`
- **Visual**: Ultra-realistic documentary astrophotography of Venus shining like a diamond beacon in the evening twilight above silhouettes of tropical palm trees and tranquil shoreline.
- **Narration**: ดาวดวงนั้นไม่ใช่ UFO หรือโดรนครับ แต่คือ 'ดาวศุกร์' หรือดาวประจำเมือง ดาวเคราะห์เพื่อนบ้านที่ได้ชื่อว่าเป็นฝาแฝดของโลก
- **TTS Text**: ดาวดวงนั้นไม่ใช่ ยูเอฟโอ หรือโดรนครับ แต่คือ ดาวศุกร์ หรือดาวประจำเมือง ดาวเคราะห์เพื่อนบ้านที่ได้ชื่อว่าเป็นฝาแฝดของโลก

### Scene 03 — Thick Reflective Atmosphere (Albedo 70%)
- **File**: `images/scene-03-albedo-clouds.png`
- **Motion**: `slow_zoom_out` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Photorealistic space view of Venus showing dense swirling clouds of sulfuric acid, glowing as a luminous thick crescent reflecting intense sunlight toward Earth.
- **Narration**: สาเหตุที่ช่วงนี้มันสว่างตาแตก เป็นเพราะดาวศุกร์กำลังโคจรสะท้อนแสงอาทิตย์มายังโลกเต็มที่ ประกอบกับบรรยากาศเมฆกรดที่สะท้อนแสงได้ถึง 70% ครับ
- **TTS Text**: สาเหตุที่ช่วงนี้มันสว่างตาแตก เป็นเพราะดาวศุกร์กำลังโคจรสะท้อนแสงอาทิตย์มายังโลกเต็มที่ ประกอบกับบรรยากาศเมฆกรดที่สะท้อนแสงได้ถึงเจ็ดสิบเปอร์เซ็นต์ครับ

### Scene 04 — Greatest Brilliancy (September 22)
- **File**: `images/scene-04-peak-brilliancy.png`
- **Motion**: `cinematic_push_in` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade_black`
- **Visual**: Magnificent wide-angle twilight horizon mirroring Venus across a calm lake, with the core of the Milky Way arching across the deepening blue sky.
- **Narration**: และในวันที่ 22 กันยายนนี้ ดาวศุกร์จะเข้าสู่ช่วงที่สว่างที่สุดบนท้องฟ้าหัวค่ำ ปรากฏเด่นชัดตั้งแต่ดวงอาทิตย์ตกดินยาวไปจนถึงเกือบสองทุ่มครับ
- **TTS Text**: และในวันที่ยี่สิบสองกันยายนนี้ ดาวศุกร์จะเข้าสู่ช่วงที่สว่างที่สุดบนท้องฟ้าหัวค่ำ ปรากฏเด่นชัดตั้งแต่ดวงอาทิตย์ตกดินยาวไปจนถึงเกือบสองทุ่มครับ

### Scene 05 — Lunar Occultation of Venus (September 14)
- **File**: `images/scene-05-lunar-occultation.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Sharp telephoto capture of the delicate crescent Moon with earthshine, positioned right next to Venus moments before occultation.
- **Narration**: แต่ก่อนหน้านั้น วันที่ 14 กันยายน จะมีปรากฏการณ์หาดูยาก 'ดวงจันทร์บังดาวศุกร์' เริ่มตั้งแต่เวลา 19 นาฬิกา 28 นาที
- **TTS Text**: แต่ก่อนหน้านั้น วันที่สิบสี่กันยายน จะมีปรากฏการณ์หาดูยาก ดวงจันทร์บังดาวศุกร์ เริ่มตั้งแต่เวลาสิบเก้านาฬิกายี่สิบแปดนาที

### Scene 06 — Sinking Below the Horizon
- **File**: `images/scene-06-setting-horizon.png`
- **Motion**: `pan_down` (Intensity: `0.12`, Speed: `slow`)
- **Transition**: `smooth_right`
- **Visual**: Authentic ESO telephoto master of the slender crescent Moon touching the fiery crimson twilight horizon as Venus shines above in the dusky blue sky.
- **Narration**: สำหรับในไทย เรามีเวลาดูสั้นมากครับ เพราะหลังจากดวงจันทร์เริ่มบัง ดาวทั้งสองจะตกลับขอบฟ้าไปก่อนที่เราจะได้เห็นดาวศุกร์โผล่ออกมาอีกฝั่ง
- **TTS Text**: สำหรับในไทย เรามีเวลาดูสั้นมากครับ เพราะหลังจากดวงจันทร์เริ่มบัง ดาวทั้งสองจะตกลับขอบฟ้าไปก่อนที่เราจะได้เห็นดาวศุกร์โผล่ออกมาอีกฝั่ง

### Scene 07 — Stargazing & Unobstructed Viewpoint
- **File**: `images/scene-07-observatory-viewpoint.png`
- **Motion**: `gentle_float` (Intensity: `0.10`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Auxiliary telescopes at world-class observatory open toward the pristine, open golden sunset horizon, representing the ideal unobstructed vantage point.
- **Narration**: ใครอยากชม แนะนำให้หาจุดสังเกตการณ์ที่ฟ้าทิศตะวันตกโปร่งโล่ง ไม่มีตึกหรือภูเขาบัง เริ่มมองหาได้ทันทีที่แสงอาทิตย์ลับขอบฟ้าครับ
- **TTS Text**: ใครอยากชม แนะนำให้หาจุดสังเกตการณ์ที่ฟ้าทิศตะวันตกโปร่งโล่ง ไม่มีตึกหรือภูเขาบัง เริ่มมองหาได้ทันทีที่แสงอาทิตย์ลับขอบฟ้าครับ

### Scene 08 — Cosmic Twin Connection
- **File**: `images/scene-08-earth-venus-cosmic.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade`
- **Visual**: Breathtaking orbital view of Earth's sunrise rim in the foreground with twin sister planet Venus gleaming brightly in deep space.
- **Narration**: ท้องฟ้ามีเรื่องเล่าและจังหวะของมันเสมอ หัวค่ำนี้ ลองเงยหน้ามองทิศตะวันตก แล้วทักทายดาวเคราะห์เพื่อนบ้านดวงนี้ดูนะครับ
- **TTS Text**: ท้องฟ้ามีเรื่องเล่าและจังหวะของมันเสมอ หัวค่ำนี้ ลองเงยหน้ามองทิศตะวันตก แล้วทักทายดาวเคราะห์เพื่อนบ้านดวงนี้ดูนะครับ

### Scene 09 — Canonical Mamase Outro
- **File**: `images/scene-09-mamase-outro.png`
- **Source**: Rescaled 1080×1920 of `assets/branding/mamase/reels-end-scene.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.05`, Speed: `slow`)
- **Transition**: `none`
- **Subtitles**: Disabled (`show_subtitle: false`)
- **Wan**: None
- **Narration**: ถ้าชอบเรื่องราวอวกาศ จักรวาล วิทยาศาสตร์ และเทคโนโลยี กดไลก์ กดแชร์ และกดติดตาม แล้วมาค้นพบโลก ค้นพบใจ ไปกับ Mamase จักรวาลของใจครับ
- **TTS Text**: ถ้าชอบเรื่องราวอวกาศ จักรวาล วิทยาศาสตร์ และเทคโนโลยี กดไลก์ กดแชร์ และกดติดตาม แล้วมาค้นพบโลก ค้นพบใจ ไปกับ มามาเซ่ จักรวาลของใจครับ

---

## 🔍 Validation Status

- `PackageService.extract_and_validate`: Passed 100%
- `unzip -t`: Passed 100%
- Image specifications: All 9 images are 1080×1920 8-bit RGB PNG.
