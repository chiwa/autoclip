# Mamase Reel Asset Manifest: Comets — ดาวหาง ผู้มาเยือนจากขอบระบบสุริยะ

This document describes the visual assets, camera motions, transitions, narration, and technical specifications for the Mamase vertical short-form video package (`mamase-comets-reel-v1.zip`).

---

## 📦 Package Overview

- **Archive**: `dist/mamase-comets-reel-v1.zip`
- **Asset Directory**: `assets/comets_reel/`
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
- **Typography & Key Art**: Title "COMETS" in gold foil Chonburi font with ambient cosmic glow, subtitle "ทำไมหาง ไม่ได้ลากตามหลังเสมอไป?" in creamy white with dark outline, accompanied by Mamase presenter gesturing toward the glowing comet nucleus hurtling through deep space with brilliant ion and dust tails.
- **Wan 2.2**: 81 frames, 25 steps, `lip_sync: true`, `character_id: "mamase-presenter-v1"`.
- **Narration**: เวลาเราเห็นดาวหางบนท้องฟ้า หลายคนคิดว่าหางของมันต้องลากตามหลังทิศที่มันพุ่งไป... แต่รู้ไหมครับว่า ความจริงไม่ได้เป็นแบบนั้นเลย?
- **TTS Text**: เวลาเราเห็นดาวหางบนท้องฟ้า หลายคนคิดว่าหางของมันต้องลากตามหลังทิศที่มันพุ่งไป... แต่รู้ไหมครับว่า ความจริงไม่ได้เป็นแบบนั้นเลย?

### Scene 02 — Solar Wind Direction (Why Tails Point Away)
- **File**: `images/scene-02-solar-wind-direction.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `smooth_left`
- **Visual**: Solar system orbital plane showing the blazing golden Sun at the center radiating energetic solar wind and radiation pressure outward. An active comet orbits nearby with its glowing gas and dust tails blown directly away from the Sun, defying its direction of motion.
- **Narration**: หางของดาวหาง ไม่ได้เกิดจากแรงเสียดทานของอากาศ แต่ถูก ลมสุริยะ และแรงดันแสงจากดวงอาทิตย์เป่าพัดออกไป ทำให้หางของมัน ชี้หนีดวงอาทิตย์เสมอ ไม่ว่ามันจะบินไปทางไหน
- **TTS Text**: หางของดาวหาง ไม่ได้เกิดจากแรงเสียดทานของอากาศ แต่ถูก ลมสุริยะ และแรงดันแสงจากดวงอาทิตย์เป่าพัดออกไป ทำให้หางของมัน ชี้หนีดวงอาทิตย์เสมอ ไม่ว่ามันจะบินไปทางไหน

### Scene 03 — Flying Tail-First (The Paradox)
- **File**: `images/scene-03-tail-first-flight.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Dramatic astronomical view of a comet speeding outbound into deep space away from the distant Sun. Because the solar wind continues blowing outward from behind it, the comet flies tail-first into the cold cosmos.
- **Narration**: นั่นหมายความว่า ตอนที่ดาวหางกำลังบินออกจากดวงอาทิตย์... มันกำลังบินโดย เอาหางพุ่งนำหน้าตัว ครับ!
- **TTS Text**: นั่นหมายความว่า ตอนที่ดาวหางกำลังบินออกจากดวงอาทิตย์... มันกำลังบินโดย เอาหางพุ่งนำหน้าตัว ครับ!

### Scene 04 — Anatomy of Two Tails (Ion vs Dust)
- **File**: `images/scene-04-two-tails-anatomy.png`
- **Motion**: `documentary_pan` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `fade_black`
- **Visual**: Close-up high-resolution telescopic visualization revealing the distinct separation of the comet's two tails: a narrow, luminescent electric-blue ion tail streaming straight along solar magnetic lines, and a broader, curved warm-golden dust tail gently trailing along its orbital arc.
- **Narration**: และถ้าสังเกตให้ดี ดาวหางมีถึงสองหางครับ หางไอออนสีน้ำเงินตรงแน่วที่ถูกลมสุริยะซัด กับหางฝุ่นสีขาวนวลที่โค้งตามวงโคจรเพราะแรงดันแสง
- **TTS Text**: และถ้าสังเกตให้ดี ดาวหางมีถึงสองหางครับ หางไอออนสีน้ำเงินตรงแน่วที่ถูกลมสุริยะซัด กับหางฝุ่นสีขาวนวลที่โค้งตามวงโคจรเพราะแรงดันแสง

