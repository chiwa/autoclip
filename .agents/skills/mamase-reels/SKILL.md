---
name: mamase-reels
description: Master rules and specifications for Mamase (จักรวาลของใจ) vertical short-form videos (Reels, Shorts, TikTok), including mandatory opening hook rules, retention architecture, editorial visual standards, Scene 01 Key Art permanent workflow, topic-specific discussion CTA, Fenrir 1.05 TTS defaults, and standard machine-friendly JSON output format.
---

# Mamase Reels Production Skill

This skill governs the production of vertical short-form videos (Reels, Shorts, TikTok) for **Mamase (จักรวาลของใจ)** in `1080x1920` (9:16) format.

---

## 1. Topic-Only Input Is Complete Input

When the user supplies only a topic, working title, or one-sentence premise, proceed autonomously:
1. Research and verify facts from authoritative scientific sources (NASA, JWST, ESO, ESA, peer-reviewed astrophysics).
2. Formulate the truthful, thumb-stopping Hook (0–3 seconds).
3. Draft the tight 45–60 second narrative arc with mini-wows every 10–15 seconds.
4. Craft the topic-specific discussion CTA.
5. Plan the scenes (normally 4–7 content scenes).
6. Design Scene 01 according to `mamase-reels-cover`.
7. Pause only at the mandatory Scene 01 approval gate, then finish the remaining scenes and AutoClip package after approval.

Never require the user to invent prompts or composition instructions. For Scene 01, generate one native candidate at a time. Do not scan unrelated assets, generate seed grids, build contact sheets, use `rembg`, paste cutouts, or attempt inpainting unless explicitly requested. Report a failed native generation instead of hiding it behind a lower-quality fallback.

---

## 2. Hook Is Mandatory in the First 3 Seconds

Every Mamase Reel must begin immediately with the strongest, most compelling idea in the story. The first spoken sentence must work as a Hook.

### Strict Prohibitions (Never begin with)
- Greetings (`สวัสดีครับ`, `ยินดีต้อนรับสู่...`)
- Channel or presenter introductions (`สู่ Mamase จักรวาลของใจ`, `ผมพี จาก Mamase`)
- "วันนี้เราจะมาพูดถึง...", "วันนี้ Mamase จะพาไป...", "ในคลิปนี้..."
- "ก่อนอื่น...", "มาเริ่มกันที่..."
- "รู้หรือไม่...", "คุณเคยสงสัยไหม..." (unless paired immediately with an extraordinary paradox)
- Background, history, or chronological setup
- Academic definitions
- Slow, cinematic buildup or establishing drone shots without a mystery

### Mandatory Starting Categories (Start immediately with one of)
- **Surprising fact**: An astonishing, counter-intuitive truth.
- **Contradiction**: Two facts that seem impossible to coexist.
- **Strong curiosity question**: A question that creates an immediate itch to know.
- **Unexpected consequence**: A radical "what if" or bizarre scientific reality.
- **Scientifically accurate “เฮ้ย เป็นแบบนี้ได้ยังไง?” moment**: Genuine scientific wonder.

### Truthful & Scientifically Defensible
The hook must be scientifically accurate and defensible. Never use misleading clickbait, exaggerated pseudoscience, or unverified claims.

### General Audience Clarity
Use phrasing that a non-scientist can understand instantly within 1–2 seconds. Avoid technical jargon in the first 3 seconds.

### Open Loop & Immediate Forward Momentum
The hook must open a curiosity gap. The second sentence must immediately continue the promise of the hook, never pivoting back to generic background exposition.

### Hook Matching Rule
The `hook` field in metadata must be **EXACTLY identical** to the first spoken sentence in `tts`.

---

## 3. Every Reel Must Earn the Next 10 Seconds

Short-form viewers decide whether to keep watching continuously:
- Every **10–15 seconds** must deliver a mini-wow, reveal, twist, or compelling new fact.
- Maintain constant forward momentum.
- Avoid lecture format, unbroken monologues, or repetitive restatements.
- A useful progression: **Hook (0–3s) → Relatable context (3–10s) → Surprising reveal / Mini-wow (10–25s) → Mechanism / Twist (25–45s) → Big payoff & Topic-Specific CTA (45–60s)**.

---

## 4. Duration & Pacing Standards

- **Preferred Target**: **45–60 seconds**.
- **Acceptable Maximum**: **60–75 seconds**.
- **Compression First**: If the estimated duration exceeds 75 seconds, revise and compress the script before returning the result. Do not simply return 90–100 seconds and consider generation successful.
- **Script compression before TTS speed adjustment**: Edit out filler, condense sentences, and sharpen points rather than artificially rushing the speech rate.
- **No Part 1 / Part 2**: Avoid splitting a story into parts unless each part genuinely provides standalone value and a complete emotional/scientific payoff.

