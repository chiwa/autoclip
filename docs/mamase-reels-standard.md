# Mamase Reels production standard

This is the canonical source of truth for Mamase Reels, Shorts, and TikTok.
Project instructions, skills, prompt templates, and generators must reference
this file instead of defining conflicting timing, scene, subtitle, motion,
hook, or outro rules.

## Runtime and scene architecture

- Target 45–55 seconds. Keep a Reel under 60 seconds unless the story genuinely
  requires more time and retention can support it.
- Normally use 6–9 narrated content scenes, then append the separate post-roll
  outro. Let narration and story beats determine the exact count; never add filler.
- The current renderer supports one visual source per scene. Do not add or claim
  support for `visual_beats`. Split long narration into coherent scenes instead.
- Scene duration comes from generated narration audio. Do not force a fixed
  8–12 second duration and do not auto-split sentences in the renderer.
- Aim for a visual refresh every 3–5 seconds. A single visual held beyond about
  6 seconds should have meaningful safe motion or produce a warning.

## Hook

- The first 1–3 seconds contain both a spoken hook and a directly reinforcing
  visual hook. Show the first visual immediately; no long black fade, logo
  animation, greeting, episode label, or intro music before the hook.
- Keep the hook simple, truthful, scientifically defensible, and curiosity-led.
  The second sentence must immediately continue its promise.
- `role: "hook"` is optional. Without it, scene index 0 is the hook.
- Run the existing **Mamase Reel Hook Gate** before images or TTS.

## Subtitles

- Full captions remain complete so the story works without sound.
- `keywords` is an optional scene array. Emphasize at most 1–3 useful terms per
  scene; never turn the subtitle into word-by-word karaoke.
- Omitting `keywords` preserves the previous subtitle behavior.

## Reel TTS: Hook and normal delivery

- Scene index 0 automatically uses the Hook delivery: Gemini Fenrir, speed
  `1.10`, and the dedicated Mamase Hook Style Prompt.
- Scene index 1 onward automatically uses the Normal delivery: Gemini Fenrir,
  speed `1.05`, and the Mamase science-storytelling style.
- `reel_tts` is optional. No scene-level voice, speed, style, or mode field is
  required. Old packages continue to work and receive the current saved/default
  Reel settings.
- A job may temporarily override Reel TTS without changing saved defaults:

```json
{
  "reel_tts": {
    "voice": "Fenrir",
    "hook": {
      "speed": 1.10,
      "style": "<hook style prompt>"
    },
    "normal": {
      "speed": 1.05,
      "style": "<normal style prompt>"
    }
  }
}
```

Built-in Hook Style Prompt:

```text
Speak in an energetic, curious Thai male voice.

Deliver the opening question with immediate surprise and excitement, as if you have just discovered something unbelievable and need to tell a friend.

Use a slightly faster pace than normal.

Strongly emphasize the contrast between the surprising fact and the final mystery question.

Keep the delivery conversational, playful, and spontaneous.

Do not shout.
Do not sound like a commercial, movie trailer, news presenter, or exaggerated YouTuber.

The Hook is normally designed for the first 3–5 seconds.
```

Built-in Normal Style Prompt:

```text
Speak like a charismatic Thai science storyteller with a playful personality.

Sound curious, friendly, warm, and conversational, as if telling an interesting science story to a friend.

Keep the delivery natural and connected, with light energy and genuine excitement when surprising facts appear.

Use small natural pauses for emphasis and comedic timing when appropriate.

Do not rush.
Do not over-dramatize.
Do not sound like a news anchor, lecturer, movie trailer, advertisement, or exaggerated YouTuber.

Keep the tone playful and engaging, but still clear enough for scientific explanations.
```

Missing Hook style/speed values fall back to Normal values before using saved,
built-in, and safe legacy defaults. Podcast remains a separate workflow and
does not use this scene-position rule.

## Motion and crop safety

- `motion: "auto"` selects motion from `focus`, never pseudo-randomly from an ID.
- Center focus uses a subtle push; left/right and top/bottom focus use
  direction-aware movement. Use explicit light or no motion for text-heavy art.
- Preserve faces, the presenter, dog, typography, and scientific hero objects
  inside safe crop areas throughout the motion.

## Outro and SFX

- Preserve `assets/branding/mamase/reels-end-scene.png`. It is a silent branding
  post-roll, never a narrated story scene. Append it only after the final
  content narration and subtitle have completely ended.
- Default duration is `2.0` seconds (safe configurable range `1.5–2.5`). It has
  no narration, no TTS, and no subtitles. BGM may continue and must fade to
  silence across the post-roll when `bgm_fade_out` is enabled.
- Use the optional top-level contract below; no scene-level outro is required:

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

- Legacy packages whose last scene is `brand-outro`/`mamase-outro` are migrated
  safely: their final spoken sentence is moved onto the preceding content
  image, and the branding art becomes the silent post-roll. New packages must
  not create a narrated outro scene.
- Prefer a memorable scientific idea, twist, or concise topic-specific question.
  Omit a CTA when it weakens the ending.
- `sfx` is an optional extension point such as `reveal` or `transition`. It does
  not promise playback yet and must not add effects to every scene.

## Compatibility and warnings

Optional scene fields:

```json
{
  "role": "hook",
  "keywords": ["กฎฟิสิกส์", "Multiverse"],
  "sfx": "reveal"
}
```

Existing ZIPs and `script.json` files without these fields remain valid and keep
their previous behavior. Retention checks are advisory warnings, not failures:

- `REEL_DURATION_LONG`
- `SCENE_VISUAL_TOO_LONG`
- `HOOK_SCENE_TOO_LONG`
- `LOW_VISUAL_REFRESH_RATE`

Schema errors remain hard failures. Multiple visual beats per narration scene
belong to a future renderer phase and are deliberately not implemented here.
