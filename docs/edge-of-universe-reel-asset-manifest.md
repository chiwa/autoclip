# Asset Manifest: ถ้าจักรวาลมีขอบ…ข้างนอกนั้นคืออะไร? (Mamase — จักรวาลของใจ)

- **Package**: `dist/mamase-edge-of-universe-reel-v1.zip`
- **Asset Directory**: `assets/edge_of_universe_reel/`
- **Topic**: What lies beyond the edge of the universe? Comparing the Observable Universe (a 46.5-billion-light-year spherical bubble bounded by the speed of light) with the Entire Universe (which could be hundreds of times larger or truly infinite with no center and no boundary). Exploring the "Wow moment" that every observer is at the center of their own cosmic bubble, the accelerating expansion of space, and the philosophical Mamase conclusion: "สิ่งที่มีขอบ... อาจไม่ใช่จักรวาล แต่คือสิ่งที่เรามองเห็นต่างหาก".
- **Presenter**: Standard Mamase warm Thai presenter (Scene 01 bottom-right, grounded ~55% height, color-graded to ambient cyan cosmic lighting).
- **Branding**: Official circular Mamase Logo crowned at top-center.
- **Outro Asset**: Canonical `assets/branding/mamase/reels-end-scene.png` resized to 1080×1920 PNG.
- **Typography Standard**: Chonburi font with 3-stage gold foil gradient, motion-safe margins (`y >= 215px`, `x >= 150px`).
- **Aspect Ratio**: 9:16 vertical (1080×1920 PNG, 30 FPS).
- **TTS Voice**: Google Gemini `Fenrir` (`speed: 1.0`, full phonetic Thai script).

---

## Scene Inventory & Shot List

| Scene | File | Focus / Motion | Transition | Narration Summary |
|---|---|---|---|---|
| **01** | `images/scene-01-hook.png` | `cinematic_push_in` (0.12) | `fade` | ถ้าเราบินตรงไปจนถึงขอบจักรวาล เราจะเจออะไร? กำแพง? ความว่างเปล่า? หรือไม่มีขอบเลย |
| **02** | `images/scene-02-cosmic-horizon.png` | `slow_zoom_in` (0.15) | `dissolve` | สิ่งที่เรียกว่าขอบจักรวาลที่สังเกตได้ ไม่ใช่กำแพงทึบ แต่คือระยะทางสูงสุดที่แสงเดินทางมาถึงเรา |
| **03** | `images/scene-03-46-billion-ly.png` | `cinematic_push_in` (0.16) | `dissolve` | รัศมีราว 46,500 ล้านปีแสง สิ่งที่อยู่พ้นไป แสงยังเดินทางมาไม่ถึงโลก |
| **04** | `images/scene-04-infinite-universe.png` | `cinematic_pull_out` (0.15) | `dissolve` | จักรวาลทั้งหมดจริง ๆ อาจใหญ่กว่าฟองที่เรามองเห็นมหาศาล หรือแผ่ขยายเป็นอนันต์ไร้ขอบเขต |
| **05** | `images/scene-05-flying-across-edge.png` | `documentary_pan` (0.14) | `dissolve` | ถ้าไปยืนตรงขอบนั้นจริง ๆ จะไม่เจอกำแพงอะไรเลย แต่จะเห็นดวงดาวและอวกาศทอดยาวต่อไปตามปกติ |
| **06** | `images/scene-06-observer-centers.png` | `slow_zoom_in` (0.15) | `dissolve` | ไม่ว่าคุณจะอยู่ที่กาแล็กซีไหน คุณมีฟองจักรวาลที่สังเกตได้ล้อมรอบตัวคุณเองเสมอ โดยมีคุณเป็นศูนย์กลาง |
| **07** | `images/scene-07-expanding-spacetime.png` | `cinematic_push_in` (0.16) | `dissolve` | อวกาศกำลังขยายตัวเร็วขึ้นเรื่อย ๆ จนแสงจากดินแดนที่ไกลเกินไปจะไม่มีวันมาถึงเราได้ตลอดกาล |
| **08** | `images/scene-08-philosophical-climax.png` | `slow_zoom_in` (0.12) | `fade` | คำถามว่านอกจักรวาลมีอะไร อาจเริ่มจากความเข้าใจผิด เพราะสิ่งที่มีขอบ... อาจไม่ใช่จักรวาล แต่คือสิ่งที่เรามองเห็นต่างหาก |
| **09** | `images/scene-09-mamase-outro.png` | `slow_zoom_in` (0.05) | `none` | Canonical Mamase Outro (`reels-end-scene.png`) กดไลก์ กดแชร์ กดติดตาม |

---

## Validation Status
- `unzip -t`: PASS
- `PackageService.extract_and_validate`: PASS 100%
- Pydantic Schema: PASS (100% compliant)
- All Image Resolutions: Strictly 1080×1920 PNG, 8-bit RGB
- Total Package Size: ~26.05 MB
