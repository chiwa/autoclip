---
name: mamase-autoclip-package
description: Create review-ready AutoClip ZIP packages for Mamase จักรวาลของใจ, including Thai narration, vertical scene assets, and required video metadata.
---

# Mamase AutoClip package

Use this skill when creating or revising a Mamase short-form video ZIP. Do not
use it to change AutoClip application code or RunPod setup.

## Creative flow

For a new public clip created manually, present the complete Thai script and
scene outline for approval before generating final assets, unless the user
explicitly asks for a technical test package. AutoClip's `/ai` automatic mode
uses the same two approvals without chat: generate and approve the script,
generate and approve the scene images, then create the finished package. It
reports each planning, image, validation, and packaging step live. Keep scenes
in the resulting `script.json` order.

Public clips default to **45–60 seconds** (acceptable maximum: **60–75 seconds**; if estimated duration exceeds 75s, compress and revise script before returning). Normally use 4–7 content scenes plus the final brand scene (minimum 5–8 scenes). Never pad runtime with repeated narration, restated points, or decorative filler. Deliver a mini-wow or reveal every 10–15 seconds to sustain retention.

### Mandatory Opening Hook & Mamase Reel Hook Gate

**CRITICAL OVERRIDE**: Never use greetings, channel intros, or slow setups like `"สวัสดีครับ ยินดีต้อนรับสู่ Mamase จักรวาลของใจ วันนี้เราจะมา..."`, `"รู้หรือไม่..."`, or `"ในคลิปนี้..."` (these legacy openings are strictly forbidden).

For short-form Reels, Shorts, and TikTok:
1. The spoken script must start immediately (0–3s) with a thumb-stopping Hook: a surprising fact, contradiction, curiosity question, unexpected consequence, or “เฮ้ย เป็นแบบนี้ได้ยังไง?”.
2. Must pass the 10-point **Mamase Reel Hook Gate** as a blocking QA gate before generating TTS, images, or package files:
   - Hook within first 1–3 sec
   - No greeting/setup before hook
   - Simple enough for general audience
   - Creates curiosity gap (open loop)
   - Scientifically accurate and defensible
   - First visual reinforces hook (hero subject dominates frame)
   - No filler
   - New information/payoff every few seconds
   - Ending leaves a strong final idea/twist
   - TTS starts directly with hook
3. TTS starts directly with the hook without intro music or branding audio.
4. Scene 01 visual must immediately communicate the hook's specific mystery with a colossal, dominating hero subject.

### Mamase science-storyteller voice

Write narration as a charismatic, playful Thai science storyteller: curious,
friendly, lightly cheeky, and genuinely delighted by surprising facts. It must
sound like an intelligent friend sharing a discovery, never like a news anchor
or a textbook. Use concise spoken sentences and intentional ellipses or short
pauses only where they improve timing.

Open with an imaginable question, contrast, or scale comparison. Translate a
large number into an everyday mental picture, then earn a small pivot such as
`แต่เดี๋ยวก่อน...` with a real next fact. End on wonder or meaning rather than
overclaiming. A useful rhythm is: **hook → relatable comparison → surprising
reveal → playful aside → accurate explanation → warm sense of wonder**.

Use human spoken asides only when they make a fact easier to picture. Keep
punctuation natural. Allow `...` sparingly in `tts_text` when it creates a natural playful beat; use commas, periods,
or clean sentence boundaries so Google TTS stays connected and even.

Humor must clarify the science, not replace it. Never invent consequences,
imply speculation is confirmed, or overstate a measurement for a punchline.
For Gemini TTS, the channel's default delivery instruction is:

> Read aloud in a natural, playful, conversational Thai voice. Sound relaxed, confident, and slightly cheeky, like you're casually telling a fascinating story to a close friend. Keep the energy lively but effortless — never sound like a news presenter, announcer, or formal narrator. Use natural changes in pitch and rhythm. Occasionally stretch or emphasize important words for personality. Add small pauses before surprising or funny moments, as if you're building anticipation. The delivery should feel spontaneous and human, with a subtle smile in the voice. Let some sentences start softly and then become more animated when the story gets interesting. Keep the pacing medium to slightly fast, but don't rush. Avoid perfectly even timing between sentences. For surprising facts, sound genuinely impressed or amused, as if you're thinking: "เฮ้ย... จริงดิ?" Overall personality: friendly, curious, mischievous, charming, expressive, slightly teasing, and naturally excited. Think of a charismatic Thai content creator explaining something interesting on TikTok or Reels — casual, fun, and easy to listen to. Never sound robotic, overly dramatic, overly cute, or like you're reading from a script.

