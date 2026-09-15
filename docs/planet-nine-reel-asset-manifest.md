# Mamase Reel Asset Manifest: Planet Nine — มีดาวเคราะห์อีกดวงซ่อนอยู่จริงไหม?

This document describes the visual assets, camera motions, transitions, narration, and technical specifications for the Mamase vertical short-form video package (`mamase-planet-nine-reel-v1.zip`).

---

## 📦 Package Overview

- **Archive**: `dist/mamase-planet-nine-reel-v1.zip`
- **Asset Directory**: `assets/planet_nine_reel/`
- **Resolution**: 1080×1920 (9:16 vertical)
- **Framerate**: 30 FPS
- **Voice Provider**: Google Gemini `Fenrir` (`speed: 1.0`, full phonetic Thai script)
- **Scenes Count**: 9 scenes (~58–64 seconds total)
- **Branding Standard**:
  - Scenes 01–08: Actual Mamase circular logo (`205×205px`) composited at top-right `(x: 839, y: 36)` with soft drop shadow.
  - Scene 09: Locked Mamase Canonical Outro (`reels-end-scene.png`) without duplicate logo, subtitles, or Wan overlay.

---

## 🎬 Scene Breakdown

### Scene 01 — Hook
- **File**: `images/scene-01-hook.png`
- **Motion**: `cinematic_push_in` (Intensity: `0.12`, Speed: `slow`)
- **Transition**: `dissolve`
- **Typography & Key Art**: Title "PLANET NINE" in gold foil Chonburi font, "มีดาวเคราะห์ซ่อนอยู่จริงไหม?" in creamy white with dark outline, accompanied by Mamase presenter pointing toward the dark silhouette of Planet Nine with subtle blue atmospheric rim in deep starfield.
- **Wan 2.2**: 81 frames, 25 steps, `lip_sync: true`, `character_id: "mamase-presenter-v1"`.
- **Narration**: ถ้าเรายังไม่เคยเห็นมันด้วยกล้องดูดาว แล้วนักดาราศาสตร์รู้ได้อย่างไร... ว่าอาจมีดาวเคราะห์ขนาดยักษ์อีกดวง ซ่อนอยู่ที่ขอบระบบสุริยะครับ?
- **TTS Text**: ถ้าเรายังไม่เคยเห็นมันด้วยกล้องดูดาว แล้วนักดาราศาสตร์รู้ได้อย่างไร... ว่าอาจมีดาวเคราะห์ขนาดยักษ์อีกดวง ซ่อนอยู่ที่ขอบระบบสุริยะครับ?

### Scene 02 — Mathematical Evidence (Clustered Orbits)
- **File**: `images/scene-02-strange-orbits.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `smooth_left`
- **Visual**: Authentic Caltech orbital diagram (5850×3900 master, unannotated) showing extreme trans-Neptunian objects' orbits clustered and aligned in one direction against Planet Nine's compensating orbit.
- **Narration**: คำตอบไม่ได้มาจากภาพถ่าย แต่มาจากแรงโน้มถ่วงครับ เมื่อนักดาราศาสตร์พบว่าวัตถุห่างไกลในแถบไคเปอร์ มีวงโคจรเอียงและเกาะกลุ่มชี้ไปทางเดียวกันอย่างผิดปกติ
- **TTS Text**: คำตอบไม่ได้มาจากภาพถ่าย แต่มาจากแรงโน้มถ่วงครับ เมื่อนักดาราศาสตร์พบว่าวัตถุห่างไกลในแถบไคเปอร์ มีวงโคจรเอียงและเกาะกลุ่มชี้ไปทางเดียวกันอย่างผิดปกติ

### Scene 03 — The Massive Invisible Sculptor
- **File**: `images/scene-03-massive-sculptor.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Ultra high-resolution 4K rendering of hypothetical Planet Nine as a mini-Neptune / super-Earth ice giant in deep shadow with crescent sunlight edge.
- **Narration**: โอกาสที่พวกมันจะเรียงตัวแบบนี้โดยบังเอิญมีน้อยกว่าศูนย์จุดสองเปอร์เซ็นต์ เหมือนมีดาวเคราะห์มวลห้าถึงสิบเท่าของโลก คอยใช้แรงโน้มถ่วงต้อนพวกมันไว้
- **TTS Text**: โอกาสที่พวกมันจะเรียงตัวแบบนี้โดยบังเอิญมีน้อยกว่าศูนย์จุดสองเปอร์เซ็นต์ เหมือนมีดาวเคราะห์มวลห้าถึงสิบเท่าของโลก คอยใช้แรงโน้มถ่วงต้อนพวกมันไว้

