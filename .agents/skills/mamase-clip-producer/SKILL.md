---
name: mamase-clip-producer
description: >-
  Expert skill for creating vertical short-form video scripts, JSON contracts, and ZIP content packages
  for Mamase (จักรวาลของใจ) on the AutoClip platform. Use when writing video scripts, organizing scenes,
  formatting script.json, configuring camera motion/transitions, or building release ZIP packages for AutoClip.
---

# Mamase Clip Producer Skill

This skill guides the end-to-end creation of vertical short-form videos for the **Mamase — จักรวาลของใจ** channel using the **AutoClip** video generation pipeline.

---

## 🛑 Mandatory Review Gate (Workflow Policy)

> **IMPORTANT**: Before every production round, you MUST show the complete 8-scene script to **พี่พี** for review.
> **DO NOT** generate final images, `script.json`, or ZIP files until the script is explicitly approved.

---

## Production Workflow

### Step 1: Script Writing & Review
1. Brainstorm or receive a topic based on approved channel themes (strange places worldwide, mysterious science, unexpected space stories, nature extremes, trending verified wonders).
2. Structure the script into the standard **8-scene format** (7 story scenes + 1 Mamase brand outro).
3. Present the script draft in clear Thai (UTF-8) including scene visuals, narration text, suggested camera motions, and transitions.
4. Solicit feedback and obtain approval from **พี่พี**.

### Step 2: Asset & JSON Preparation (After Approval)
1. Verify vertical (9:16) image assets (1080x1920 recommended; JPG, PNG, or WebP).
2. Ensure Scene 08 uses the fixed Mamase Brand Outro asset: `images/scene-08-brand-outro.png`.
3. Construct `script.json` adhering strictly to the JSON contract.
4. Verify all asset paths are relative to the ZIP root (e.g. `images/scene-01.png`) and avoid path traversal (`../`).

### Step 3: ZIP Package Assembly & Validation
1. Create directory structure:
   ```text
   <package-name>/
   ├── script.json
   ├── images/
   │   ├── scene-01.png
   │   ├── ...
   │   └── scene-08-brand-outro.png
   └── audio/ (optional)
       └── bgm.mp3
   ```
2. Archive into a `.zip` file.
3. Validate and submit to AutoClip API or Docker test runner.

---

## Core References

- [AutoClip System Context & Guidelines](./references/autoclip-context.md)
- [Script JSON Contract & Motion/Transition Reference](./references/script-contract.md)
- [8-Scene Production Template & Storytelling Guide](./references/production-template.md)
- [Mamase Brand Assets & Outro Spec](./references/brand-assets.md)
