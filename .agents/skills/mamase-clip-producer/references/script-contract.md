# Script JSON & ZIP Contract Reference

## Canonical Benchmark Package
The reference template for production packages is `/dist/mamase-roman-space-telescope-wan-v2.zip`.

## 1. `video-metadata.json` Specification
Required at ZIP root for title, description, and hashtags:
```json
{
  "title": "Roman Space Telescope: กว้างกว่า Hubble 100 เท่า",
  "description": "Roman Space Telescope ออกเดินทางแล้ว เพื่อสำรวจ dark energy, โครงสร้างขนาดใหญ่ของจักรวาล และดาวเคราะห์นอกระบบด้วยมุมมองที่กว้างกว่า Hubble อย่างน้อย 100 เท่า\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#RomanSpaceTelescope #NASA #อวกาศ #DarkEnergy #วิทยาศาสตร์ #Mamase"
}
```

---

## 2. Schema Definition (`script.json`)

```json
{
  "project": {
    "id": "mamase-roman-space-telescope-v1",
    "title": "Roman Space Telescope: กว้างกว่า Hubble 100 เท่า",
    "language": "th-TH",
    "resolution": "1080x1920",
    "fps": 30
  },
  "voice": {
    "provider": "local",
    "voice": "thai-male-01",
    "speed": 0.96
  },
  "scenes": [
    {
      "id": "scene-01-hook",
      "image": "images/scene-01-hook.png",
      "narration": "กล้องตัวนี้มองท้องฟ้าได้กว้างกว่า Hubble อย่างน้อยร้อยเท่า… และมันเพิ่งออกเดินทางเพื่อไขความลับที่ใหญ่ที่สุดของจักรวาล",
      "subtitle": "กว้างกว่า Hubble 100 เท่า",
      "motion": "cinematic_push_in",
      "motion_speed": "normal",
      "motion_intensity": 0.2,
      "focus": "center",
      "transition": "fade",
      "wan": {
        "prompt": "Use the canonical Mamase anime presenter identity, friendly Thai male with tousled black hair, thin rectangular glasses and navy blazer, face-forward on the right for a talking shot. Premium science-book-cover composition: Nancy Grace Roman Space Telescope above Earth, vast blue-purple cosmos, elegant Thai title กว้างกว่า Hubble 100 เท่า in upper left. Scientifically grounded, no alien, no misleading claims.",
        "negative_prompt": "extra person, extra text, watermark, logo, alien, distorted face, distorted hands, blurry telescope",
        "seed": 326,
        "frames": 81,
        "steps": 25,
        "lip_sync": true,
        "character_id": "mamase-presenter-v1"
      }
    }
  ]
}
```

## Fields Specification

### Project Object (`project`)
| Field | Type | Requirement | Description / Notes |
| :--- | :--- | :--- | :--- |
| `id` | string | **Required** | Filesystem-safe project identifier (e.g. `mamase-roman-space-telescope-v1`) |
| `title` | string | **Required** | Human-readable title for display |
| `language` | string | **Required** | Locale code (e.g. `th-TH`) |
| `resolution` | string | Optional | `WIDTHxHEIGHT`, defaults to `1080x1920` |
| `fps` | number | Optional | Positive integer frame rate (defaults to `30`) |

### Voice Object (`voice`)
| Field | Type | Requirement | Description / Notes |
| :--- | :--- | :--- | :--- |
| `provider` | string | **Required** | TTS Provider: `local` (VachanaTTS2 ONNX) or `runpod` (F5-TTS-THAI V2) |
| `voice` | string | **Required** | Voice identifier: `thai-male-01`, `thai-male-02`, etc. |
| `speed` | number | **Required** | Narration speed multiplier (e.g. `0.96` to `1.0`) |

