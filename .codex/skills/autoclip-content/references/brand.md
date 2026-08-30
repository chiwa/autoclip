# Mamase channel identity

- Channel name: **Mamase**
- Thai descriptor: **จักรวาลของใจ**
- Closing line: **ค้นพบโลก ค้นพบใจ กับ Mamase**

## Mandatory final scene

Every completed package ends with a dedicated branding scene after the editorial ending. It must be the final JSON scene.

```json
{
  "id": "scene-NN-brand-outro",
  "image": "images/scene-NN-brand-outro.png",
  "narration": "ค้นพบโลก ค้นพบใจ กับ Mamase",
  "subtitle": "Mamase\nจักรวาลของใจ",
  "motion": "slow_zoom_in",
  "transition": "fade_black"
}
```

Replace `NN` with the next sequential scene number. Copy `assets/mamase-brand-outro.png` into the package using the exact path referenced by the final scene.

Do not redesign, recolor, crop, add text to, or generate a substitute for the canonical branding asset unless พี่พี explicitly requests and approves a replacement.
