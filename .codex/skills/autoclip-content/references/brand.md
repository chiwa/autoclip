# Mamase channel identity

- Channel name: **Mamase**
- Thai descriptor: **จักรวาลของใจ**
- Closing line: Topic-specific discussion question (e.g. `ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?`)

## Mandatory final scene

Every completed Reel package ends with a dedicated branding scene after the editorial ending. It must be the final JSON scene:

```json
{
  "id": "scene-NN-brand-outro",
  "image": "images/scene-NN-brand-outro.png",
  "narration": "ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?",
  "tts_text": "ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?",
  "subtitle": "ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?",
  "motion": "slow_zoom_in",
  "transition": "none"
}
```

Replace `NN` with the next sequential scene number. Use the topic-specific discussion question inviting viewer response. Strictly forbid generic CTAs ("กดไลก์", "กดแชร์", "คอมเมนต์คุยกัน", "ขอบคุณที่รับชม"). Zero spoken words after the CTA.
