---
name: mamase-clip-producer
description: >-
  Expert skill for creating vertical short-form video scripts, JSON contracts, and ZIP content packages
  for Mamase (จักรวาลของใจ) on the AutoClip platform following start.md, agent.md, and the Parker/Tianwen-2 benchmarks.
  Use when writing video scripts, organizing scenes, formatting script.json, configuring camera motion/transitions/Wan 2.2,
  or building release ZIP packages for AutoClip.
---

# Mamase Clip Producer Skill

This skill guides the end-to-end creation of vertical short-form videos for the **Mamase — จักรวาลของใจ** channel on the **AutoClip** platform according to [`/Users/zengcode/projects/autoclip/start.md`](file:///Users/zengcode/projects/autoclip/start.md).

For full details, reference files, and validation scripts, see also [`../mamase-autoclip-package/SKILL.md`](file:///Users/zengcode/projects/autoclip/.agents/skills/mamase-autoclip-package/SKILL.md).

---

## 🛑 Mandatory Review Gate (Workflow Policy)

> **IMPORTANT**: Before every production round, you MUST show the complete script (minimum 8–9 scenes) to **พี่พี** for review.
> **DO NOT** generate final images, `script.json`, or ZIP files until the script is explicitly approved.
> Once approved, generate all master images and package assets autonomously without asking the user for prompt-by-prompt inputs.

---

## Production Workflow

### Step 1: Script Writing & Review Gate
1. Select/receive a topic aligned with approved channel themes (strange places worldwide, mysterious science, unexpected space stories, nature extremes, trending verified wonders).
2. Structure the script into the standard **9-scene format** (8 story scenes + 1 Mamase brand outro).
3. Write narration in the approved **charismatic science storyteller persona** (curious, playful, warm, slightly cheeky).
4. Present the complete script draft in clear Thai (UTF-8) including scene visuals, narration text, suggested camera motions, and transitions for พี่พี's review.
5. Obtain approval before generating images or JSON.

### Step 2: Autonomous Master Image Generation (Real Science + Cinematic Documentary)
1. **Benchmark**: Follow [`assets/parker_solar_probe_reel/visual-reference.md`](file:///Users/zengcode/projects/autoclip/assets/parker_solar_probe_reel/visual-reference.md) and [`assets/tianwen-2-quasi-satellite-reel/images/`](file:///Users/zengcode/projects/autoclip/assets/tianwen-2-quasi-satellite-reel/images/).
2. **Quality Standards**:
   - Resolution: strictly **1080x1920 PNG** (9:16 vertical).
   - Use authentic astronomy/spacecraft data from NASA, JWST, ESO, Hubble, ESA.
   - Active composition fills **70–80%** of the frame (Foreground + Midground + Background depth).
   - Subtitle safe area (**y: 1380–1920**) is clean, calm, and dark.
   - Scene 01: Narrative Key Art with canonical presenter (`mamase-presenter-v1`), directional rim lighting, and Sukhumvit Set Bold typography top-left.
   - Scenes 02+: 100% clean documentary visuals with ZERO in-image text/HUD/logos/watermarks.
3. Save durable master images in `assets/<topic_reel>/`. Never rely on `dist/` as durable reference.

### Step 3: JSON & ZIP Package Assembly
1. Create `script.json` adhering strictly to the JSON contract:
   - Voice: `google-gemini`, `Fenrir`, speed `1.3`, charismatic storyteller prompt.
   - Mandatory phonetic `tts_text` overrides for all foreign terms, acronyms, and numbers.
   - Scene 01 Wan: `steps: 25`, `seed: 901`, `frames: 81`, `lip_sync: true`, `character_id: "mamase-presenter-v1"`.
2. Ensure final scene uses the canonical locked Mamase Brand Outro asset and wording.
3. Create `video-metadata.json` with title, description, and hashtags.
4. Archive at ZIP root without parent wrapping folder:
   ```text
   <package-name>.zip
   ├── script.json
   ├── video-metadata.json
   ├── images/
   │   ├── scene-01-hook.png
   │   ├── ...
   │   └── scene-09-mamase-outro.png
   └── audio/ (optional)
   ```
5. Validate package using `.agents/skills/mamase-autoclip-package/scripts/validate_package.py` and `unzip -t`.
6. Write documentation manifest to `docs/<topic>-reel-asset-manifest.md`.

---

## Core References

- [Main Package Runbook](../mamase-autoclip-package/SKILL.md)
- [Visual Standard Reference](../mamase-autoclip-package/references/visual-standard.md)
- [Narrative Voice & TTS Reference](../mamase-autoclip-package/references/narrative-voice.md)
- [Script JSON & Metadata Contract](../mamase-autoclip-package/references/script-contract.md)
- [Mamase Brand Outro Spec](../mamase-autoclip-package/references/brand-outro.md)