### Scene Object (`scenes[]`)
| Field | Type | Requirement | Description / Notes |
| :--- | :--- | :--- | :--- |
| `id` | string | **Required** | Unique scene ID (e.g. `scene-01-hook`, `scene-02-launch`) |
| `image` | string | **Required** | Relative path to image (e.g. `images/scene-01-hook.png`) |
| `narration` | string | **Required** | Thai narration text in UTF-8 for TTS |
| `tts_text` | string | Optional | Phonetic Thai pronunciation override for TTS (e.g. for loanwords like นาซา, ดาร์ก เอนเนอร์จี) |
| `subtitle` | string / boolean | Optional | Subtitle display text. Use `\n` for line breaks. Set to `false` or `"none"` to disable |
| `show_subtitle` | boolean | Optional | `true` (default) or `false` |
| `motion` | string | **Required** | Camera motion preset (e.g. `cinematic_push_in`, `documentary_pan`, `slow_zoom_in`) |
| `motion_speed` | string | Optional | `slow` (default), `normal`, `fast` |
| `motion_intensity`| number | Optional | Decimal float between `0.01` and `0.35` (e.g. `0.14`, `0.2`) |
| `focus` | string | Optional | Focus point: `center` (default), `bottom`, `top`, `left`, `right` |
| `transition` | string | Optional | Transition to next scene; default `fade`. Ignored on final scene |
| `wan` | object | Optional | Optional Wan 2.2 generative video hints (see Wan Options below) |

### Wan Options Object (`wan`)
| Field | Type | Requirement | Description / Notes |
| :--- | :--- | :--- | :--- |
| `prompt` | string | **Required** | Visual and motion description for ComfyUI Wan 2.2 |
| `negative_prompt` | string | Optional | Negative prompt (defaults to text, watermark, jitter) |
| `seed` | integer | Optional | Random seed for deterministic generation |
| `frames` | integer | Optional | Frame count (default `81`, approx 5.06 sec at 16 fps) |
| `steps` | integer | Optional | Sampling steps (`25` for scene 1 hook, omitted or 22 for others) |
| `lip_sync` | boolean | Optional | `true` for presenter talking head, `false` for b-roll |
| `character_id` | string | Optional | Registered character identifier (e.g. `mamase-presenter-v1`) |


---

## Supported Motion Presets

| Motion Preset | Behavior / Description |
| :--- | :--- |
| `none` | No camera motion |
| `slow_zoom_in` | Subtle cinematic zoom in (Recommended for hook/outro) |
| `slow_zoom_out` | Subtle cinematic zoom out (Recommended for reveals/endings) |
| `pan_left_to_right` | Horizontal pan left to right |
| `pan_right_to_left` | Horizontal pan right to left |
| `pan_up` | Vertical pan upward |
| `pan_down` | Vertical pan downward |

---

## Supported Transitions

### Recommended & Standard
- `fade`: Smooth crossfade (Default)
- `dissolve`: Soft dissolve
- `smooth_left`, `smooth_right`, `smooth_up`, `smooth_down`: Soft directional movements
- `fade_black`: Crossfade through black (Ideal before/after outro)
- `fade_white`: Crossfade through white (Flash reveal)

### Additional Supported
- **Fade variants**: `fade_slow`, `fade_fast`, `fade_grays`
- **Directional slides**: `slide_left`, `slide_right`, `slide_up`, `slide_down`
- **Directional wipes**: `wipe_left`, `wipe_right`, `wipe_up`, `wipe_down`, `wipe_top_left`, `wipe_top_right`, `wipe_bottom_left`, `wipe_bottom_right`
- **Shape wipes**: `circle_open`, `circle_close`, `circle_crop`, `rect_crop`, `vertical_open`, `vertical_close`, `horizontal_open`, `horizontal_close`
- **Special / Stylistic** *(Use sparingly)*: `zoom_in`, `pixelize`, `radial`, `horizontal_blur`, `distance`, `squeeze_horizontal`, `squeeze_vertical`, `diagonal_top_left`, `diagonal_top_right`, `diagonal_bottom_left`, `diagonal_bottom_right`, `horizontal_slice_left`, `horizontal_slice_right`, `vertical_slice_up`, `vertical_slice_down`
- `none`: Hard cut

---

## Critical Rules
1. **No manual durations**: Duration is automatically computed from TTS audio length.
2. **Relative paths only**: No `/` root prefixes or `../` directory traversal.
3. **Authoritative order**: Render order is strictly defined by the array order in `scenes`.
