# Asset Manifest: TON 618 — หลุมดำที่ใหญ่เกินกว่าสมองมนุษย์จะจินตนาการ!

- **Package**: `dist/mamase-ton-618-black-hole-reel-v1.zip`
- **Asset Directory**: `assets/ton_618_ultramassive_black_hole_reel/`
- **Topic**: TON 618 Ultramassive Black Hole (66 billion solar masses, 390 billion km event horizon). Comparing familiar scales from Sun to Sagittarius A*, the sheer size swallowing our solar system, the blinding quasar brighter than 140 trillion suns, and the philosophical wonder of human curiosity.
- **Presenter**: Standard Mamase warm Thai presenter (Scene 01 bottom-right, grounded ~55% height, color-graded to TON 618 golden accretion disk lighting).
- **Branding**: Official circular Mamase Logo crowned at top-center.
- **Typography Standard**: Chonburi font with 3-stage gold foil gradient, motion-safe margins (`y >= 215px`, `x >= 150px`).
- **Aspect Ratio**: 9:16 vertical (1080×1920 PNG, 30 FPS).
- **TTS Voice**: Google Gemini `Fenrir` (`speed: 1.0`, full phonetic Thai script).

---

## Scene Inventory & Shot List

| Scene | File | Focus / Motion | Transition | Narration Summary |
|---|---|---|---|---|
| **01** | `images/scene-01-hook.png` | `cinematic_push_in` (0.12) | `fade` | หลุมดำที่ใหญ่ที่สุดในจักรวาล หนักเท่าดวงอาทิตย์ 6.6 หมื่นล้านดวง |
| **02** | `images/scene-02-familiar-scale.png` | `slow_zoom_in` (0.15) | `dissolve` | ดวงอาทิตย์หนักกว่าโลก 3.3 แสนเท่า และหลุมดำทั่วไปหนักสิบเท่าดวงอาทิตย์ |
| **03** | `images/scene-03-sagittarius-a.png` | `cinematic_push_in` (0.16) | `dissolve` | หลุมดำใจกลางทางช้างเผือก Sagittarius A* หนัก 4 ล้านเท่าของดวงอาทิตย์ |
| **04** | `images/scene-04-monster-ton618.png` | `slow_zoom_in` (0.16) | `dissolve` | TON 618 อภิมหาหลุมดำ Ultramassive หนัก 66,000 ล้านเท่าของดวงอาทิตย์ |
| **05** | `images/scene-05-swallowing-solar-system.png` | `cinematic_pull_out` (0.16) | `dissolve` | ขอบฟ้าเหตุการณ์กว้าง 4 แสนล้านกิโลเมตร กลืนระบบสุริยะทั้งหมดลงไปได้ |
| **06** | `images/scene-06-blinding-quasar.png` | `cinematic_push_in` (0.18) | `dissolve` | จานสะสมมวลสารหมุนเร็วใกล้แสง สว่างกว่าทางช้างเผือกทั้งกาแล็กซีร้อยเท่า |
| **07** | `images/scene-07-cosmic-time-machine.png` | `slow_zoom_in` (0.15) | `dissolve` | แสงเดินทางข้ามอวกาศ 1 หมื่นล้านปี ย้อนกลับไปตั้งแต่จักรวาลเพิ่งเริ่มต้น |
| **08** | `images/scene-08-philosophical-insight.png` | `cinematic_pull_out` (0.15) | `fade` | ยิ่งจักรวาลกว้างใหญ่ ยิ่งตระหนักถึงความมหัศจรรย์ของใจมนุษย์ |
| **09** | `images/scene-09-mamase-outro.png` | `slow_zoom_in` (0.10) | `none` | ภาพปิดทางการ Mamase Reels (`assets/branding/mamase/reels-end-scene.png`) |

---

## Validation & Compliance Check
- [x] **Pydantic Validation**: `Script.model_validate()` passed with 0 errors.
- [x] **Motion Preset Safety**: Strictly supported presets (`cinematic_push_in`, `slow_zoom_in`, `cinematic_pull_out`).
- [x] **Zero Text Violations**: Scenes 02–08 have 0 in-image text/logos/HUDs.
- [x] **Motion-Safe Margins**: Scene 01 title, logo, and hook are clear of top/side clipping zones.
- [x] **Outro Compliance**: Canonical Mamase glowing cyan planet outro with complete call-to-action.