When the Google Gemini TTS provider is selected, use the approved Mamase voice
profile unless the user overrides it: voice `Fenrir`, `pitch: 0`, and
`speakingRate: 1.05`. The target feeling is natural, playful, confident, and
naturally conversational, with crisp energetic pacing.

For Native AutoClip, Google Gemini TTS uses Application Default Credentials
created with `gcloud auth application-default login` and its quota project. Do
not create, store, or put service-account JSON keys in a ZIP or project config.
The default provider is `google-gemini`; its default voice is `Fenrir`.
When exposing Gemini settings in AutoClip, make the narration-style prompt and
speaking rate editable. Always provide a **คืนค่า Mamase default** control that
restores the approved prompt, Fenrir, and `speakingRate: 1.05`; list voices in
clearly labelled **ชาย** and **หญิง** groups, with Fenrir first.
Keep narration silence trimming disabled by default. It may remain available as
an explicit opt-in, but package generation must not trim scene audio edges
unless the user enables it because the first Thai syllable can be clipped.
For a Google Gemini render, narration requests may run concurrently (default:
six scenes per job, configurable through `AUTOCLIP_GOOGLE_TTS_PARALLELISM`)
because each scene is independent. Keep the completed
audio mapped back to the original scene order; use bounded concurrency rather
than unbounded requests.
For FFmpeg Motion, AutoClip may render two independent scenes concurrently;
their subtitle and MP4 outputs remain scene-local and are sorted back into
script order before final composition. Keep Wan 2.2 generation and final
composition sequential.

Use the supplied presenter image unchanged for a static/FFmpeg-motion scene.
If a Wan prompt is included, state that it must preserve the supplied 2D anime
image, character identity, glasses, hair, clothing, and composition. Do not
claim that `character_id` alone identity-locks Wan.

Use presenter scenes sparingly and use b-roll for explanation. Reserve the
lower safe area for AutoClip subtitles. The first scene always uses a short
in-image hook under the rule below; otherwise avoid in-image text. For space
topics, use `dist/examples/` as the visual benchmark:
real-science, cinematic documentary imagery rather than generic AI infographic
cards; prefer permitted NASA/JWST/ESO/Hubble/Caltech-IPAC sources when
available.

Choose each scene image from that scene's narration, not just the broad topic.
The visual must show the central subject, setting, action, or evidence stated
in the line so a viewer can understand it before reading subtitles. Avoid
generic decorative b-roll whenever the narration calls for a specific animal,
place, process, object, or scientific detail.

## Visual quality gate — cinematic, not placeholder art

When the user provides only a topic and asks to create images after reading
`start.md`, complete the master-image workflow autonomously. Derive the visual
story, shot list, and prompts yourself; do not ask the user for per-scene
prompts. If only images were requested, stop after saving and reporting the
approved masters—do not create JSON or a ZIP without a separate request.

Before delivery or packaging, open and inspect every master image at phone
size. A written audit or generated manifest alone is not evidence that an image
passed. Mamase space and
science clips must feel like a premium cinematic documentary, not a sparse
slide deck, a generic AI render, or an infographic channel.

Treat `start.md` as the detailed visual authority. The target medium is Premium
Cinematic Documentary Key Art / Cinematic Editorial Concept Art, not raw
astrophotography, stock b-roll, wallpaper, or loosely composited web images.
Every frame needs a large hero subject, a visible story relationship or action,
three-layer depth, coherent directional lighting, material texture, scale cues,
and a consistent color script across the set.

For vertical delivery, require at least native `1080x1920`. Prefer native
`2160x3840` masters when the generator supports it and extra crop/zoom latitude
is useful, but never upscale a smaller image merely to label it 4K. For
horizontal work, the equivalents are `1920x1080` minimum and `3840x2160`
preferred native master. Composition and narration fidelity outrank pixel
count.

Read `assets/parker_solar_probe_reel/visual-reference.md` before creating a
space or science Reel. It is the concise, durable quality benchmark; inspect
the master images in that folder only when a composition needs closer study.
Meet or exceed its standard without copying its Sun/Parker subject matter into
unrelated stories. Never rely on `dist/` as the sole visual reference because
ZIP outputs may be cleaned up.

