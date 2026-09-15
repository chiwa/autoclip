# Mamase Reel Asset Manifest: ERIS — โลกที่บรรยากาศแข็งตัวตกลงบนพื้น

This document describes the visual assets, camera motions, transitions, narration, and technical specifications for the Mamase vertical short-form video package (`mamase-eris-reel-v1.zip`).

---

## 📦 Package Overview

- **Archive**: `dist/mamase-eris-reel-v1.zip`
- **Asset Directory**: `assets/eris_reel/`
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
- **Typography & Key Art**: Title "ERIS" in gold foil Chonburi font with ambient cyan glow, subtitle "โลกที่บรรยากาศ แข็งตัวตกลงบนพื้น" in creamy white with dark outline, badge box "“ผู้เปลี่ยนนิยามดาวเคราะห์”" in luminous deep blue, accompanied by Mamase presenter gesturing toward the glistening icy white dwarf planet Eris and its moon Dysnomia in deep space.
- **Wan 2.2**: 81 frames, 25 steps, `lip_sync: true`, `character_id: "mamase-presenter-v1"`.
- **Narration**: รู้ไหมครับว่า มีโลกใบหนึ่งที่หนาวจัด จนชั้นบรรยากาศของมัน... แข็งตัวและร่วงลงมาเคลือบพื้นผิวทั้งดวง?
- **TTS Text**: รู้ไหมครับว่า มีโลกใบหนึ่งที่หนาวจัด จนชั้นบรรยากาศของมัน... แข็งตัวและร่วงลงมาเคลือบพื้นผิวทั้งดวง?

### Scene 02 — The Planet Killer: Demoting Pluto
- **File**: `images/scene-02-planet-killer-pluto.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `smooth_left`
- **Visual**: Astronomical comparison in deep space: reddish-tan Pluto with Tombaugh Regio side-by-side with pure white glistening Eris of nearly identical size, evoking the 2006 IAU planet definition revolution.
- **Narration**: นี่คือ เอริส ดาวเคราะห์แคระที่ใหญ่เกือบเท่าพลูโต และเป็นต้นเหตุตัวจริง ที่ทำให้พลูโตถูกปลดออกจากการเป็นดาวเคราะห์ดวงที่เก้าในปี 2006
- **TTS Text**: นี่คือ เอ-ริส ดาวเคราะห์แคระที่ใหญ่เกือบเท่าพลูโต และเป็นต้นเหตุตัวจริง ที่ทำให้พลูโตถูกปลดออกจากการเป็นดาวเคราะห์ดวงที่เก้าในปี สองพันหก

### Scene 03 — Twin Sizes & Moon Dysnomia
- **File**: `images/scene-03-twin-sizes-dysnomia.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Close-up of dwarf planet Eris (radius 1,163 km) with crisp crystalline surface textures, orbited by its dark rocky moon Dysnomia, rotating once every 25.9 hours (virtually identical to an Earth day).
- **Narration**: เอริสมีรัศมีประมาณ 1,163 กิโลเมตร มีดวงจันทร์บริวารชื่อ ดิสนอเมีย และที่น่าทึ่งคือ มันหมุนรอบตัวเอง 25.9 ชั่วโมง หนึ่งวันของมันแทบจะยาวเท่ากับโลกเราเลยครับ
- **TTS Text**: เอ-ริส มีรัศมีประมาณ หนึ่งพันหนึ่งร้อยหกสิบสาม กิโลเมตร มีดวงจันทร์บริวารชื่อ ดิส-นอ-เมีย และที่น่าทึ่งคือ มันหมุนรอบตัวเอง ยี่สิบห้าจุดเก้า ชั่วโมง หนึ่งวันของมันแทบจะยาวเท่ากับโลกเราเลยครับ

### Scene 04 — The Cosmic Mirror Surface (96% Albedo)
- **File**: `images/scene-04-cosmic-mirror.png`
- **Motion**: `slow_zoom_in` (Intensity: `0.13`, Speed: `slow`)
- **Transition**: `fade_black`
- **Visual**: Surface landscape of Eris: an expanse of pristine nitrogen and methane ice crystals reflecting the distant pinpoint Sun with mirror-like brilliance (96% geometric albedo), far whiter than fresh Earth snow.
- **Narration**: แต่สิ่งที่ทำให้นักดาราศาสตร์ประหลาดใจที่สุด คือผิวนอกที่สว่างเหมือนกระจกเงา มันสะท้อนแสงแดดได้สูงถึง 96% ขาวบริสุทธิ์ยิ่งกว่าหิมะบนโลก
- **TTS Text**: แต่สิ่งที่ทำให้นักดาราศาสตร์ประหลาดใจที่สุด คือผิวนอกที่สว่างเหมือนกระจกเงา มันสะท้อนแสงแดดได้สูงถึง เก้าสิบหกเปอร์เซ็นต์ ขาวบริสุทธิ์ยิ่งกว่าหิมะบนโลก

