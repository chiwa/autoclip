---
name: autoclip-content
description: Create, revise, and package Thai short-form video content for the AutoClip project, including script review, vertical scene imagery, script.json, transitions, branding outro, and an AutoClip-ready ZIP. Use for Mamase channel content or when preparing packages for AutoClip; do not use for changing the AutoClip application itself.
---

# AutoClip Content

Create accurate, engaging Thai short-form videos for YouTube Shorts, TikTok, and Reels under the channel **Mamase — จักรวาลของใจ**.

## Required workflow

1. Draft the complete Thai script first. Include scene order, narration, intended visual, approximate duration, motion, and transition.
2. Stop after the script draft and ask พี่พี to review it. Do not generate images, `script.json`, or a ZIP until explicit approval.
3. Revise the complete script when feedback arrives and request approval again if the revision changes content materially.
4. After approval, create diverse 9:16 scene images, then create `script.json`, validate every referenced path, and package the ZIP.
5. Preserve JSON scene order exactly. End every finished clip with the reusable Mamase branding scene.

Never put API keys, `.env`, credentials, private tokens, or unrelated project files in a content package or this skill.

## Editorial direction

- Cover strange places, surprising science, unexpected space stories, and timely topics.
- Lead with a strong factual hook, explain the mechanism clearly, add a meaningful reveal, then close with wonder rather than sensationalism.
- Write natural spoken Thai. Avoid misleading certainty, invented facts, graphic imagery, and claims that confuse myth with evidence.
- Prefer approximately 55–70 seconds when the subject supports it, with enough scenes to keep the visuals varied. Duration is an editorial target, not a fixed schema field.
- Use documentary-style, non-graphic visuals. Vary aerial, wide, close-up, explanatory, wildlife, and atmospheric compositions where relevant.
- Branding narration: `ค้นพบโลก ค้นพบใจ กับ Mamase`
- Branding subtitle: `Mamase\nจักรวาลของใจ`

## References and assets

- Before creating JSON or a ZIP, read [references/package-contract.md](references/package-contract.md).
- For the reusable channel identity and outro rules, read [references/brand.md](references/brand.md).
- Reuse [assets/mamase-brand-outro.png](assets/mamase-brand-outro.png) for the final scene unless พี่พี explicitly approves a replacement.

## Delivery check

The ZIP root must contain only supported package content, with `script.json` at the root and referenced images under `images/`. Verify JSON validity, unique scene IDs, relative POSIX paths, actual asset existence, supported presets, and ZIP root layout before delivery.