For every vertical Mamase Reel, Short, or TikTok, also read
`../mamase-reels/SKILL.md`. It is authoritative for the locked logo overlay and
final scene.

- Make the subject visually dominant: use a clear foreground subject plus
  atmosphere, scale, light, depth, or a secondary element that tells the
  scene's story. Do not deliver a small spacecraft, diagram, or moon floating
  in a mostly empty black 9:16 canvas.
- Keep visual energy in the middle 70–80% of the frame. The subtitle safe area
  is a calm lower-center band, not an excuse to leave half the image empty.
  Compose vertically with deliberate foreground, midground, and background.
- Prefer dramatic, physically credible documentary lighting: directional sun
  light, reflected ice, volumetric dust/ice particles, rich but controlled
  contrast, and scale cues. Avoid flat cut-out objects on a plain star field.
- Except for scene 1's approved Thai title and hook, scene masters contain no
  generated labels, English copy, numbered callouts, charts, HUD, NASA/ESA
  logos, watermarks, or embedded subtitles. Vertical Mamase content scenes use
  only the real locked logo composited after artwork as required by
  `mamase-reels`.
- Scene 1 must be integrated **Narrative Key Art**: the presenter, subject,
  title, and hook share one cinematic light direction and depth. Never paste a
  stock presenter over an unrelated background or leave a huge blank area.
- A mechanism that genuinely needs explanation may use a clean cinematic
  cutaway, but it must be image-led and label-free—not a textbook cross-section
  or presentation slide.

Reject and regenerate an image that has any of these failure signals: more
than roughly one third dead empty space without a compositional purpose,
generic black-starfield filler, weak/small focal subject, inconsistent visual
style, unreadable or unintended text, any generated or unapproved logo/watermark, visibly pasted
presenter, or a picture that does not make that narration's fact legible.
For a multi-scene package, do this visual pass before writing the final ZIP;
regenerate only the failed scenes and retain strong ones.
In autonomous image mode, repeat generation and inspection for failed scenes
until all images pass before reporting completion.

## Mandatory Reels hook and retention

Treat the first 1–3 seconds as the package's highest-priority moment. The TTS
must start directly with a simple, truthful hook: a surprising fact,
contradiction, strong curiosity question, unexpected consequence, or a
scientifically accurate “เฮ้ย เป็นแบบนี้ได้ยังไง?” moment. Never place a
greeting, channel introduction, `วันนี้เราจะมาพูดถึง...`, background, history,
definition, slow setup, episode label, branding audio, or intro music before it.
The hook must open a loop and its second sentence must immediately continue the
promise. For uncertain science, create intrigue without visualizing an
unsupported outcome. For K2-18 b, use a
cinematic exoplanet, red dwarf star, and small JWST silhouette with the hook
`K2-18 b… เราเจอสัญญาณของเอเลียนแล้วหรือยัง?` Do not include aliens,
unverified in-image claims, or a presentation that suggests life is confirmed;
the next scene must explain the actual evidence and uncertainty.

Every first scene includes two complementary in-image Thai text layers: a
concise topic title (for example `ดาวศุกร์`) and a separate short, beautiful
2-5 word hook that makes the viewer want the answer. Make their hierarchy
clear—topic title identifies the story, hook supplies curiosity—and keep both
large, high contrast, outside the lower subtitle safe area and main subject.
Compose it like a premium science-book cover or documentary-film poster: one
dominant focal subject, intentional negative space, and elegant restrained
typography—not a crowded information card. The recurring Mamase anime
presenter must appear in this scene with the established face, glasses, tousled
black hair, and a face-forward composition suitable for a Wan/LatentSync
talking shot. The canonical reference is
`assets/characters/mamase-presenter-v1.png`; preserve its identity and set
`character_id` to `mamase-presenter-v1` in the Wan plan. Do not introduce a
different presenter without the user's approval. The wardrobe is not fixed:
for each new clip, match it to the background with a professional, youthful,
lightly playful outfit. Preserve the approved asset in an existing package
unless the user asks to change it. Choose expression and natural body language
to serve the story beat—wonder, surprise, joy, concern, curiosity, or quiet
reflection are all valid when appropriate—while preserving the same identity.
For K2-18 b, the in-image
hook is `เจอสัญญาณเอเลียน?`.

