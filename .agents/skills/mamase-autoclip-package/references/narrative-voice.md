# Mamase Narrative Voice & Audio Guidelines

This reference details the scripting persona, storytelling arc, Google Gemini TTS configuration, and phonetic pronunciation standards for **Mamase — จักรวาลของใจ**.

---

## 1. The Playful, Natural Science Storyteller Persona

The voice of Mamase is that of a thoughtful, knowledgeable friend sharing a remarkable discovery:

- **Tone**: Natural, playful, confident, lightly cheeky, and conversational.
- **Delivery**: Smooth, connected, lively but effortless. Never sound like a formal television news anchor, advertisement, stage performer, or academic lecturer.
- **Pacing Rhythm**:
  1. **Hook**: An intriguing, counter-intuitive question or relatable comparison.
  2. **Everyday Anchor**: Grounding an incomprehensible cosmic number into an everyday mental picture.
  3. **Surprising Reveal**: An unexpected fact that challenges common assumptions.
  4. **Accurate Mechanism**: A clear explanation of the scientific principles at work.
  5. **Warm Sense of Wonder**: A philosophical climax connecting space and nature to the human spirit (จักรวาลของใจ).

---

## 2. Opening & Outro Conventions

### Scene 01 Opening Line (Reels Hook Rule)
**DO NOT use greetings or slow intros** like `"สวัสดีครับ ยินดีต้อนรับสู่ Mamase จักรวาลของใจ วันนี้เราจะมา..."` in Reels/Shorts.
The spoken script must begin directly (0–3 sec) with a thumb-stopping Hook (surprising fact, contradiction, curiosity question, unexpected consequence, or "เฮ้ย เป็นแบบนี้ได้ยังไง?"). TTS starts directly with the hook without intro music or branding audio.

### Final Scene Outro Line (Topic-Specific Discussion CTA)
End the final content scene on a memorable scientific idea, twist, or implication.
Every Reel then concludes its narration with the approved topic-specific discussion CTA:
> One short question naturally inviting discussion (opinion, prediction, or philosophical reaction) matching the topic.
> Example: "ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?"
> Strictly forbid generic CTAs ("อย่าลืมกดไลก์ กดติดตาม", "คอมเมนต์คุยกันหน่อยนะครับ", "ขอบคุณที่รับชม", or the legacy canned outro).
> The CTA is the final spoken sentence with zero spoken text after it.

---

## 3. Google Gemini TTS Configuration (Approved Default)

In `script.json`, configure the `voice` object as follows:

```json
"voice": {
  "provider": "google-gemini",
  "voice": "Fenrir",
  "speed": 1.05,
  "style_prompt": "Read aloud in a natural, playful, conversational Thai voice. Sound relaxed, confident, and slightly cheeky, like you're casually telling a fascinating story to a close friend. Keep the energy lively but effortless — never sound like a news presenter, announcer, or formal narrator. Use natural changes in pitch and rhythm. Occasionally stretch or emphasize important words for personality. Add small pauses before surprising or funny moments, as if you're building anticipation. The delivery should feel spontaneous and human, with a subtle smile in the voice. Let some sentences start softly and then become more animated when the story gets interesting. Keep the pacing medium to slightly fast, but don't rush. Avoid perfectly even timing between sentences. For surprising facts, sound genuinely impressed or amused, as if you're thinking: \"เฮ้ย... จริงดิ?\" Overall personality: friendly, curious, mischievous, charming, expressive, slightly teasing, and naturally excited. Think of a charismatic Thai content creator explaining something interesting on TikTok or Reels — casual, fun, and easy to listen to. Never sound robotic, overly dramatic, overly cute, or like you're reading from a script."
}
```

- **Voice**: `Fenrir` (natural, playful, conversational tone).
- **Speed**: `1.05` (energetic, crisp short-form pacing).

---

## 4. Mandatory Phonetic Pronunciation (`tts_text`)

Thai text-to-speech engines cannot reliably guess English pronunciations, acronyms, or numbers. Therefore, every scene must provide a phonetic override in `tts_text` whenever needed.

### Core Rules
1. **Full Sentence Replacement**: When `tts_text` is used, write out the **entire spoken line** in natural spoken Thai phonetics.
2. **Correct Spelling in `narration`**: Keep the viewer-facing English and Thai spelling clean and accurate in `narration` and `subtitle` (e.g. `BepiColombo`, `10 เท่า`, `ESA`).
3. **Phonetic Spelling in `tts_text`**: Spell foreign names and acronyms with natural Thai tones and vowels:
4. **Selective Ellipses in `tts_text`**: `...` is allowed for an intentional playful beat such as `เฮ้ย... จริงดิ?`, but do not use it habitually or in every sentence.

| Subject Term | Correct Spelling (`narration`) | Spoken Override (`tts_text`) |
| :--- | :--- | :--- |
| **BepiColombo** | BepiColombo | `เบปิโคลอมโบ` |
| **ESA** | ESA | `อีเอสเอ` |
| **JAXA** | JAXA | `แจ็กซา` |
| **NASA** | NASA | `นาซา` |
| **C3** | C3 | `ซีทรี` |
| **CubeSat** | CubeSat | `คิวบ์แซต` |
| **MPO** | MPO | `เอ็มพีโอ` |
| **Mio** | Mio | `มิโอะ` |
| **Planetary Arrival** | Planetary Arrival | `แพลเน็ตทารี อะไรวัล` |
| **Mamase** | Mamase | `มามาเซ่` |
| **Numbers** | 30 ลำ, 2 ล้าน กม. | `สามสิบ ลำ`, `สอง ล้าน กิโลเมตร` |
| **Temperatures** | 430 องศาเซลเซียส | `สี่ร้อยสามสิบ องศาเซลเซียส` |