### Scene 04 — Distance & Scale (400–800 AU Abyss)
- **File**: `images/scene-04-distance-scale.png`
- **Motion**: `slow_zoom_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade_black`
- **Visual**: Inner solar system orbital scale zooming out into the vast, dark cosmic abyss, highlighting the unfathomable distance beyond Neptune.
- **Narration**: หากมีอยู่จริง Planet Nine จะอยู่ห่างจากดวงอาทิตย์ถึง 400 ถึง 800 เท่าของระยะทางโลก ไกลกว่าเนปจูนนับสิบเท่า และโคจรรอบละนับหมื่นปี
- **TTS Text**: หากมีอยู่จริง แพลนเน็ต ไนน์ จะอยู่ห่างจากดวงอาทิตย์ถึงสี่ร้อยถึงแปดร้อยเท่าของระยะทางโลก ไกลกว่าเนปจูนนับสิบเท่า และโคจรรอบละนับหมื่นปี

### Scene 05 — Why Unseen?
- **File**: `images/scene-05-why-unseen.png`
- **Motion**: `documentary_pan` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: James Webb Space Telescope with golden hexagonal mirror array floating in deep cosmos, illustrating the extreme challenge of searching for a faint object whose reflected light drops by trillions of times.
- **Narration**: ทำไมกล้องระดับโลกถึงยังหาไม่เจอ? เพราะที่ระยะนั้น แสงสะท้อนจะจางลงเป็นล้านล้านเท่า มันจึงมืดสนิท เคลื่อนที่ช้ามาก และมีพื้นที่ค้นหากว้างใหญ่ระดับซีกฟ้า
- **TTS Text**: ทำไมกล้องระดับโลกถึงยังหาไม่เจอ? เพราะที่ระยะนั้น แสงสะท้อนจะจางลงเป็นล้านล้านเท่า มันจึงมืดสนิท เคลื่อนที่ช้ามาก และมีพื้นที่ค้นหากว้างใหญ่ระดับซีกฟ้า

### Scene 06 — Evidence vs Hypothesis
- **File**: `images/scene-06-evidence-vs-hypothesis.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.12`, Speed: `slow`)
- **Transition**: `smooth_right`
- **Visual**: Distant Sun glowing faintly amid the Milky Way star clouds with tiny orbital rings of inner planets, emphasizing the scientific boundary between mathematical hypothesis and direct optical detection.
- **Narration**: ดังนั้น Planet Nine ในปัจจุบัน จึงยังเป็น 'สมมติฐาน' ที่มีทฤษฎีรองรับอย่างแน่นหนา แต่ยังไม่ถือเป็นการค้นพบ จนกว่าจะมีใครถ่ายภาพมันได้จริงครับ
- **TTS Text**: ดังนั้น แพลนเน็ต ไนน์ ในปัจจุบัน จึงยังเป็น สมมติฐาน ที่มีทฤษฎีรองรับอย่างแน่นหนา แต่ยังไม่ถือเป็นการค้นพบ จนกว่าจะมีใครถ่ายภาพมันได้จริงครับ

### Scene 07 — The Hunt & Vera C. Rubin Observatory
- **File**: `images/scene-07-vera-rubin-hunt.png`
- **Motion**: `cinematic_push_in` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Official nighttime photograph of the Vera C. Rubin Observatory on Cerro Pachón summit under the Chilean starry sky, representing humanity's upcoming 3.2-gigapixel optical survey.
- **Narration**: แต่การรอคอยใกล้สิ้นสุดลงแล้วครับ หอดูดาวแห่งใหม่อย่าง Vera C. Rubin กำลังจะเริ่มกวาดถ่ายท้องฟ้าทั้งหมด ซึ่งอาจยืนยันตัวตน หรือปิดตำนานดาวเคราะห์ดวงนี้ในไม่ช้า
- **TTS Text**: แต่การรอคอยใกล้สิ้นสุดลงแล้วครับ หอดูดาวแห่งใหม่อย่าง เวรา ซี รูบิน กำลังจะเริ่มกวาดถ่ายท้องฟ้าทั้งหมด ซึ่งอาจยืนยันตัวตน หรือปิดตำนานดาวเคราะห์ดวงนี้ในไม่ช้า

### Scene 08 — Cosmic Frontier Payoff
- **File**: `images/scene-08-cosmic-frontier.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade`
- **Visual**: Cosmic dawn deep-field vista representing the frontier of exploration, expanding humanity's understanding of the cosmos.
- **Narration**: ไม่ว่าคำตอบสุดท้ายจะมีหรือไม่มี ความลับที่ซ่อนอยู่ตรงขอบระบบสุริยะ ก็กำลังจะขยายขอบเขตความเข้าใจของมนุษยชาติไปอีกขั้นครับ
- **TTS Text**: ไม่ว่าคำตอบสุดท้ายจะมีหรือไม่มี ความลับที่ซ่อนอยู่ตรงขอบระบบสุริยะ ก็กำลังจะขยายขอบเขตความเข้าใจของมนุษยชาติไปอีกขั้นครับ

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
