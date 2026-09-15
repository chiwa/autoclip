# Mamase Reel Asset Manifest: Interstellar Space — หลังออกจากระบบสุริยะ เราเจออะไร?

This document describes the visual assets, camera motions, transitions, narration, and technical specifications for the Mamase vertical short-form video package (`mamase-interstellar-space-reel-v1.zip`).

---

## 📦 Package Overview

- **Archive**: `dist/mamase-interstellar-space-reel-v1.zip`
- **Asset Directory**: `assets/interstellar_space_reel/`
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
- **Typography & Key Art**: Title "INTERSTELLAR SPACE" in gold foil Chonburi font with radial glow and lens flare accent, subtitle "พ้นระบบสุริยะ... เราเจออะไร?" in creamy white with dark outline, accompanied by Mamase presenter gesturing toward the vast glowing interstellar plasma threshold.
- **Wan 2.2**: 81 frames, 25 steps, `lip_sync: true`, `character_id: "mamase-presenter-v1"`.
- **Narration**: เมื่อยานอวกาศหลุดพ้นขอบระบบสุริยะออกไป... เราจะเจอกับความว่างเปล่าที่มืดมิดจริง ๆ หรือเปล่าครับ?
- **TTS Text**: เมื่อยานอวกาศหลุดพ้นขอบระบบสุริยะออกไป... เราจะเจอกับความว่างเปล่าที่มืดมิดจริง ๆ หรือเปล่าครับ?

