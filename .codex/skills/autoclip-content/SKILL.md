---
name: autoclip-content
description: Create, revise, and package Thai short-form video content for the AutoClip project, including script review, vertical scene imagery, script.json, transitions, channel branding, and an AutoClip-ready ZIP. Use for Mamase or Thai Java Zone channel content, or when preparing packages for AutoClip; do not use for changing the AutoClip application itself.
---

# AutoClip Content

Create accurate, engaging Thai short-form videos for YouTube Shorts, TikTok,
and Reels for **Mamase — จักรวาลของใจ** and **Thai Java Zone**.

## Required workflow

1. Draft the complete Thai script first. Include scene order, narration, intended visual, approximate duration, motion, and transition.
2. Stop after the script draft and ask พี่พี to review it. Do not generate images, `script.json`, or a ZIP until explicit approval.
3. Revise the complete script when feedback arrives and request approval again if the revision changes content materially.
4. After approval, create diverse 9:16 scene images, then create `script.json`, validate every referenced path, and package the ZIP.
5. Preserve JSON scene order exactly. Use the outro and branding belonging to
   the requested channel; never place Mamase branding in a Thai Java Zone clip
   or Thai Java Zone branding in a Mamase clip.

Never put API keys, `.env`, credentials, private tokens, or unrelated project files in a content package or this skill.

## Mamase editorial direction

- Cover strange places, surprising science, unexpected space stories, and timely topics.
- Lead with a strong factual hook, explain the mechanism clearly, add a meaningful reveal, then close with wonder rather than sensationalism.
- Write natural spoken Thai. Avoid misleading certainty, invented facts, graphic imagery, and claims that confuse myth with evidence.
- Prefer approximately 55–70 seconds when the subject supports it, with enough scenes to keep the visuals varied. Duration is an editorial target, not a fixed schema field.
- Use documentary-style, non-graphic visuals. Vary aerial, wide, close-up, explanatory, wildlife, and atmospheric compositions where relevant.
- Branding narration: `ถ้าชอบเรื่องราวอวกาศ จักรวาล วิทยาศาสตร์ และเทคโนโลยี กดไลก์ กดแชร์ และกดติดตาม แล้วมาค้นพบโลก ค้นพบใจ ไปกับ Mamase จักรวาลของใจครับ`
- Branding `tts_text`: `ถ้าชอบเรื่องราวอวกาศ จักรวาล วิทยาศาสตร์ และเทคโนโลยี กดไลก์ กดแชร์ และกดติดตาม แล้วมาค้นพบโลก ค้นพบใจ ไปกับ มามาเซ่ จักรวาลของใจครับ`
- Branding subtitle: `กดไลก์ · แชร์ · ติดตาม\nMamase จักรวาลของใจ`
- Keep the call to action warm and conversational. Do not shout, pressure the
  viewer, or insert multiple promotional interruptions earlier in the clip.

## Thai Java Zone visual style bible

When the requested channel or package is **Thai Java Zone**, keep the existing
workflow and package checks, but use this channel-specific visual direction
instead of the Mamase cinematic-documentary art direction:

- Every image is a clean, modern software-engineering explainer with exactly
  one clear concept per scene.
- Prefer realistic, professional developer workspaces, backend systems, or
  software-architecture visuals that directly support the scene narration.
- Use minimal clutter, balanced composition, clear visual hierarchy, soft
  natural lighting, a dark neutral tech background, subtle depth, and a
  vertical 9:16 frame with motion-safe and subtitle-safe placement.
- Do not include text, subtitles, watermarks, logos, fake UI labels, or
  model-generated interface copy unless the user explicitly requests it.
- Reject cyberpunk, futuristic holograms, fantasy technology, excessive neon,
  glowing monoliths, and sci-fi movie-poster aesthetics.
- Build every scene prompt by inheriting this complete base style and adding
  only the scene-specific subject and action. Never invent a new art direction,
  palette, lighting language, or visual world for an individual scene.

## References and assets

- Before creating JSON or a ZIP, read [references/package-contract.md](references/package-contract.md).
- For Mamase channel identity and outro rules, read [references/brand.md](references/brand.md).
- For a Mamase clip, reuse [assets/mamase-brand-outro.png](assets/mamase-brand-outro.png) for the final scene unless พี่พี explicitly approves a replacement. For Thai Java Zone, use only its own approved branding assets.

## Delivery check

The ZIP root must contain only supported package content, with `script.json` at the root and referenced images under `images/`. Verify JSON validity, unique scene IDs, relative POSIX paths, actual asset existence, supported presets, and ZIP root layout before delivery.
