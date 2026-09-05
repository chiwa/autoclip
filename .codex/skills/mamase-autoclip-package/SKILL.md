---
name: mamase-autoclip-package
description: Create review-ready AutoClip ZIP packages for Mamase จักรวาลของใจ, including Thai narration, vertical scene assets, and required video metadata.
---

# Mamase AutoClip package

Use this skill when creating or revising a Mamase short-form video ZIP. Do not
use it to change AutoClip application code or RunPod setup.

## Creative flow

For a new public clip, present the complete Thai script and scene outline for
approval before generating final assets, unless the user explicitly asks for a
technical test package. Keep scenes in the approved `script.json` order.

Public clips require **at least 8 scenes**, counting the mandatory Mamase
outro. Use more scenes when each additional scene earns its place with a new
fact, visual reveal, explanation, or emotional turn. Do not pad the runtime by
repeating narration, restating a point, or adding decorative b-roll that does
not advance the story.

By default, scene 1 is the recurring original anime presenter with
`character_id: "mamase-presenter-v1"`. Its opening narration uses this form,
adapted only for the topic:

> สวัสดีครับ ยินดีต้อนรับสู่ Mamase จักรวาลของใจ วันนี้เราจะมา...

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

Use human spoken asides when they reveal the storyteller's reaction and make a
fact easier to picture—for example, `แต่เดี๋ยวก่อน...`, `ย้ำนะครับ สมมุติ!`,
or `เอ๊ะ วันนี้แดดก็ดีนี่นา`. They should feel like a real person thinking
alongside the viewer, never like a repeated catchphrase.

Humor must clarify the science, not replace it. Never invent consequences,
imply speculation is confirmed, or overstate a measurement for a punchline.
For Gemini TTS, the channel's default delivery instruction is:

> Read aloud like a charismatic science storyteller with a playful personality.
> Sound curious, friendly, slightly cheeky, and genuinely excited by surprising
> facts. Keep the delivery natural and conversational, with small pauses for
> comedic timing and emphasis. Never sound like a news anchor.

When the Google Gemini TTS provider is selected, use the approved Mamase voice
profile unless the user overrides it: voice `Fenrir`, `pitch: 0`, and
`speakingRate: 1.3`. The target feeling is energetic and clear, playful and
friendly, warm and reassuring—something that makes the listener relaxed and
curious, never rushed, tense, excessively dramatic, or announcer-like. Add:

> Keep the delivery energetic, clear, playful, warm, and reassuring. Make the
> listener feel relaxed and curious, never rushed, tense, or overly dramatic.

For Native AutoClip, Google Gemini TTS uses Application Default Credentials
created with `gcloud auth application-default login` and its quota project. Do
not create, store, or put service-account JSON keys in a ZIP or project config.
The default provider is `google-gemini`; its default voice is `Fenrir`.
When exposing Gemini settings in AutoClip, make the narration-style prompt and
speaking rate editable. Always provide a **คืนค่า Mamase default** control that
restores the approved prompt, Fenrir, and `speakingRate: 1.3`; list voices in
clearly labelled **ชาย** and **หญิง** groups, with Fenrir first.
For a Google Gemini render, narration requests may run concurrently (default:
six scenes per job, configurable through `AUTOCLIP_GOOGLE_TTS_PARALLELISM`)
because each scene is independent. Keep the completed
audio mapped back to the original scene order; use bounded concurrency rather
than unbounded requests.

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

## First-scene hook

Treat the first 2-3 seconds as the package's highest-priority visual. Use the
most arresting truthful image and a short spoken question or reveal; it must be
clear on a phone screen before subtitles are read. For uncertain science,
create intrigue without visualizing an unsupported outcome. For K2-18 b, use a
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

For a normal 45–60 second Mamase Reel, Shorts, or TikTok, create **9–12
scenes** so Thai subtitles remain readable while the visual changes roughly
every 4–6 seconds. Use 12–15 scenes only when the story has real additional
reveals or cutaways. Do not make 20 scenes for a 45–60 second clip; use that
density only for about 75–90 seconds or a deliberately rapid, readable edit.

Make **FFmpeg Motion** the default renderer for short-form packages: it is
fast, stable, and inexpensive. Use Wan only for 0–2 high-value shots—normally
the Mamase presenter hook and optionally one reveal. The remaining shots need
distinct, narration-matched source images with intentional FFmpeg motion and
focus; do not repeatedly zoom the same frame just to increase scene count.

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

## Mandatory Mamase outro

Every package ends with the canonical outro scene from
`dist/planet-nine-extended.zip`; do not make it optional unless the user
explicitly changes the channel branding. Copy that ZIP's `images/scene-08.png`
into the new package as the final scene image and preserve this treatment:

```json
{
  "narration": "ค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ",
  "tts_text": "ค้นพบโลก ค้นพบใจ กับ มามาเซ่ จักรวาลของใจ",
  "subtitle": "ค้นพบโลก ค้นพบใจ\\nMamase จักรวาลของใจ",
  "motion": "slow_zoom_in",
  "motion_speed": "slow",
  "motion_intensity": 0.1,
  "focus": "center",
  "transition": "none",
  "wan": {
    "prompt": "Mamase brand outro, glowing cyan orbiting planet in dark navy space, peaceful and contemplative.",
    "negative_prompt": "watermark, blur, jitter",
    "seed": 98,
    "frames": 81,
    "lip_sync": false
  }
}
```

Give it the package's next ordered scene id and a relative image path in
`images/`; it must remain the final `script.json` scene.

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
