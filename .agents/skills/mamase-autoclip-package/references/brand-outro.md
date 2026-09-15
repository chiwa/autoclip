# Mamase Brand Outro Specification

Every AutoClip package created for **Mamase — จักรวาลของใจ** must conclude with this canonical branding scene.

---

## 1. Scene Specification Table

| Attribute | Canonical Value | Notes |
| :--- | :--- | :--- |
| **Scene Position** | Final scene in `scenes` array | E.g. `scene-08` or `scene-09` |
| **Image Asset** | `images/<scene-id>.png` | Copy of canonical glowing cyan planet |
| **Narration** | Topic-specific discussion CTA (e.g. `ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?`) or `ค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ` | Strictly NO generic engagement lines ("กดไลก์", "กดแชร์", "คอมเมนต์คุยกัน", "ขอบคุณที่รับชม") |
| **TTS Text** | Phonetic override matching Narration | No spoken words after CTA |
| **Subtitle** | Clean matching subtitle | One to two lines |
| **Motion** | `slow_zoom_in` | Subtle cinematic zoom |
| **Motion Speed** | `slow` | Gentle movement |
| **Motion Intensity** | `0.1` | Controlled intensity |
| **Focus** | `center` | Centered focal point |
| **Transition** | `none` | Ignored on final scene |
| **Wan Plan** | `prompt`: "Mamase brand outro, glowing cyan orbiting planet in dark navy space, peaceful and contemplative." | `seed: 98`, `frames: 81`, `lip_sync: false` |

---

## 2. Canonical Source Image Asset

Copy the canonical outro PNG from the official branding folder:
- **Primary for Reels (9:16)**: `assets/branding/mamase/reels-end-scene.png` (Resized to 1080×1920 PNG into package `images/scene-09-mamase-outro.png`)
- **Alternative / Legacy planet**: `assets/tno-time-capsule-reel/images/scene-09-mamase-outro.png`

Do not modify or replace the visual branding asset without explicit user approval.
