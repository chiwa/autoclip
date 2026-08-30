# AutoClip package contract

This reference mirrors the current validator in `app/domain/models.py` and `app/services/package_service.py`. If the application contract changes, update this file from the code rather than guessing.

## ZIP layout

```text
script.json
images/
  scene-01.png
  ...
  scene-NN-brand-outro.png
audio/                  optional
  bgm.mp3               optional
```

- `script.json` must be at ZIP root.
- Asset paths must be safe relative POSIX paths: no absolute paths, backslashes, or `..`.
- Images: `.jpg`, `.jpeg`, `.png`, `.webp`.
- Audio: `.mp3`, `.wav`, `.m4a`, `.aac`.
- Optional background music must be exactly one file named `audio/bgm` with a supported extension.
- Do not include executable/code files or unsupported file types.

## JSON shape

```json
{
  "project": {"id": "filesystem-safe-id", "title": "ชื่อคลิป", "language": "th-TH", "resolution": "1080x1920", "fps": 30},
  "voice": {"provider": "local", "voice": "thai-male-01", "speed": 1.0},
  "scenes": [
    {"id": "scene-01", "image": "images/scene-01.png", "narration": "ข้อความบรรยาย", "subtitle": "ข้อความบนจอ", "motion": "slow_zoom_in", "transition": "dissolve"}
  ]
}
```

- Resolution is `WIDTHxHEIGHT`; use `1080x1920` for vertical output. Use 30 FPS unless requested otherwise.
- Voice speed is 0.5–2.0. Scene IDs must be unique. Narration must not be empty.
- If subtitle is absent or blank, AutoClip uses narration.
- Every referenced image must exist in the ZIP.
- A scene's transition leads from that scene to the next. Omitted transition uses the app's default fade behavior.

## Supported motion presets

`none`, `slow_zoom_in`, `slow_zoom_out`, `pan_left_to_right`, `pan_right_to_left`, `pan_up`, `pan_down`

## Supported transition presets

`none`, `fade`, `dissolve`, `fade_black`, `fade_white`, `fade_slow`, `fade_fast`, `fade_grays`, `wipe_left`, `wipe_right`, `wipe_up`, `wipe_down`, `wipe_top_left`, `wipe_top_right`, `wipe_bottom_left`, `wipe_bottom_right`, `slide_left`, `slide_right`, `slide_up`, `slide_down`, `smooth_left`, `smooth_right`, `smooth_up`, `smooth_down`, `circle_open`, `circle_close`, `circle_crop`, `rect_crop`, `vertical_open`, `vertical_close`, `horizontal_open`, `horizontal_close`, `zoom_in`, `pixelize`, `radial`, `horizontal_blur`, `distance`, `squeeze_horizontal`, `squeeze_vertical`, `diagonal_top_left`, `diagonal_top_right`, `diagonal_bottom_left`, `diagonal_bottom_right`, `horizontal_slice_left`, `horizontal_slice_right`, `vertical_slice_up`, `vertical_slice_down`

For Mamase, prefer restrained combinations such as `fade`, `dissolve`, `fade_black`, `smooth_left`, `smooth_right`, and occasional `zoom_in`.
