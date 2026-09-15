# Mamase Reel Asset Manifest: STAR FLYBY — ถ้ามีดาวอีกดวงบินเฉียดระบบสุริยะ โลกจะรอดไหม?

This document describes the visual assets, camera motions, transitions, narration, and technical specifications for the Mamase vertical short-form video package (`mamase-stellar-flyby-reel-v1.zip`).

---

## 📦 Package Overview

- **Archive**: `dist/mamase-stellar-flyby-reel-v1.zip`
- **Asset Directory**: `assets/stellar_flyby_reel/`
- **Resolution**: 1080×1920 (9:16 vertical)
- **Framerate**: 30 FPS
- **Voice Provider**: Google Gemini `Fenrir` (`speed: 1.0`, full phonetic Thai script)
- **Scenes Count**: 9 scenes (~58–63 seconds total)
- **Branding Standard**:
  - Scenes 01–08: Actual Mamase circular logo (`205×205px`) composited at top-right `(x: 839, y: 36)` with soft drop shadow.
  - Scene 09: Locked Mamase Canonical Outro (`reels-end-scene.png`) without duplicate logo, subtitles, or Wan overlay.

---

## 🎬 Scene Breakdown

### Scene 01 — Hook & Key Art
- **File**: `images/scene-01-hook.png`
- **Motion**: `cinematic_push_in` (Intensity: `0.12`, Speed: `slow`)
- **Transition**: `dissolve`
- **Typography & Key Art**: Title "STAR FLYBY" in gold foil Chonburi font with ambient cosmic glow, subtitle "ถ้ามีดาวอีกดวงบินเฉียด... โลกจะรอดไหม?" in creamy white with dark outline, badge box "“มันกำลังเข้ามา…”" in glowing amber-red, accompanied by Mamase presenter gesturing toward the massive blazing orange dwarf star hurtling through deep space.
- **Wan 2.2**: 81 frames, 25 steps, `lip_sync: true`, `character_id: "mamase-presenter-v1"`.
- **Narration**: ถ้าวันหนึ่ง มีดาวฤกษ์อีกดวงบินเฉียดเข้ามาใกล้ระบบสุริยะ... คุณคิดว่าโลกของเราจะรอดไหมครับ?
- **TTS Text**: ถ้าวันหนึ่ง มีดาวฤกษ์อีกดวงบินเฉียดเข้ามาใกล้ระบบสุริยะ... คุณคิดว่าโลกของเราจะรอดไหมครับ?

### Scene 02 — The Core Revelation: No Collision Needed
- **File**: `images/scene-02-core-revelation.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `smooth_left`
- **Visual**: Immense orange dwarf star passing through space above the distant solar system plane, radiating intense coronal flares and warping background starlight with gravitational shockwaves.
- **Narration**: ความจริงที่น่าขนลุกคือ มันไม่จำเป็นต้องพุ่งชนโลก หรือเข้ามาใกล้ดวงอาทิตย์เลยครับ แค่มันบินเฉียดขอบนอก ก็เปลี่ยนชะตากรรมของระบบสุริยะได้แล้ว
- **TTS Text**: ความจริงที่น่าขนลุกคือ มันไม่จำเป็นต้องพุ่งชนโลก หรือเข้ามาใกล้ดวงอาทิตย์เลยครับ แค่มันบินเฉียดขอบนอก ก็เปลี่ยนชะตากรรมของระบบสุริยะได้แล้ว

### Scene 03 — The Moving Solar System (Not Static)
- **File**: `images/scene-03-moving-solar-system.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Helical vortex model of the entire solar system hurtling through the Milky Way galaxy at 230 km/s, with planets tracing luminous spiral paths around the moving Sun, surrounded by drifting stars.
- **Narration**: เพราะระบบสุริยะของเราไม่ได้ลอยนิ่งอยู่กับที่ แต่กำลังเดินทางรอบกาแล็กซีด้วยความเร็ว 230 กิโลเมตรต่อวินาที และดาวดวงอื่นก็กำลังเคลื่อนที่เหมือนกัน
- **TTS Text**: เพราะระบบสุริยะของเราไม่ได้ลอยนิ่งอยู่กับที่ แต่กำลังเดินทางรอบกาแล็กซีด้วยความเร็ว สองร้อยสามสิบ กิโลเมตรต่อวินาที และดาวดวงอื่นก็กำลังเคลื่อนที่เหมือนกัน

### Scene 04 — Breaching the Oort Cloud (The Ice Wall)
- **File**: `images/scene-04-breaching-oort-cloud.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.13`, Speed: `slow`)
- **Transition**: `fade_black`
- **Visual**: Vast spherical shell of trillions of icy cometary planetesimals enclosing the distant Sun, as the fiery orange intruder star enters and slices directly through the fragile icy swarm.
- **Narration**: และด่านแรกที่มันจะเจอ คือ เมฆออร์ต กำแพงน้ำแข็งทรงกลมขนาดยักษ์ที่มีดาวหางนับล้านล้านดวง เกาะอยู่ด้วยแรงโน้มถ่วงที่เปราะบางมาก
- **TTS Text**: และด่านแรกที่มันจะเจอ คือ เมฆออร์ต กำแพงน้ำแข็งทรงกลมขนาดยักษ์ที่มีดาวหางนับล้านล้านดวง เกาะอยู่ด้วยแรงโน้มถ่วงที่เปราะบางมาก