### Scene 02 — Crossing the Heliopause
- **File**: `images/scene-02-heliopause.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `smooth_left`
- **Visual**: Authentic robotic depiction of Voyager 1 crossing the shimmering heliopause plasma curtain, leaving the solar bubble into the interstellar medium.
- **Narration**: หลายคนคิดว่าอวกาศระหว่างดวงดาวคือความว่างเปล่าสนิท แต่ข้อมูลจากยานวอยเอเจอร์ที่เดินทางพ้นขอบระบบสุริยะออกไป เผยความจริงที่ต่างออกไปสิ้นเชิงครับ
- **TTS Text**: หลายคนคิดว่าอวกาศระหว่างดวงดาวคือความว่างเปล่าสนิท แต่ข้อมูลจากยาน วอยเอเจอร์ ที่เดินทางพ้นขอบระบบสุริยะออกไป เผยความจริงที่ต่างออกไปสิ้นเชิงครับ

### Scene 03 — Galactic Cosmic Rays Surge
- **File**: `images/scene-03-cosmic-rays.png`
- **Motion**: `cinematic_push_in` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Ultra-high-energy galactic cosmic rays piercing interstellar space at near light-speed, leaving electric-blue and ultraviolet relativistic ionization trails across the Milky Way starfield.
- **Narration**: ทันทีที่ข้ามพรมแดน ลมสุริยะจากดวงอาทิตย์ก็เงียบหายไป แต่สิ่งที่พุ่งเข้ามาแทน คือ รังสีคอสมิกจากดาราจักร อนุภาคพลังงานสูงยิ่งยวดที่เดินทางมาจากทั่วทางช้างเผือก
- **TTS Text**: ทันทีที่ข้ามพรมแดน ลมสุริยะจากดวงอาทิตย์ก็เงียบหายไป แต่สิ่งที่พุ่งเข้ามาแทน คือ รังสีคอสมิกจากดาราจักร อนุภาคพลังงานสูงยิ่งยวดที่เดินทางมาจากทั่วทางช้างเผือก

### Scene 04 — The Interstellar Medium (Plasma)
- **File**: `images/scene-04-plasma-ism.png`
- **Motion**: `slow_zoom_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade_black`
- **Visual**: Tenuous, cold ionized hydrogen and helium gas glowing faintly with ethereal violet-magenta and deep cyan luminescence across light-years.
- **Narration**: และพื้นที่ตรงนี้ไม่ได้มีแต่ความว่างเปล่า แต่เต็มไปด้วย พลาสมาอวกาศ ไอออนของไฮโดรเจนและฮีเลียมที่บางเบามาก แต่ว่องไวและพร้อมนำพากระแสแม่เหล็ก
- **TTS Text**: และพื้นที่ตรงนี้ไม่ได้มีแต่ความว่างเปล่า แต่เต็มไปด้วย พลาสมาอวกาศ ไอออนของไฮโดรเจนและฮีเลียมที่บางเบามาก แต่ว่องไวและพร้อมนำพากระแสแม่เหล็ก

### Scene 05 — Cosmic Dust & Building Blocks
- **File**: `images/scene-05-cosmic-dust.png`
- **Motion**: `documentary_pan` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Macro-scale cosmic view of crystalline silicate micro-grains, carbon graphite flakes, and organic polycyclic aromatic hydrocarbons (PAHs) glinting like microscopic diamonds and stardust.
- **Narration**: ปะปนอยู่กับ ฝุ่นคอสมิก ละอองธาตุหนักและโมเลกุลคาร์บอนที่ซากดาวฤกษ์รุ่นก่อนพ่นทิ้งไว้ รอคอยการรวมตัวเป็นดาวเคราะห์และสิ่งมีชีวิตรุ่นต่อไป
- **TTS Text**: ปะปนอยู่กับ ฝุ่นคอสมิก ละอองธาตุหนักและโมเลกุลคาร์บอนที่ซากดาวฤกษ์รุ่นก่อนพ่นทิ้งไว้ รอคอยการรวมตัวเป็นดาวเคราะห์และสิ่งมีชีวิตรุ่นต่อไป

### Scene 06 — The Local Interstellar Cloud
- **File**: `images/scene-06-local-cloud.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.13`, Speed: `slow`)
- **Transition**: `smooth_right`
- **Visual**: 3D astrophysics documentary map showing our Sun and planets inside their protective heliosphere teardrop cocoon, drifting through the translucent wisps of the Local Interstellar Cloud inside the Local Bubble.
- **Narration**: ที่น่าทึ่งคือ ตอนนี้ระบบสุริยะของเรา กำลังล่องลอยอยู่ท่ามกลางกลุ่มก๊าซที่ชื่อว่า เมฆระหว่างดาวท้องถิ่น ซึ่งอยู่ในโพรงฟองยักษ์ที่เกิดจาก ซูเปอร์โนวา โบราณ
- **TTS Text**: ที่น่าทึ่งคือ ตอนนี้ระบบสุริยะของเรา กำลังล่องลอยอยู่ท่ามกลางกลุ่มก๊าซที่ชื่อว่า เมฆระหว่างดาวท้องถิ่น ซึ่งอยู่ในโพรงฟองยักษ์ที่เกิดจาก ซูเปอร์โนวา โบราณ

### Scene 07 — Galactic Magnetic Ribbons
- **File**: `images/scene-07-magnetic-fields.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Luminous, elegant magnetic flux ribbons and electromagnetic streamlines curving through deep space like invisible ocean currents, deflecting cosmic rays and channeling plasma.
- **Narration**: นอกจากนี้ยังมี เส้นแรงแม่เหล็กของดาราจักร ที่คดเคี้ยวและคอยเบี่ยงเบนทิศทางของอนุภาค ราวกับกระแสน้ำในมหาสมุทรที่มองไม่เห็น
- **TTS Text**: นอกจากนี้ยังมี เส้นแรงแม่เหล็กของดาราจักร ที่คดเคี้ยวและคอยเบี่ยงเบนทิศทางของอนุภาค ราวกับกระแสน้ำในมหาสมุทรที่มองไม่เห็น

### Scene 08 — Cosmic Cradle Payoff
- **File**: `images/scene-08-cosmic-cradle.png`
- **Motion**: `cinematic_push_in` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade`
- **Visual**: Deep cosmic vista of glowing jewel-toned star nurseries, newborn stars igniting in collapsing clouds, connected by delicate cosmic dust filaments.
- **Narration**: อวกาศระหว่างดวงดาว จึงไม่ใช่สุสานที่ว่างเปล่า... แต่คือมหาสมุทรแห่งชีวิต ที่เชื่อมต่อทุกดวงดาว และเป็นจุดเริ่มต้นของทุกสิ่งในจักรวาลครับ
- **TTS Text**: อวกาศระหว่างดวงดาว จึงไม่ใช่สุสานที่ว่างเปล่า... แต่คือมหาสมุทรแห่งชีวิต ที่เชื่อมต่อทุกดวงดาว และเป็นจุดเริ่มต้นของทุกสิ่งในจักรวาลครับ

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

- **unzip -t**: PASSED (100% integrity, zero corrupt entries)
- **AutoClip PackageService**: PASSED 100%
- **Image Specifications**: All 9 files 1080×1920 8-bit RGB PNG
- **Branding Standard**: Compliant with Mamase locked outro, circular logo placement, and typography hierarchy.
