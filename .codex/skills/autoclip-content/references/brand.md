# Mamase channel identity

- Channel name: **Mamase**
- Thai descriptor: **จักรวาลของใจ**
- Closing line: Topic-specific discussion question (e.g. `ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?`)

## Mandatory silent post-roll

Every completed Mamase Reel appends the locked branding image only after final
content narration and subtitles finish. It is not a JSON scene:

```json
{
  "outro": {
    "enabled": true,
    "image": "mamase-reels-end-scence.png",
    "duration": 2.0,
    "bgm_fade_out": true
  }
}
```

Keep any topic-specific discussion question in the final content scene. The
post-roll has no narration, TTS, subtitle, or scene-level motion plan.
