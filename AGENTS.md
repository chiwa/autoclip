# AutoClip agent instructions

This file is the standard project-level entry point for every coding agent
working anywhere under this repository.

The single human-facing entry point is
`/Users/zengcode/projects/autoclip/start.md`. Before planning, editing,
reviewing, testing, generating media, or packaging an AutoClip ZIP, read it
completely and follow its routing instructions. Read each routed file once;
do not loop back through this file. Do not rely on remembered conversation
context when repository documentation is available.

For Mamase script, image, JSON, and ZIP work, also read and follow
`/Users/zengcode/projects/autoclip/.codex/skills/mamase-autoclip-package/SKILL.md`
completely. Apply that workflow whenever the task involves creating or revising
a Mamase AutoClip package, even when the user does not explicitly name the
skill.

Key non-negotiable rules:

- For every Thai Java Zone script, shot list, scene plan, image, or motion
  prompt, enforce the shared visual style bible in `agent.md` and `start.md`.
  Every scene inherits one clean modern software-engineering explainer style;
  never invent a separate visual direction per scene.
- Preserve the ZIP contract: `script.json` and `images/` at archive root;
  `audio/` is optional; all asset paths are safe relative POSIX paths.
- Present the complete script and scene plan for review before generating
  images or the final ZIP, unless the user explicitly approves autonomous
  completion or requests a technical test package.
- Use the approved Mamase presenter identity and canonical outro rules from
  `agent.md` and the Mamase skill. Every Mamase outro naturally invites viewers
  to like, share, and follow before ending with the channel's closing line.
- For science and space visuals, read
  `assets/parker_solar_probe_reel/visual-reference.md` and use
  `assets/tianwen-2-quasi-satellite-reel/images/` as the successful autonomous
  master-image workflow example. Reuse the method, not its subject matter.
- A request shaped as `read start.md and create images for <topic>` authorizes
  autonomous master-image production only. Derive the visual story, shot list,
  and per-scene prompts without asking the user to write them; generate,
  visually inspect, and regenerate failed scenes until the set meets the
  benchmark. Do not infer permission to create JSON or a ZIP unless requested.
- A written self-audit is not a substitute for opening every generated image.
  Reject generic, narration-mismatched, watermarked, visually inconsistent,
  pasted-presenter, broken-text, or sub-benchmark assets before delivery.
- Never use `dist/` as the sole durable visual reference because generated
  outputs may be cleaned up.
- Never expose, print, commit, package, or copy API keys, cloud credentials,
  SSH private keys, `.env` contents, or other secrets.
- Preserve unrelated user changes in the working tree. Do not delete, reset,
  overwrite, stage, commit, or push them unless explicitly requested.
- For YouTube Podcast work (`/podcast`), respect the horizontal 16:9 (1920×1080
  30 FPS) single-cover + long-script architecture, Gemini Enceladus bedtime
  defaults, and sidechain audio ducking without affecting standard Reel defaults
  (Fenrir 9:16).
- After code changes, run relevant tests and restart the native AutoClip service
  when required by `agent.md` or explicitly requested by the user.

If `agent.md` and a task-specific skill conflict, follow the more specific
task instruction while preserving security, repository safety, and explicit
user requirements. Keep this entry point concise; detailed operational history
belongs in `agent.md`, while reusable package procedures belong in the skill.
