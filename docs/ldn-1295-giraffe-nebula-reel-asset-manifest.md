# Asset Manifest: LDN 1295 — The Giraffe Nebula (เนบิวลายีราฟยักษ์แห่งกลุ่มดาวแคสซิโอเปีย)

- **Package**: `dist/mamase-ldn-1295-giraffe-nebula-reel-v1.zip`
- **Asset Directory**: `assets/ldn_1295_giraffe_nebula_reel/`
- **Topic**: NASA APOD (10 Sep 2026) by Alessandro Merga — LDN 1295 dark nebula in Cassiopeia. Exploring the silhouette of interstellar cold dust resembling a giraffe, Beverly Lynds' 1962 Dark Nebula Catalogue, the evolutionary psychology of pareidolia, microscopic dust chemistry at -250°C, infrared observation piercing the dust veil, and star birth nurseries inside cosmic darkness ("ความมืดมิดไม่ใช่จุดจบ แต่คือครรภ์มารดาที่ฟูมฟักแสงสว่าง").
- **Presenter**: Standard Mamase warm Thai presenter (Scene 01 bottom-right, grounded ~55% height, color-graded to warm dusty amber lighting).
- **Branding**: Official circular Mamase Logo crowned at top-center.
- **Outro Asset**: Canonical `assets/branding/mamase/reels-end-scene.png` resized to 1080×1920 PNG.
- **Typography Standard**: Chonburi font with 3-stage gold foil gradient, motion-safe margins (`y >= 215px`, `x >= 150px`).
- **Aspect Ratio**: 9:16 vertical (1080×1920 PNG, 30 FPS).
- **TTS Voice**: Google Gemini `Fenrir` (`speed: 1.0`, full phonetic Thai script).

---

## Scene Inventory & Shot List

| Scene | File | Focus / Motion | Transition | Narration Summary |
|---|---|---|---|---|
| **01** | `images/scene-01-hook.png` | `cinematic_push_in` (0.12) | `fade` | ยีราฟยักษ์โผล่กลางอวกาศ? ภาพล่าสุดจาก NASA APOD บันทึกเงาดำลึกลับ |
| **02** | `images/scene-02-dark-silhouette.png` | `slow_zoom_in` (0.15) | `dissolve` | LDN 1295 เนบิวลายีราฟ ในกลุ่มดาวแคสซิโอเปีย บดบังแสงดาวเบื้องหลัง |
| **03** | `images/scene-03-beverly-lynds-catalog.png` | `documentary_pan` (0.14) | `dissolve` | บันทึกในแคตตาล็อกเนบิวลามืด โดย Beverly Lynds นักดาราศาสตร์หญิงในตำนานปี 1962 |
| **04** | `images/scene-04-pareidolia-pattern.png` | `slow_zoom_in` (0.15) | `dissolve` | ทำไมสมองเราถึงเห็นเป็นสัตว์? ปรากฏการณ์แพริโดเลีย สัญชาตญาณเอาตัวรอดของมนุษย์ |
| **05** | `images/scene-05-cold-molecular-dust.png` | `cinematic_push_in` (0.16) | `dissolve` | แท้จริงไม่ใช่ความว่างเปล่า แต่คือกลุ่มฝุ่นคอสมิกและก๊าซโมเลกุลหนาทึบ -250°C |
| **06** | `images/scene-06-infrared-penetration.png` | `cinematic_push_in` (0.15) | `dissolve` | ส่องอินฟราเรดทะลุม่านฝุ่นมืด (JWST L1527) พบแกนดาวเกิดใหม่ซ่อนอยู่ข้างใน |
| **07** | `images/scene-07-star-nursery.png` | `cinematic_push_in` (0.16) | `dissolve` | แรงโน้มถ่วงบีบอัดก๊าซ จุดฟิวชันกำเนิดดวงอาทิตย์ใหม่และเจ็ตความเร็วเหนือเสียง (JWST HH 211) |
| **08** | `images/scene-08-philosophical-climax.png` | `cinematic_pull_out` (0.15) | `fade` | ความมืดมิดไม่ใช่ความว่างเปล่า แต่คือครรภ์มารดาที่กำลังฟูมฟักแสงสว่างให้กับเอกภพ |
| **09** | `images/scene-09-mamase-outro.png` | `slow_zoom_in` (0.05) | `none` | Canonical Mamase Outro (`reels-end-scene.png`) กดไลก์ กดแชร์ กดติดตาม |

---

## Validation Status
- `unzip -t`: PASS
- `PackageService.extract_and_validate`: PASS
- Pydantic Schema: PASS (100% compliant)
- All Image Resolutions: Strictly 1080×1920 PNG, 8-bit RGB
- Total Package Size: ~24.1 MB
