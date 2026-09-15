# Asset Manifest: Hubble + Webb พบ ‘Time Capsule’ ระบบสุริยะ 4.5 พันล้านปี

- **Package**: `dist/mamase-tno-time-capsule-reel-v1.zip`
- **Asset Directory**: `assets/tno-time-capsule-reel/`
- **Topic**: NASA breaking news — Hubble and James Webb Space Telescope survey of >75 Trans-Neptunian Objects (TNOs) revealing primordial chemical composition preserved for 4.5 billion years.
- **Presenter**: Standard Mamase warm Thai presenter (Scene 01 bottom-right, grounded 55–58% height, color-graded to deep cosmic lighting).
- **Typography Standard**: Chonburi font with 3-stage gold foil gradient, motion-safe margins (`y: 200–220px`, `x: 150px`).
- **Aspect Ratio**: 9:16 vertical (1080×1920 PNG, 30 FPS).
- **TTS Voice**: Google Gemini `Fenrir` (`speed: 1.0`, full phonetic Thai script).

---

## Scene Inventory & Shot List

| Scene | File | Focus / Motion | Transition | Narration Summary |
|---|---|---|---|---|
| **01** | `images/scene-01-hook.png` | `cinematic_push_in` (0.12) | `fade` | Hubble + Webb ร่วมมือครั้งแรก พบ Time Capsule ระบบสุริยะ 4.5 พันล้านปี |
| **02** | `images/scene-02-frozen-frontier.png` | `slow_zoom_in` (0.15) | `dissolve` | วัตถุ Trans-Neptunian (TNOs) ก้อนน้ำแข็งและหินพ้นดาวเนปจูน |
| **03** | `images/scene-03-absolute-zero.png` | `cinematic_push_in` (0.16) | `dissolve` | ความหนาวเหน็บใกล้ศูนย์สัมบูรณ์ สภาพเคมีไม่เปลี่ยน 4.5 พันล้านปี |
| **04** | `images/scene-04-hubble-webb-collaboration.png` | `documentary_pan` (0.15) | `dissolve` | ผสานพลังสายตา Hubble + เซนเซอร์อินฟราเรด James Webb สำรวจเป็นระบบ |
| **05** | `images/scene-05-75-spectra-analysis.png` | `slow_zoom_in` (0.16) | `dissolve` | Webb เก็บสเปกตรัม TNOs กว่า 75 ดวง พบสารอินทรีย์และโมเลกุลตั้งต้น |
| **06** | `images/scene-06-solar-system-birth.png` | `cinematic_push_in` (0.18) | `dissolve` | วัตถุดิบตั้งต้นชุดแรกที่หมุนวนรอบดวงอาทิตย์ก่อนกำเนิดดาวเคราะห์ |
| **07** | `images/scene-07-planetary-migration.png` | `cinematic_pull_out` (0.16) | `dissolve` | จำลองการเคลื่อนย้ายดาวเคราะห์ยักษ์ที่ผลักวัตถุโบราณสู่ขอบสุริยะ |
| **08** | `images/scene-08-understanding-our-roots.png` | `slow_zoom_in` (0.15) | `fade` | การมองขอบนอกอันมืดมิดเพื่อทำความเข้าใจจุดเริ่มต้นของพวกเรา |
| **09** | `images/scene-09-mamase-outro.png` | `slow_zoom_in` (0.10) | `none` | ชวนกดไลก์ กดแชร์ กดติดตาม และ Mamase จักรวาลของใจ |

---

## Validation & Compliance Check
- [x] **Pydantic Validation**: `Script.model_validate()` passed with 0 errors.
- [x] **Motion Preset Safety**: No unsupported strings (strictly `cinematic_push_in`, `slow_zoom_in`, `documentary_pan`, `cinematic_pull_out`).
- [x] **Zero Text Violations**: Scenes 02–08 have 0 in-image text/logos/HUDs.
- [x] **Motion-Safe Margins**: Scene 01 title and hook are clear of top/side clipping zones.
- [x] **Outro Compliance**: Canonical Mamase glowing cyan planet outro with complete call-to-action.