Design the same image as **Narrative Key Art** / a cinematic storytelling
thumbnail: it should show the full story, stakes, and emotional promise of the
video at a glance, not just a generic subject image. Favor a readable
cause-and-effect or before-and-after composition where appropriate. Scene 1
must deliver the same core story image as the thumbnail, so the click is paid
off immediately.

## Delivery format

Every Wan plan defaults to AutoClip's 22 sampling steps. The first hook scene
must explicitly include `"steps": 25` in its `wan` object for the best visual
quality. Leave `steps` out of ordinary scenes unless they need a deliberate
quality override; valid values are 10 through 50. `steps` is a sampling budget,
not a frame rate and not a duration control.

Use `frames: 81` for normal Wan scenes. At 16 fps this is about 5.06 seconds;
write each Wan narration for roughly 4.5–5.0 seconds and add a scene when the
story needs more time rather than extending one AI shot. Prepare vertical Wan
assets for the 640x1152 generation profile; AutoClip will upscale during final
1080x1920 composition. The hook remains 25 steps, presenter/important scenes
normally use 22, and simple b-roll may use 20 only after review.

Runtime note for a package author: the proven default is ComfyUI dynamic VRAM.
The RunPod operator may explicitly launch `/workspace/start-comfyui.sh
--highvram` only when its queue is empty and an 81-frame smoke test follows;
it is not a package field and must never be assumed or claimed by the ZIP.
The tested long-shot workload previously required rollback from high-VRAM mode,
so package design must remain safe under dynamic VRAM.

Use exactly one format per package and generate images in that native aspect
ratio: `1080x1920` for Shorts/Reels/TikTok or `1920x1080` for standard YouTube.
Set `project.resolution` accordingly. For 16:9, use real wide documentary
composition rather than cropping a vertical image, and reserve a clean
lower-center area for subtitles.

### Reel / Shorts pacing

Default to a dense **45–60 second** Mamase Reel without padding or forcing an
exact runtime. Use 60–120 seconds only when the subject has enough genuine
reveals to sustain retention. Choose scene count from the story beats; every
few seconds must add information, payoff, reversal, consequence, or a larger
question. Do not add filler or decorative b-roll merely to reach a duration.

Use this default structure: `0–3 sec` hook; `3–10 sec` minimum context;
`10–30 sec` payoff plus a real wow or reversal; `30–45 sec` twist or larger
implication; and, when earned, `45–60 sec` memorable final payoff or strong
unanswered question.

#### Mamase Reel Hook Gate

Before approving a script and before generating TTS or visuals, verify:

1. Hook within first 1–3 sec.
2. No greeting or setup before hook.
3. Simple enough for a general audience.
4. Creates a curiosity gap.
5. Scientifically accurate and defensible.
6. First visual reinforces the hook.
7. No filler.
8. New information or payoff every few seconds.
9. Ending leaves a strong final idea or twist.
10. TTS starts directly with the hook.

If any major item fails, rewrite the opening before continuing.

Make **FFmpeg Motion** the default renderer for short-form packages: it is
fast, stable, and inexpensive. Use Wan only for 0–2 high-value shots—normally
the Mamase presenter hook and optionally one reveal. The remaining shots need
distinct, narration-matched source images with intentional FFmpeg motion and
focus; do not repeatedly zoom the same frame just to increase scene count.

One ZIP must work unchanged in both Generate modes. Every scene always includes
its image and FFmpeg `motion`. Add the optional `wan` object only to scenes that
should use generated motion. Selecting **FFmpeg Motion** renders all scenes with
FFmpeg and ignores every `wan` object; selecting **Wan 2.2** runs those scenes
with a `wan` object through Wan and automatically falls back to FFmpeg for the
others. Do not add a separate per-scene renderer field.

If the user explicitly requests **Wan for every scene**, treat that as a
package-level creative override: preserve every existing image, narration,
subtitle, motion, transition, and scene order, then add a valid `wan` object to
every scene. Give each scene a narration-matched image-to-video prompt, stable
seed, `frames: 81`, and an appropriate negative prompt. Keep `lip_sync: true`
only for presenter scenes that need speech; use `false` for b-roll and branding.
The hook still uses `steps: 25`; ordinary scenes omit `steps` to inherit the
configured default. This override does not remove FFmpeg compatibility: every
scene retains its image and `motion`, so choosing **FFmpeg Motion** still renders
the entire package without consulting any `wan` object. Repackage as a new
version unless the user explicitly asks to overwrite the previous ZIP.

