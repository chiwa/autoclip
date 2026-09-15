# Mamase Reel Asset Manifest: Oort Cloud — ขอบจริงของระบบสุริยะอยู่ตรงไหน?

This document describes the visual assets, camera motions, transitions, narration, and technical specifications for the Mamase vertical short-form video package (`mamase-oort-cloud-reel-v1.zip`).

---

## 📦 Package Overview

- **Archive**: `dist/mamase-oort-cloud-reel-v1.zip`
- **Asset Directory**: `assets/oort_cloud_reel/`
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
- **Typography & Key Art**: Title "OORT CLOUD" in gold foil Chonburi font with ambient glow and flare, subtitle "ขอบจริงของระบบสุริยะ อยู่ตรงไหน?" in creamy white with dark outline, accompanied by Mamase presenter gesturing toward the colossal spherical swarm of the Oort Cloud enclosing the solar system.
- **Wan 2.2**: 81 frames, 25 steps, `lip_sync: true`, `character_id: "mamase-presenter-v1"`.
- **Narration**: เรามักได้ยินว่ายานวอยเอเจอร์เดินทางออกนอกระบบสุริยะแล้ว... แต่รู้ไหมครับว่า ความจริงมันยังไปไม่ถึงขอบจริง ๆ เลยด้วยซ้ำ?
- **TTS Text**: เรามักได้ยินว่ายานวอยเอเจอร์เดินทางออกนอกระบบสุริยะแล้ว... แต่รู้ไหมครับว่า ความจริงมันยังไปไม่ถึงขอบจริง ๆ เลยด้วยซ้ำ?

### Scene 02 — Heliosphere vs True Boundary
- **File**: `images/scene-02-heliosphere-bubble.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `smooth_left`
- **Visual**: The glowing golden-amber bubble of the Heliosphere enclosing the Sun and inner planets, with Voyager crossing its boundary into the vast cosmic abyss ahead.
- **Narration**: สิ่งที่วอยเอเจอร์ข้ามพ้น เป็นเพียง ฟองลมสุริยะ หรือเฮลิโอสเฟียร์ แต่ขอบเขตแรงโน้มถ่วงที่แท้จริงของดวงอาทิตย์ อยู่ไกลออกไปกว่านั้นมหาศาลครับ
- **TTS Text**: สิ่งที่วอยเอเจอร์ข้ามพ้น เป็นเพียง ฟองลมสุริยะ หรือเฮลิโอสเฟียร์ แต่ขอบเขตแรงโน้มถ่วงที่แท้จริงของดวงอาทิตย์ อยู่ไกลออกไปกว่านั้นมหาศาลครับ

### Scene 03 — Revealing the Oort Cloud (Spherical Shell)
- **File**: `images/scene-03-spherical-swarm.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Grand 3D astronomical visualization showing the tiny inner planetary disk at the center, completely enclosed within the colossal spherical swarm of trillions of icy cometary objects.
- **Narration**: นั่นคือ เมฆออร์ต กำแพงน้ำแข็งทรงกลมขนาดยักษ์ ที่โอบล้อมระบบสุริยะไว้ทั้งหมด ประกอบด้วยวัตถุน้ำแข็งและดาวหางนับล้านล้านดวง
- **TTS Text**: นั่นคือ เมฆออร์ต กำแพงน้ำแข็งทรงกลมขนาดยักษ์ ที่โอบล้อมระบบสุริยะไว้ทั้งหมด ประกอบด้วยวัตถุน้ำแข็งและดาวหางนับล้านล้านดวง

### Scene 04 — The Incomprehensible Scale
- **File**: `images/scene-04-distance-scale.png`
- **Motion**: `slow_zoom_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade_black`
- **Visual**: Looking from an icy planetesimal into the dark cosmic abyss stretching across 2,000 to 100,000 AU (nearly 2 light-years) toward neighboring stars.
- **Narration**: ขอบด้านในของเมฆออร์ต เริ่มต้นที่สองพันเท่าของระยะทางโลก และแผ่ขยายออกไปไกลถึงหนึ่งแสนเท่า หรือเกือบสองปีแสง... ครึ่งทางไปยังดาวฤกษ์ดวงถัดไป
- **TTS Text**: ขอบด้านในของเมฆออร์ต เริ่มต้นที่สองพันเท่าของระยะทางโลก และแผ่ขยายออกไปไกลถึงหนึ่งแสนเท่า หรือเกือบสองปีแสง... ครึ่งทางไปยังดาวฤกษ์ดวงถัดไป