### Scene 05 — Atmospheric Collapse: Nitrogen Snow
- **File**: `images/scene-05-atmospheric-collapse.png`
- **Motion**: `documentary_pan` (Intensity: `0.14`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Extreme cold (-243°C) atmospheric collapse: hazy violet-blue nitrogen and methane gas condensing into glittering frost flakes and snow that precipitate onto the ground, leaving vacuum above.
- **Narration**: นั่นเพราะตอนที่มันโคจรห่างไกลดวงอาทิตย์ อุณหภูมิติดลบกว่า 240 องศา จนก๊าซไนโตรเจนและมีเทนในอากาศ แข็งตัวและตกลงมาเคลือบพื้นดินจนกลายเป็นแผ่นน้ำแข็งขาวประกาย
- **TTS Text**: นั่นเพราะตอนที่มันโคจรห่างไกลดวงอาทิตย์ อุณหภูมิติดลบกว่า สองร้อยสี่สิบ องศา จนก๊าซไนโตรเจนและมีเทนในอากาศ แข็งตัวและตกลงมาเคลือบพื้นดินจนกลายเป็นแผ่นน้ำแข็งขาวประกาย

### Scene 06 — The Breathing World (557-Year Seasons)
- **File**: `images/scene-06-breathing-world-orbit.png`
- **Motion**: `slow_zoom_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `smooth_right`
- **Visual**: Highly eccentric elliptical orbit spanning 557 Earth years; as Eris journeys closer to perihelion near the Sun, sublimating nitrogen ice vapor rises to reform its seasonal atmosphere.
- **Narration**: เอริสใช้เวลาถึง 557 ปีในการโคจรรอบดวงอาทิตย์หนึ่งรอบ และเมื่อมันเข้าใกล้แดดในอีกหลายร้อยปีข้างหน้า น้ำแข็งจะระเหิดกลับเป็นบรรยากาศอีกครั้ง... โลกใบนี้จึง หายใจเปิดปิดบรรยากาศ ตามฤดูกาล
- **TTS Text**: เอ-ริส ใช้เวลาถึง ห้าร้อยห้าสิบเจ็ด ปีในการโคจรรอบดวงอาทิตย์หนึ่งรอบ และเมื่อมันเข้าใกล้แดดในอีกหลายร้อยปีข้างหน้า น้ำแข็งจะระเหิดกลับเป็นบรรยากาศอีกครั้ง... โลกใบนี้จึง หายใจเปิดปิดบรรยากาศ ตามฤดูกาล

### Scene 07 — The Unreached Frontier (Ground-Based Science)
- **File**: `images/scene-07-unreached-observatory.png`
- **Motion**: `cinematic_push_in` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `dissolve`
- **Visual**: Authentic ESO Very Large Telescope (VLT) atop Cerro Paranal under the brilliant starry skies of the Atacama Desert, firing its golden laser guide star beam into the cosmos to observe distant stellar occultations.
- **Narration**: และจนถึงวันนี้ มนุษย์ยังไม่เคยส่งยานอวกาศลำไหนไปสำรวจเอริสเลยครับ ภาพทั้งหมดที่เรามี เกิดจากการส่องกล้องโทรทรรศน์ และการคำนวณจากระยะไกลหลายพันล้านกิโลเมตรเท่านั้น
- **TTS Text**: และจนถึงวันนี้ มนุษย์ยังไม่เคยส่งยานอวกาศลำไหนไปสำรวจ เอ-ริส เลยครับ ภาพทั้งหมดที่เรามี เกิดจากการส่องกล้องโทรทรรศน์ และการคำนวณจากระยะไกลหลายพันล้านกิโลเมตรเท่านั้น

### Scene 08 — Mamase Frontier Payoff: Untouched Power
- **File**: `images/scene-08-mamase-frontier-payoff.png`
- **Motion**: `cinematic_pull_out` (Intensity: `0.15`, Speed: `slow`)
- **Transition**: `fade`
- **Visual**: Official ESO scientific master portrait of dwarf planet Eris floating as a solitary white diamond against the quiet darkness of the outer solar system and distant stars.
- **Narration**: โลกที่มนุษย์ยังไม่เคยไปสัมผัส... แต่กลับทรงพลังพอที่จะเปลี่ยนตำราดาราศาสตร์ของโลกเราไปตลอดกาลครับ
- **TTS Text**: โลกที่มนุษย์ยังไม่เคยไปสัมผัส... แต่กลับทรงพลังพอที่จะเปลี่ยนตำราดาราศาสตร์ของโลกเราไปตลอดกาลครับ

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

- **ZIP integrity**: Passed (`unzip -t dist/mamase-eris-reel-v1.zip`)
- **Dimensions**: All 9 images strictly 1080×1920 8-bit RGB PNG
- **Branding**: Official Mamase circular logo (205×205px) placed at top-right (x: 839, y: 36) with soft shadow on Scenes 01–08; Scene 09 locked outro clean
- **Text discipline**: Scenes 02–08 completely free of baked-in labels and text overlays
- **Contract compliance**: `PackageService.extract_and_validate` passed 100%
