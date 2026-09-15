# Asset Manifest: ถ้าดาว ‘บีเทลจุส’ ระเบิดคืนนี้? จะเกิดอะไรขึ้นกับโลกของเรา!

- **Package**: `dist/mamase-betelgeuse-supernova-reel-v1.zip`
- **Asset Directory**: `assets/betelgeuse_supernova_reel/`
- **Topic**: Betelgeuse Supernova — What happens if the red supergiant in Orion explodes tonight? Explaining supernova physics, Earth's visual impact, safe distance (640 ly), cosmic forge of elements, and the poetic link between dying stars and human existence ("We are stardust").
- **Presenter**: Standard Mamase warm Thai presenter (Scene 01 bottom-right, grounded ~55% height, color-graded to Betelgeuse warm orange-red lighting).
- **Typography Standard**: Chonburi font with 3-stage gold foil gradient, motion-safe margins (`y >= 215px`, `x >= 150px`).
- **Aspect Ratio**: 9:16 vertical (1080×1920 PNG, 30 FPS).
- **TTS Voice**: Google Gemini `Fenrir` (`speed: 1.0`, full phonetic Thai script).

---

## Scene Inventory & Shot List

| Scene | File | Focus / Motion | Transition | Narration Summary |
|---|---|---|---|---|
| **01** | `images/scene-01-hook.png` | `cinematic_push_in` (0.12) | `fade` | ถ้าบีเทลจุสระเบิดเป็นซูเปอร์โนวาคืนนี้ จะเกิดอะไรขึ้นกับโลก? |
| **02** | `images/scene-02-dying-giant.png` | `slow_zoom_in` (0.15) | `dissolve` | ดาวยักษ์แดงใหญ่กว่าดวงอาทิตย์ 700 เท่า กำลังเผาผลาญเชื้อเพลิงช่วงท้ายชีวิต |
| **03** | `images/scene-03-supernova-explosion.png` | `cinematic_push_in` (0.18) | `dissolve` | แกนกลางยุบตัว ระเบิดซูเปอร์โนวาสว่างเท่าดาวฤกษ์หลายพันล้านดวง |
| **04** | `images/scene-04-two-moons-night-sky.png` | `pan_right_to_left` (0.15) | `dissolve` | แสงสว่างจ้าเท่าพระจันทร์เต็มดวง ส่องเห็นเงายามค่ำคืนและเห็นได้ตอนกลางวัน |
| **05** | `images/scene-05-safe-distance.png` | `slow_zoom_in` (0.15) | `dissolve` | อยู่ห่างออกไป 640 ปีแสง ปลอดภัยเกินกว่าที่รังสีจะทำลายโลก |
| **06** | `images/scene-06-cosmic-forge.png` | `cinematic_push_in` (0.16) | `dissolve` | เตาหลอมจักรวาลที่พ่นธาตุ เหล็ก คาร์บอน ออกซิเจน กระจายสู่อวกาศ |
| **07** | `images/scene-07-we-are-stardust.png` | `slow_zoom_in` (0.15) | `dissolve` | ธาตุเหล่านี้จะกลายเป็นดาวเคราะห์ดวงใหม่ และร่างกายของพวกเราทุกคน |
| **08** | `images/scene-08-philosophical-insight.png` | `cinematic_pull_out` (0.15) | `fade` | เราไม่ได้แค่เกิดในจักรวาล แต่เราคือจักรวาลที่กำลังมองดูตัวเอง |
| **09** | `images/scene-09-mamase-outro.png` | `slow_zoom_in` (0.10) | `none` | ชวนกดไลก์ กดแชร์ กดติดตาม และ Mamase จักรวาลของใจ |

---

## Validation & Compliance Check
- [x] **Pydantic Validation**: `Script.model_validate()` passed with 0 errors.
- [x] **Motion Preset Safety**: Strictly supported presets (`cinematic_push_in`, `slow_zoom_in`, `pan_right_to_left`, `cinematic_pull_out`).
- [x] **Zero Text Violations**: Scenes 02–08 have 0 in-image text/logos/HUDs.
- [x] **Motion-Safe Margins**: Scene 01 title and hook are clear of top/side clipping zones.
- [x] **Outro Compliance**: Canonical Mamase glowing cyan planet outro with complete call-to-action.
