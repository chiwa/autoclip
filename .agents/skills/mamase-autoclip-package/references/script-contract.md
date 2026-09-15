# Script JSON & Metadata Contract

This reference details the exact JSON schema and technical requirements for `script.json` and `video-metadata.json` in every AutoClip package.

---

## 1. File Placement & Relative Paths

- `script.json` **MUST** exist at the root of the ZIP archive.
- `video-metadata.json` **MUST** exist at the root of the ZIP archive.
- All asset paths in `image` and `audio` must be relative POSIX paths (e.g. `images/scene-01-hook.png`).
- Absolute paths (`/Users/...`) and directory traversal (`../`) are strictly rejected.

---

## 2. Schema Specification: `script.json`

```json
{
  "project": {
    "id": "mamase-<topic-slug>-reel-v1",
    "title": "Title of the Video",
    "language": "th-TH",
    "resolution": "1080x1920",
    "fps": 30
  },
  "voice": {
    "provider": "google-gemini",
    "voice": "Fenrir",
    "speed": 1.05,
    "style_prompt": "Read aloud in a natural, playful, conversational Thai voice..."
  },
  "scenes": [
    {
      "id": "scene-01-hook",
      "image": "images/scene-01-hook.png",
      "narration": "ข้อความบรรยายที่แสดงบนหน้าจอ",
      "tts_text": "ข้อความคำอ่านภาษาไทยตามเสียงพูดจริงโดยไม่มีจุดไข่ปลา",
      "subtitle": "ข้อความซับไตเติลสั้นกระชับ",
      "motion": "cinematic_push_in",
      "motion_speed": "normal",
      "motion_intensity": 0.2,
      "focus": "right",
      "transition": "dissolve",
      "wan": {
        "prompt": "Detailed AI video generation prompt preserving presenter identity...",
        "negative_prompt": "extra person, watermark, distorted hands, flicker, jitter",
        "seed": 901,
        "frames": 81,
        "steps": 25,
        "lip_sync": true,
        "character_id": "mamase-presenter-v1"
      }
    }
  ]
}
```

---

## 3. Motion & Transition Enumerations

### Motion Types (`motion`)
- `slow_zoom_in`: Smooth cinematic forward zoom into the focal center.
- `cinematic_push_in`: Energetic push into the subject, ideal for opening hooks.
- `cinematic_pull_out`: Pull back to reveal vast scale or surroundings.
- `gentle_float`: Subtle organic drift, great for micro-gravity or space objects.
- `documentary_pan`: Smooth horizontal pan across a landscape or hardware.
- `slow_zoom_out`: Contemplative zoom out, ideal for endings and reveals.

### Focus Alignments (`focus`)
- `center`: Default centered focal point.
- `right`: Ideal for Scene 01 when the presenter is positioned on the right.
- `left`: Ideal when the primary subject is on the left edge.
- `top` / `bottom`: Focus on upper or lower third.

### Transition Types (`transition`)
- `fade`: Safe, clean fade through black (standard documentary default).
- `dissolve`: Smooth cross-fade between scenes.
- `none`: Hard cut (used for the final scene / outro).

---

## 4. Wan 2.2 Parameters
- **Sampling Budget (`steps`)**:
  - Scene 01 (Hook): Must explicitly specify `"steps": 25`.
  - Scenes 02+: Omit `steps` (inherits server default of 22 steps).
- **Frame Count (`frames`)**:
  - Default: `81` frames (~5.06s at 16 fps).
  - Derived from audio duration: Wan renderer automatically extends frame count using `4k + 1` formula if narration exceeds 5 seconds.
- **Lip Sync (`lip_sync`)**:
  - Scene 01: `true` (declares F5 + LatentSync intent for presenter).
  - Other scenes: `false`.
- **Character Identifier (`character_id`)**:
  - Scene 01: `"mamase-presenter-v1"`.

---

## 5. Schema Specification: `video-metadata.json`

```json
{
  "title": "Title of the Video in Thai with Hook Keyword",
  "description": "Engaging description summarizing the core mystery or discovery.\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#Hashtag1 #Hashtag2 #Mamase #จักรวาลของใจ"
}
```