### Scene 05 — Voyager Reality Check (Time Scale)
- **File**: `images/scene-05-voyager-journey.png`
- **Motion**: `documentary_pan` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Voyager 1 robotic spacecraft floating in the deep star-studded space between the heliosphere and the Oort Cloud across millennia.
- **Narration**: ด้วยความเร็วของยานวอยเอเจอร์ในปัจจุบัน มันต้องใช้เวลาอีกถึง 300 ปี กว่าจะไปแตะขอบในของเมฆออร์ต และต้องใช้เวลาอีกกว่า 30,000 ปี ถึงจะทะลุผ่านออกไปได้จริง
- **TTS Text**: ด้วยความเร็วของยาน วอยเอเจอร์ ในปัจจุบัน มันต้องใช้เวลาอีกถึงสามร้อยปี กว่าจะไปแตะขอบในของเมฆออร์ต และต้องใช้เวลาอีกกว่าสามหมื่นปี ถึงจะทะลุผ่านออกไปได้จริง

### Scene 06 — The Primordial Cosmic Freezer
- **File**: `images/scene-06-cosmic-freezer.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.13`, Speed: `slow`)
- **Transition**: `smooth_right`
- **Visual**: Primordial cometary ice nucleus speeding across deep space leaving its glowing cyan ion/dust tail, preserving pristine solar system volatiles from 4.6 billion years ago.
- **Narration**: ที่นี่คือตู้แช่แข็งโบราณที่เก็บสสารดึกดำบรรพ์ตั้งแต่กำเนิดระบบสุริยะ และเป็นต้นกำเนิดของดาวหางคาบยาว ที่นาน ๆ ครั้งจะหลุดเข้ามาเฉียดโลก
- **TTS Text**: ที่นี่คือตู้แช่แข็งโบราณที่เก็บสสารดึกดำบรรพ์ตั้งแต่กำเนิดระบบสุริยะ และเป็นต้นกำเนิดของดาวหางคาบยาว ที่นาน ๆ ครั้งจะหลุดเข้ามาเฉียดโลก

### Scene 07 — The True Edge of the Sun's Gravity
- **File**: `images/scene-07-gravity-boundary.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Spacetime curvature grid and gravitational boundary where the Sun's gravitational well gives way to the galactic tidal field of the Milky Way.
- **Narration**: ตรงสุดขอบของเมฆออร์ต คือจุดที่แรงโน้มถ่วงของดวงอาทิตย์ พ่ายแพ้ให้กับแรงดึงดูดของดาราจักร นี่ต่างหากคือ เส้นแบ่งเขตแดนที่แท้จริง ของระบบสุริยะ
- **TTS Text**: ตรงสุดขอบของเมฆออร์ต คือจุดที่แรงโน้มถ่วงของดวงอาทิตย์ พ่ายแพ้ให้กับแรงดึงดูดของดาราจักร นี่ต่างหากคือ เส้นแบ่งเขตแดนที่แท้จริง ของระบบสุริยะ

### Scene 08 — Cosmic Horizon Payoff
- **File**: `images/scene-08-cosmic-home.png`
- **Motion**: `cinematic_push_in` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade`
- **Visual**: The glowing cosmic sphere containing our galaxy and cosmic web, conveying the philosophical perspective that our cosmic home is vastly larger than imagined.
- **Narration**: บ้านของเราไม่ได้สิ้นสุดแค่ดาวเคราะห์แปดดวงหรือพลูโต แต่ยิ่งใหญ่ไพศาลกว่าที่เราเคยจินตนาการไว้มากครับ
- **TTS Text**: บ้านของเราไม่ได้สิ้นสุดแค่ดาวเคราะห์แปดดวงหรือพลูโต แต่ยิ่งใหญ่ไพศาลกว่าที่เราเคยจินตนาการไว้มากครับ

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
