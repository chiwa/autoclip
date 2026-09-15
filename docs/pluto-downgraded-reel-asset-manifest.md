# Mamase Reel Asset Manifest: Pluto — จากดาวเคราะห์ดวงที่ 9 สู่ดาวเคราะห์แคระ

This document describes the visual assets, camera motions, transitions, narration, and technical specifications for the Mamase vertical short-form video package (`mamase-pluto-downgraded-reel-v1.zip`).

---

## 📦 Package Overview

- **Archive**: `dist/mamase-pluto-downgraded-reel-v1.zip`
- **Asset Directory**: `assets/pluto_downgraded_reel/`
- **Resolution**: 1080×1920 (9:16 vertical)
- **Framerate**: 30 FPS
- **Voice Provider**: Google Gemini `Fenrir` (`speed: 1.0`, full phonetic Thai script)
- **Scenes Count**: 9 scenes (~58–65 seconds total)
- **Branding Standard**:
  - Scenes 01–08: Actual Mamase circular logo (`205×205px`) composited at top-right `(x: 839, y: 36)` with soft drop shadow.
  - Scene 09: Locked Mamase Canonical Outro (`reels-end-scene.png`) without duplicate logo, subtitles, or Wan overlay.

---

## 🎬 Scene Breakdown

### Scene 01 — Hook
- **File**: `images/scene-01-hook.png`
- **Motion**: `cinematic_push_in` (Intensity: `0.12`, Speed: `slow`)
- **Transition**: `dissolve`
- **Typography & Key Art**: Title "PLUTO" in gold foil Chonburi font, "ทำไมถูกลดชั้น?" in creamy white with dark blue outline, accompanied by Mamase presenter pointing toward Pluto and the distant 8 planets.
- **Wan 2.2**: 81 frames, 25 steps, `lip_sync: true`, `character_id: "mamase-presenter-v1"`.
- **Narration**: ทำไม Pluto ถึงถูกลดชั้นครับ ทั้งที่เมื่อก่อนมันคือดาวเคราะห์ดวงที่ 9 ของระบบสุริยะ?
- **TTS Text**: ทำไม พลูโต ถึงถูกลดชั้นครับ ทั้งที่เมื่อก่อนมันคือดาวเคราะห์ดวงที่เก้าของระบบสุริยะ?

### Scene 02 — Ninth Planet Legacy (1930)
- **File**: `images/scene-02-ninth-planet.png`
- **Motion**: `documentary_pan` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `smooth_left`
- **Visual**: Classic solar system alignment with 9 planets, highlighting Pluto at the outermost rim beyond Neptune in vintage astronomical chart aesthetic.
- **Narration**: หลังถูกค้นพบในปี 1930 Pluto ครองตำแหน่งดาวเคราะห์ดวงที่ 9 มานานถึง 76 ปี
- **TTS Text**: หลังถูกค้นพบในปีหนึ่งพันเก้าร้อยสามสิบ พลูโต ครองตำแหน่งดาวเคราะห์ดวงที่เก้า มานานถึงเจ็ดสิบหกปี

### Scene 03 — Discovery of Eris
- **File**: `images/scene-03-discovery-eris.png`
- **Motion**: `slow_zoom_out` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Pluto floating alongside the newly discovered icy dwarf planet Eris in the Kuiper Belt, glowing faintly under distant sunlight.
- **Narration**: แต่เมื่อนักดาราศาสตร์พบวัตถุคล้าย Pluto เพิ่มขึ้น โดยเฉพาะ Eris คำถามก็เกิดขึ้นว่า แล้วอะไรควรถูกเรียกว่าดาวเคราะห์?
- **TTS Text**: แต่เมื่อนักดาราศาสตร์พบวัตถุคล้าย พลูโต เพิ่มขึ้น โดยเฉพาะ อีริส คำถามก็เกิดขึ้นว่า แล้วอะไรควรถูกเรียกว่าดาวเคราะห์?