---

## 5. Topic-Specific Discussion CTA

Every Mamase Reel must conclude with **one short question naturally inviting discussion** (opinion, prediction, or philosophical reaction) matching the topic.

### Preferred Examples (Topic-Specific)
- `"ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?"`
- `"คุณคิดว่ามนุษย์จะไปถึงอารยธรรมระดับหนึ่งก่อน หรือเราจะหยุดตัวเองเสียก่อน?"`
- `"ถ้าค้นพบสิ่งมีชีวิตบนยูโรปาจริง คุณคิดว่าเราควรไปรบกวนพวกมันไหม?"`
- `"ถ้าเลือกได้ คุณอยากให้ยานสำรวจลำต่อไปมุ่งหน้าไปดาวยูเรนัสหรือเนปจูน?"`

### Strict Prohibitions (Generic CTAs)
Do **NOT** use generic social-media engagement lines:
- `อย่าลืมกดไลก์ กดติดตาม`
- `อย่าลืมคอมเมนต์คุยกันหน่อยนะครับ`
- `ถ้าชอบเรื่องราวอวกาศ... กดไลก์ กดแชร์` (the legacy canned outro is retired)
- `ขอบคุณที่รับชม`
- `ติดตาม Mamase จักรวาลของใจ`

### Final Spoken Sentence Rule
The CTA is normally the **final spoken sentence** of the Reel. There must be **no spoken text after the CTA** unless explicitly requested.

---

## 6. TTS Defaults

- **Provider**: `google-gemini`
- **Language**: `th-TH`
- **Voice**: `Fenrir`
- **Default Speed**: `1.05` (updated from 1.0 for crisper, energetic short-form pacing)
- **Style**: Natural, playful, conversational Thai storyteller—warm, confident, curious, and lightly cheeky without sounding like a news anchor or formal narrator.

---

## 7. Branding & End-Scene Rules

- Use `"Mamase"` or `"Mamase REELS"` only.
- **Strictly NO "MAMASE PODCAST"** on Reel covers or assets.
- **Strictly NO bilingual badges** (`"AVAILABLE IN THAI & ENGLISH"`), language flags, or audio-track labels on Reel assets.
- End card must be short with the optional CTA question displayed or clean brand outro (`assets/branding/mamase/reels-end-scene.png`).

---

## 8. Natural Spoken Thai

- Prefer natural Thai terms over clumsy phonetic transliterations (e.g. `ดาวอังคาร` instead of Mars, `ลมสุริยะ` instead of โซลาร์วินด์, `สนามแม่เหล็ก` instead of แมกเนติกฟิลด์).
- For proper scientific names, spacecraft, or international designations (e.g. `Parker Solar Probe`, `JWST`, `K2-18 b`), use clear phonetic Thai in `tts_text` while preserving correct English spelling in subtitles.

---

## 9. Standard Mamase Reel Output Contract

All Mamase Reel generation must return a predictable, machine-friendly output format. Do not return free-form prose only.

### Primary Deliverable (Standard JSON Structure)

When generating a Mamase Reel, return this JSON-compatible structure:

```json
{
  "topic": "Short internal topic name",
  "title": "Viewer-facing Reel title",
  "description": "Short social description with relevant hashtags",
  "estimated_duration_seconds": 55,
  "hook": "Exact first spoken Hook sentence",
  "cta": "Exact final spoken discussion question",
  "tts": "Complete Thai narration from Hook through CTA",
  "voice": {
    "provider": "google-gemini",
    "voice": "Fenrir",
    "speed": 1.05,
    "language": "th-TH"
  },
  "validation": {
    "hook_within_first_3_seconds": true,
    "has_mini_wow_every_10_to_15_seconds": true,
    "topic_specific_cta": true,
    "generic_engagement_cta": false,
    "podcast_branding_present": false,
    "target_duration_met": true
  }
}
```

### Hook Field Requirements
- `hook` must be exactly identical to the first spoken sentence in `tts`.
- Normally one sentence.
- Zero greeting, zero setup, zero channel introduction.

### CTA Field Requirements
- `cta` must contain the exact final spoken discussion question.
- Matches the ending of `tts`.
- No generic subscribe/like/share language. No "ขอบคุณที่รับชม".

### Estimated Duration Requirement
- Target: `45–60 seconds`. Acceptable: `60–75 seconds`.
- Calculate or estimate `estimated_duration_seconds` from actual spoken words (~3.5–4 syllables/sec in Thai at speed 1.05).
- If duration exceeds 75 seconds, compress the script before returning.

