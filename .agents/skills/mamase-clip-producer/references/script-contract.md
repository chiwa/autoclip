# Script JSON Contract Reference

## Schema Definition (`script.json`)

```json
{
  "project": {
    "id": "lake-natron-mamase-v2",
    "title": "Lake Natron ทะเลสาบที่เปลี่ยนสัตว์เป็นหินจริงหรือ?",
    "language": "th-TH",
    "resolution": "1080x1920",
    "fps": 30
  },
  "voice": {
    "provider": "local",
    "voice": "thai-male-01",
    "speed": 1.0
  },
  "scenes": [
    {
      "id": "scene-01",
      "image": "images/scene-01.png",
      "narration": "คุณเชื่อไหม เรื่องนี้มีอยู่จริงบนโลกของเรา",
      "subtitle": "คุณเชื่อไหม เรื่องนี้มีอยู่จริงบนโลกของเรา",
      "motion": "slow_zoom_in",
      "transition": "dissolve"
    }
  ]
}
```

## Fields Specification

### Project Object (`project`)
| Field | Type | Requirement | Description / Notes |
| :--- | :--- | :--- | :--- |
| `id` | string | **Required** | Filesystem-safe project identifier (e.g. `lake-natron-mamase-v2`) |
| `title` | string | **Required** | Human-readable title for display |
| `language` | string | **Required** | Locale code (e.g. `th-TH`) |
| `resolution` | string | Optional | `WIDTHxHEIGHT`, defaults to `1080x1920` |
| `fps` | number | Optional | Positive integer frame rate (defaults to `30`) |

### Voice Object (`voice`)
| Field | Type | Requirement | Description / Notes |
| :--- | :--- | :--- | :--- |
| `provider` | string | **Required** | TTS Provider: `local` (VachanaTTS2 ONNX) or test dummy |
| `voice` | string | **Required** | Voice identifier: `thai-male-01`, `thai-male-02`, `thai-female-01`, `thai-female-02` |
| `speed` | number | **Required** | Narration speed multiplier (e.g. `1.0`) |

### Scene Object (`scenes[]`)
| Field | Type | Requirement | Description / Notes |
| :--- | :--- | :--- | :--- |
| `id` | string | **Required** | Unique scene ID (e.g. `scene-01`) |
| `image` | string | **Required** | Relative path to image (e.g. `images/scene-01.png`) |
| `narration` | string | **Required** | Thai narration text in UTF-8 for TTS |
| `subtitle` | string / boolean | Optional | Subtitle display text. Set to `false` or `"none"` to disable subtitles |
| `show_subtitle` | boolean | Optional | `true` (default) or `false`. Set to `false` when text is already baked into the image |
| `motion` | string | **Required** | Camera motion preset (see Motion Presets below) |
| `transition` | string | Optional | Transition to next scene; default `fade`. Ignored on final scene |

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