### Long-form YouTube pacing

For a roughly 10-minute 16:9 video, outline 18-22 narrative chapters and use
70-100 visual scenes/shots. Refresh the visual every 4-8 seconds; only hold a
deliberately important tableau for 8-10 seconds. Treat a scene as a visual shot
rather than a whole chapter. Reserve approximately 10-15 Wan 2.2 hero shots
for high-stakes moments and use FFmpeg Motion for the remaining explanatory
shots. Each added shot must advance the story, comparison, or emotion—not just
create motion.

At render time, AutoClip's Create Video UI offers `use_json`, `vertical`, and
`youtube`. The first preserves the ZIP resolution; the latter two override it
only for the submitted job. State the selected mode in the preview and check
that the completed video metadata reports the expected output resolution.

## Mandatory Mamase outro asset and short-form ending

Every Reel ends with `assets/branding/mamase/reels-end-scene.png` as the locked
artwork master. Never crop, regenerate, recolor, retouch, change its text, or
add another logo. Keep the source file untouched. Because the master is
941x1672 while AutoClip Reel packages use 1080x1920, create a proportionally
resized 1080x1920 package copy without changing its composition or artwork.

End the preceding content scene on the story's memorable scientific idea,
twist, or implication. Then conclude with the approved topic-specific discussion
CTA question in the final branding scene:

```json
{
  "narration": "ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?",
  "tts_text": "ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?",
  "subtitle": "ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?",
  "show_subtitle": true,
  "motion": "slow_zoom_in",
  "motion_speed": "slow",
  "motion_intensity": 0.1,
  "focus": "center",
  "transition": "none"
}
```

The CTA must be a single short question matching the topic that invites audience
discussion, predictions, or philosophical reactions. Strictly forbid generic
engagement language ("กดไลก์", "กดแชร์", "กดติดตาม", "คอมเมนต์คุยกัน", "ขอบคุณที่รับชม").
The legacy canned outro is retired. The CTA is the final spoken sentence with
zero spoken words after it.

Give it the package's next ordered scene id ending in `brand-outro` and a
relative image path in `images/`; it must remain the final `script.json` scene.
The required narration is schema-valid and must not be empty. FFmpeg motion is always
available; include a Wan plan only when Wan motion adds value.

## Required ZIP contract

The ZIP root must contain:

```text
script.json
video-metadata.json
images/<scene>.png|jpg|webp
audio/                 # optional BGM only
```

Use safe relative POSIX image paths. `video-metadata.json` must include a
clickable Thai title and concise description with Mamase wording and relevant
hashtags. Never put Pod IPs, keys, URLs, reference-audio paths, or API
credentials in a ZIP.

## Voice compatibility

## Thai TTS pronunciation

Treat `narration` as the viewer-facing script, but treat `tts_text` as the
spoken script whenever a scene contains an English word, acronym, proper name,
foreign unit, scientific designation, or number that a Thai TTS engine may
mispronounce. Keep the correctly spelled term in `narration` and subtitles;
provide Thai phonetic speech in `tts_text` for the whole scene. Examples:
`Parker Solar Probe` → `พาร์กเกอร์ โซลาร์ โพรบ`, `Hubble` → `ฮับเบิล`,
`N44` → `เอ็น สี่สิบสี่`, and `Superbubble` → `ซูเปอร์บับเบิล`.

Do not guess a machine's English pronunciation. Add `tts_text` proactively
whenever any such term appears, then listen to the scene preview in AutoClip
before final publishing. Keep names, dates, measurements, and abbreviations
natural in Thai speech rather than spelling individual Latin characters unless
that is the intended pronunciation.

For a package using `"provider": "local"`, use only one of
`thai-male-01`, `thai-female-01`, `thai-male-02`, or `thai-female-02` in
`voice.voice`. Do not use Kokoro names such as `m_young_clear` in a Local
package. RunPod F5 packages may keep the canonical `thai-male-01` placeholder:
the actual identity is the protected configured reference voice, not a ZIP
voice-name roster.

Select motion and transitions that serve the scene; `fade` is the safe default.
Validate all asset paths and run AutoClip's `PackageService` validation before
delivery. For a technical package, state unavailable runtime dependencies
instead of claiming a full render was tested.