### TTS Content Requirements
- Production-ready text only.
- Never include drafting tags (`[HOOK]`, `[CTA]`, `[Scene 1]`, `[Pause]`, `(dramatic tone)`).
- Never include Markdown formatting or production notes inside `tts`.

### Description & Title Fields
- `description`: Social copy with hashtags (`#Mamase #อวกาศ #วิทยาศาสตร์`). Keep hashtags out of `tts`.
- `title`: Short, curiosity-driven title suitable for mobile screens.

---

## 10. Optional Scene-Based Output

When the caller requests multiple images, scenes, or per-scene generation:

```json
{
  "topic": "...",
  "title": "...",
  "description": "...",
  "estimated_duration_seconds": 58,
  "hook": "...",
  "cta": "...",
  "scenes": [
    {
      "scene": 1,
      "purpose": "hook",
      "tts": "...",
      "visual_prompt": "..."
    },
    {
      "scene": 2,
      "purpose": "setup",
      "tts": "...",
      "visual_prompt": "..."
    },
    {
      "scene": 3,
      "purpose": "wow",
      "tts": "...",
      "visual_prompt": "..."
    },
    {
      "scene": 4,
      "purpose": "payoff",
      "tts": "...",
      "visual_prompt": "..."
    },
    {
      "scene": 5,
      "purpose": "cta",
      "tts": "...",
      "visual_prompt": "..."
    }
  ],
  "voice": {
    "provider": "google-gemini",
    "voice": "Fenrir",
    "speed": 1.05,
    "language": "th-TH"
  }
}
```

Rules for scenes:
- Concatenating every `scenes[].tts` in order must produce the complete spoken Reel.
- Scene 1 contains the Hook.
- The final scene containing narration contains the CTA.
- Do not repeat the Hook or CTA.
- Normally 4–7 scenes.
- Each scene has one clear narrative purpose.

---

## 11. Quick Reel Compatibility

For the existing AutoClip Quick Reel workflow, preserve compatibility with:

```json
{
  "topic": "...",
  "description": "...",
  "tts": "..."
}
```

When this minimal schema is required, all Hook and CTA rules still apply:
- `tts` starts directly with the Hook (no greeting).
- `tts` ends with the topic-specific CTA.
- Target duration remains 45–60 seconds.
- Do not add unsupported fields to endpoints expecting the minimal contract.

---

## 12. Output Cleanliness & Pre-Return Validation

When JSON is requested:
- Return valid JSON only.
- No conversational prose wrappers (`นี่คือ JSON ที่สร้างให้ครับ`, `หวังว่าจะชอบนะครับ`).
- No trailing commas. No JS-style comments.

### Final Validation Checklist
Before returning a generated Reel, verify:
```text
✓ hook == first spoken sentence of tts
✓ cta == final spoken sentence of tts
✓ estimated_duration_seconds <= 75 seconds (target 45–60s)
✓ no greeting or setup before hook
✓ no spoken text after CTA
✓ no generic engagement CTA ("กดไลก์", "คอมเมนต์คุยกัน", "ขอบคุณที่รับชม")
✓ no Podcast-only branding ("MAMASE PODCAST", bilingual badges, flags)
✓ no metadata/markdown mixed into tts
✓ natural Thai narration
✓ Fenrir default speed = 1.05
```

---

## 13. Scene 01 Permanent Standard (Key Art)

Every Mamase Reel Cover must inspect and follow the permanent master reference at `assets/branding/mamase/reference/mamase-reels-editorial-poster-master.png`.

Scene 01 is a **Premium Cinematic Science Documentary Key Art**:
1. Stops scrolling immediately (1–2s).
2. Communicates the core mystery or contradiction in a single frame.
3. Crystal-clear Topic title and Thai hook readability on mobile.
4. **Hero Subject**: Prominent with massive scale, retaining complete recognizable shape, silhouette, and spatial context. Correlates directly with the hook premise.
5. **Story Anchors**: Mamase male explorer and dog participate in the story with unified lighting, contact shadows, and contextual action (do not default to sitting on a rock looking upward).
6. **Typography & Branding**:
   - Composite brand header (`mamase_podcast_header.png` as clean Mamase logo) top-left.
   - Strictly NO "MAMASE PODCAST" text or bilingual badges added to the cover.
   - Topic Title + Thai Hook (`Kanit-Bold.ttf`, warm white with cyan highlight on second line).
   - Protected zones: Map hero, celestial objects, explorer, and dog; typography must never overlap protected rectangles or the subtitle safe area.