### Scene 04 — Uncleared Orbit (IAU 2006 Rule)
- **File**: `images/scene-04-uncleared-orbit.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade_black`
- **Visual**: Wide-angle orbital diagram showing Pluto's inclined and eccentric orbit intersecting millions of icy Kuiper Belt asteroids and comets.
- **Narration**: ปี 2006 สหพันธ์ดาราศาสตร์สากลกำหนดว่า ดาวเคราะห์ต้องครองอิทธิพลเหนือบริเวณวงโคจรของตัวเอง แต่ Pluto ยังอยู่ร่วมกับวัตถุจำนวนมากใน Kuiper Belt
- **TTS Text**: ปีสองพันหก สหพันธ์ดาราศาสตร์สากลกำหนดว่า ดาวเคราะห์ต้องครองอิทธิพลเหนือบริเวณวงโคจรของตัวเอง แต่ พลูโต ยังอยู่ร่วมกับวัตถุจำนวนมากในแถบไคเปอร์

### Scene 05 — The 2006 Public Protest & Debate
- **File**: `images/scene-05-protest-2006.png`
- **Motion**: `gentle_float` (Intensity: `0.10`, Speed: `slow`)
- **Transition**: `smooth_right`
- **Visual**: Editorial 2006 campus and conference scene with passionate astronomy students and researchers holding signs supporting Pluto.
- **Narration**: แล้วคนประท้วงจริงไหม? จริงครับ มีทั้งการรวมตัว คำร้อง และนักวิทยาศาสตร์ที่คัดค้าน เพราะหลายคนผูกพันกับดาวเคราะห์ดวงเล็กนี้มาก
- **TTS Text**: แล้วคนประท้วงจริงไหม? จริงครับ มีทั้งการรวมตัว คำร้อง และนักวิทยาศาสตร์ที่คัดค้าน เพราะหลายคนผูกพันกับดาวเคราะห์ดวงเล็กนี้มาก

### Scene 06 — Pluto Unchanged
- **File**: `images/scene-06-pluto-unchanged.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Majestic close-up portrait of Pluto, untouched by human classifications, serenely rotating in deep space.
- **Narration**: แต่เดี๋ยวก่อน Pluto ไม่ได้เล็กลง ไม่ได้เปลี่ยนวงโคจร และไม่ได้สำคัญน้อยลง มนุษย์แค่เปลี่ยนวิธีจัดหมวดหมู่มันครับ
- **TTS Text**: แต่เดี๋ยวก่อน พลูโต ไม่ได้เล็กลง ไม่ได้เปลี่ยนวงโคจร และไม่ได้สำคัญน้อยลง มนุษย์แค่เปลี่ยนวิธีจัดหมวดหมู่มันครับ

### Scene 07 — New Horizons Flyby (2015)
- **File**: `images/scene-07-new-horizons-flyby.png`
- **Motion**: `pan_right_to_left` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: NASA New Horizons spacecraft soaring past Pluto, capturing the vast nitrogen ice sheet of Sputnik Planitia (the famous heart feature) and rugged ice mountains.
- **Narration**: และเมื่อ New Horizons บินผ่านในปี 2015 เราก็พบภูเขาน้ำแข็ง หมอกบรรยากาศสีฟ้า และธารน้ำแข็งไนโตรเจนรูปหัวใจขนาดมหึมา
- **TTS Text**: และเมื่อ นิว ฮอไรซันส์ บินผ่านในปีสองพันสิบห้า เราก็พบภูเขาน้ำแข็ง หมอกบรรยากาศสีฟ้า และธารน้ำแข็งไนโตรเจนรูปหัวใจขนาดมหึมา

### Scene 08 — Philosophical Payoff (Pluto & Charon)
- **File**: `images/scene-08-pluto-charon-payoff.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade`
- **Visual**: Pluto with its large moon Charon hovering in the background over glistening icy peaks, showing deep blue atmospheric haze under starry space.
- **Narration**: เพราะฉะนั้น Pluto อาจเสียตำแหน่งดาวเคราะห์ดวงที่ 9 แต่สิ่งที่เราค้นพบกลับทำให้มันน่าสนใจกว่าเดิมเสียอีก
- **TTS Text**: เพราะฉะนั้น พลูโต อาจเสียตำแหน่งดาวเคราะห์ดวงที่เก้า แต่สิ่งที่เราค้นพบกลับทำให้มันน่าสนใจกว่าเดิมเสียอีก

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