### Scene 05 — The "Dirty Snowball" Nucleus
- **File**: `images/scene-05-nucleus-jets.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.13`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Extreme close-up of the rugged, cratered cometary nucleus — a dark primordial "dirty snowball" of rock, carbonaceous organics, and water ice. Active geyser-like jets erupt from crevasses on the sunlit side, spewing pressurized gas and sparkling dust into space.
- **Narration**: ใจกลางของมันคือ ก้อนน้ำแข็งสกปรก ขนาดยักษ์ ที่เก็บกักน้ำแข็ง ก๊าซคาร์บอน และฝุ่นดึกดำบรรพ์มาตั้งแต่ยุคกำเนิดระบบสุริยะ เมื่อเข้าใกล้แดด น้ำแข็งจึงระเหิดพวยพุ่งออกมา
- **TTS Text**: ใจกลางของมันคือ ก้อนน้ำแข็งสกปรก ขนาดยักษ์ ที่เก็บกักน้ำแข็ง ก๊าซคาร์บอน และฝุ่นดึกดำบรรพ์มาตั้งแต่ยุคกำเนิดระบบสุริยะ เมื่อเข้าใกล้แดด น้ำแข็งจึงระเหิดพวยพุ่งออกมา

### Scene 06 — Origin From the Cosmic Edge
- **File**: `images/scene-06-origin-from-edge.png`
- **Motion**: `slow_zoom_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `smooth_right`
- **Visual**: Vast scale visualization of the solar system's frozen outer frontiers — the Kuiper Belt and the distant Oort Cloud. An icy cometary body is perturbed from its gravitational slumber, embarking on a multi-hundred-thousand-year pilgrimage inward.
- **Narration**: พวกมันคือผู้มาเยือนจากพรมแดนสุดขอบระบบสุริยะ ทั้งแถบไคเปอร์และเมฆออร์ตที่อยู่ไกลนับปีแสง บางดวงใช้เวลานับแสนปี กว่าจะเดินทางมาถึงเราหนึ่งครั้ง
- **TTS Text**: พวกมันคือผู้มาเยือนจากพรมแดนสุดขอบระบบสุริยะ ทั้งแถบไคเปอร์และเมฆออร์ตที่อยู่ไกลนับปีแสง บางดวงใช้เวลานับแสนปี กว่าจะเดินทางมาถึงเราหนึ่งครั้ง

### Scene 07 — Seeders of Earth's Oceans and Life
- **File**: `images/scene-07-seeders-of-life.png`
- **Motion**: `cinematic_push_in` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Early Hadean/Archean Earth illuminated by cosmic starlight and glowing oceans. An incoming comet hurtles through the atmosphere, delivering pristine water ice, amino acids, and complex organic molecules to seed primordial life.
- **Narration**: นักวิทยาศาสตร์ยังพบว่า ดาวหางอาจเป็นผู้ส่งมอบ น้ำ และ กรดอะมิโน ต้นกำเนิดของชีวิตมายังโลก เมื่อสี่พันล้านปีก่อนอีกด้วย
- **TTS Text**: นักวิทยาศาสตร์ยังพบว่า ดาวหางอาจเป็นผู้ส่งมอบ น้ำ และ กรดอะมิโน ต้นกำเนิดของชีวิตมายังโลก เมื่อสี่พันล้านปีก่อนอีกด้วย

### Scene 08 — The Cosmic Connection Payoff
- **File**: `images/scene-08-cosmic-connection.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade`
- **Visual**: Breathtaking real astrophotography landscape of Comet C/2020 F3 (NEOWISE) with glowing twin tails reflected over a tranquil mirror-like lake under twilight skies, accompanied by a shooting star streak.
- **Narration**: ทุกครั้งที่เราเงยหน้ามองดาวหาง... เราจึงไม่ได้มองแค่ก้อนน้ำแข็งในอวกาศ แต่กำลังมองดูผู้ส่งสาร ที่อาจเป็นต้นกำเนิดของชีวิตบนโลกครับ
- **TTS Text**: ทุกครั้งที่เราเงยหน้ามองดาวหาง... เราจึงไม่ได้มองแค่ก้อนน้ำแข็งในอวกาศ แต่กำลังมองดูผู้ส่งสาร ที่อาจเป็นต้นกำเนิดของชีวิตบนโลกครับ

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

- **ZIP integrity**: Passed (`unzip -t dist/mamase-comets-reel-v1.zip`)
- **Dimensions**: All 9 images strictly 1080×1920 8-bit RGB PNG
- **Branding**: Official Mamase circular logo (205×205px) placed at top-right (x: 839, y: 36) with soft shadow on Scenes 01–08; Scene 09 locked outro clean
- **Text discipline**: Scenes 02–08 completely free of baked-in labels and text overlays
- **Contract compliance**: `PackageService.extract_and_validate` passed 100%
