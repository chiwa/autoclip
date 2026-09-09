# Mamase channel identity

- Channel name: **Mamase**
- Thai descriptor: **จักรวาลของใจ**
- Closing line: **ถ้าชอบเรื่องราวอวกาศ จักรวาล วิทยาศาสตร์ และเทคโนโลยี กดไลก์ กดแชร์ และกดติดตาม แล้วมาค้นพบโลก ค้นพบใจ ไปกับ Mamase จักรวาลของใจครับ**

## Mandatory final scene

Every completed package ends with a dedicated branding scene after the editorial ending. It must be the final JSON scene.

```json
{
  "id": "scene-NN-brand-outro",
  "image": "images/scene-NN-brand-outro.png",
  "narration": "ถ้าชอบเรื่องราวอวกาศ จักรวาล วิทยาศาสตร์ และเทคโนโลยี กดไลก์ กดแชร์ และกดติดตาม แล้วมาค้นพบโลก ค้นพบใจ ไปกับ Mamase จักรวาลของใจครับ",
  "tts_text": "ถ้าชอบเรื่องราวอวกาศ จักรวาล วิทยาศาสตร์ และเทคโนโลยี กดไลก์ กดแชร์ และกดติดตาม แล้วมาค้นพบโลก ค้นพบใจ ไปกับ มามาเซ่ จักรวาลของใจครับ",
  "subtitle": "กดไลก์ · แชร์ · ติดตาม\nMamase จักรวาลของใจ",
  "motion": "slow_zoom_in",
  "transition": "fade_black"
}
```

Replace `NN` with the next sequential scene number. Copy `assets/mamase-brand-outro.png` into the package using the exact path referenced by the final scene.

Do not redesign, recolor, crop, add text to, or generate a substitute for the canonical branding asset unless พี่พี explicitly requests and approves a replacement.

Deliver the CTA in the same friendly storyteller voice as the clip. It belongs
only in the final branding scene; do not repeatedly interrupt the story with
promotional requests.