### Scene 05 — The Gravitational Domino Effect (Comet Shower Inbound)
- **File**: `images/scene-05-domino-effect-comets.png`
- **Motion**: `documentary_pan` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Dramatic gravitational perturbation: thousands of glowing comets with brilliant electric-blue ion tails and white dust tails streaming inward from the cosmic outskirts towards the Sun and inner rocky planets.
- **Narration**: แรงดึงดูดของดาวฤกษ์ผู้มาเยือน จะทำหน้าที่เหมือนไม้พายที่กวนผิวน้ำ เหวี่ยงฝูงดาวหางมหาศาล ให้พุ่งดิ่งตรงเข้ามายังระบบสุริยะชั้นใน... ถล่มโลกและดาวเคราะห์หิน!
- **TTS Text**: แรงดึงดูดของดาวฤกษ์ผู้มาเยือน จะทำหน้าที่เหมือนไม้พายที่กวนผิวน้ำ เหวี่ยงฝูงดาวหางมหาศาล ให้พุ่งดิ่งตรงเข้ามายังระบบสุริยะชั้นใน... ถล่มโลกและดาวเคราะห์หิน!

### Scene 06 — The Real Approaching Threat: Gliese 710
- **File**: `images/scene-06-gliese-710-threat.png`
- **Motion**: `slow_zoom_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `smooth_right`
- **Visual**: High-precision astronomical visualization of orange dwarf star Gliese 710 in constellation Serpens, with its Gaia DR3 trajectory vector cutting through interstellar space toward our solar boundary in 1.29 million years.
- **Narration**: และนี่ไม่ใช่แค่เรื่องสมมุติครับ! ข้อมูลจากกล้องอวกาศกายอา ยืนยันว่าดาวแคระส้ม กลีเซอ 710 กำลังพุ่งตรงมาหาเรา และจะตัดเข้ากลางเมฆออร์ตในอีก 1.3 ล้านปีข้างหน้า
- **TTS Text**: และนี่ไม่ใช่แค่เรื่องสมมุติครับ! ข้อมูลจากกล้องอวกาศ กาย-อา ยืนยันว่าดาวแคระส้ม กลีเซอ เจ็ดหนึ่งศูนย์ กำลังพุ่งตรงมาหาเรา และจะตัดเข้ากลางเมฆออร์ตในอีก หนึ่งจุดสาม ล้านปีข้างหน้า

### Scene 07 — The Sky View on Earth (Magnitude -2.7)
- **File**: `images/scene-07-sky-view-earth.png`
- **Motion**: `cinematic_push_in` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Night sky view from Earth's serene lake landscape: a brilliant orange-amber star shining intensely at magnitude -2.7, rivalling Venus, casting a warm golden reflection across the water, accompanied by distant meteor streaks.
- **Narration**: ในยุคนั้น ท้องฟ้าบนโลกจะมองเห็นดาวสีส้มดวงนี้สว่างจ้าแข่งกับดาวศุกร์ ก่อนที่ฝนดาวหางระลอกใหญ่จะตามมาเยือนระบบสุริยะชั้นใน
- **TTS Text**: ในยุคนั้น ท้องฟ้าบนโลกจะมองเห็นดาวสีส้มดวงนี้สว่างจ้าแข่งกับดาวศุกร์ ก่อนที่ฝนดาวหางระลอกใหญ่จะตามมาเยือนระบบสุริยะชั้นใน

### Scene 08 — Mamase Philosophical Payoff: The Cosmic Voyage
- **File**: `images/scene-08-mamase-cosmic-voyage.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade`
- **Visual**: Majestic view of Planet Earth suspended like a delicate blue marble in the cosmic ocean against the sweeping arc of the Milky Way, conveying that Earth is a cosmic voyager traveling among moving stars.
- **Narration**: อวกาศจึงไม่ใช่ความเงียบสงบที่หยุดนิ่ง แต่คือการเดินทางที่เราต้องพบเจอกับเพื่อนบ้านใหม่... ตลอดเวลาครับ
- **TTS Text**: อวกาศจึงไม่ใช่ความเงียบสงบที่หยุดนิ่ง แต่คือการเดินทางที่เราต้องพบเจอกับเพื่อนบ้านใหม่... ตลอดเวลาครับ

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

- **ZIP integrity**: Passed (`unzip -t dist/mamase-stellar-flyby-reel-v1.zip`)
- **Dimensions**: All 9 images strictly 1080×1920 8-bit RGB PNG
- **Branding**: Official Mamase circular logo (205×205px) placed at top-right (x: 839, y: 36) with soft shadow on Scenes 01–08; Scene 09 locked outro clean
- **Text discipline**: Scenes 02–08 completely free of baked-in labels and text overlays
- **Contract compliance**: `PackageService.extract_and_validate` passed 100%
