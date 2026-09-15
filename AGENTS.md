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

For Mamase Reels, Shorts, or TikTok work, additionally read
`/Users/zengcode/projects/autoclip/.agents/skills/mamase-reels/SKILL.md` and
`/Users/zengcode/projects/autoclip/.agents/skills/mamase-reels-cover/SKILL.md`.
Its locked logo, mobile QA, and final-scene rules override older guidance.
Every Scene 01 must inspect
`/Users/zengcode/projects/autoclip/assets/branding/mamase/reference/mamase-reels-editorial-poster-master.png`.
This is the permanent Premium Editorial Science Poster master for future
Mamase Reel covers; match its visual language and quality while adapting the
composition, action, setting, and scientific subjects to each topic.
Target a dense 45–60 seconds by default (acceptable: 60–75 seconds; if over
75s, compress and revise script before returning). Treat the `Mamase Reel Hook Gate`
as a blocking QA gate: do not proceed to image generation, TTS, or rendering until
the hook passes. The first 1–3 seconds MUST stop scrolling with a truthful,
scientifically defensible surprise, contradiction, or curiosity question (never
greetings, channel intros, "วันนี้เราจะมา...", "รู้หรือไม่...", definitions, or slow setup).
Spoken TTS must start directly with the hook (matching `hook` metadata identically),
and the first visual must reinforce the hook immediately with a colossal, dominating
hero subject (never generic backgrounds or tiny pasted subjects). Deliver a mini-wow
or reveal every 10–15 seconds to sustain retention without lecture format. Locked
Mamase Reel TTS defaults: Google Gemini `Fenrir`, `th-TH`, default speed `1.05`.

Key non-negotiable rules:

- For **คนเหนือดวง / ดวง 12 ราศี**, use the isolated `/zodiac-weekly`
  workflow. One weekly batch JSON must produce 12 zodiac MP4 files, 12 durable
  metadata JSON records, and one UTF-8 `youtube-upload.csv`. Use only the fixed
  masters in `assets/12ราศี`; alter the weekly date plaque only. Keep scripts,
  jobs, History type, branding, and output separate from Mamase.
- Zodiac publishing metadata is a separate layer from rendering. Editing or
  regenerating title, description, hashtags, or search tags must never invoke
  TTS or scene rendering. Keep metadata truthful to each reading, include the
  standard belief disclaimer, persist it across restart, and stream-copy/remux
  completed MP4 container tags only when synchronization is needed.
- Locked คนเหนือดวง TTS defaults: Google Gemini `Iapetus`, `th-TH`, speed
  `1.10`, using the warm/calm/confident/slightly mysterious style in
  `app/services/zodiac_service.py`. Spoken structure is Hook → Work → Money →
  Love → Advice → encouraging close; the hook begins within 1–3 seconds.
- Group คนเหนือดวง jobs by weekly parent batch in the dedicated
  `/zodiac-history` page. Treat the batch as the unit for view, retry, bulk
  download/archive, and deletion while retaining access to all 12 child jobs.

- For every Thai Java Zone script, shot list, scene plan, image, or motion
  prompt, enforce the shared visual style bible in `agent.md` and `start.md`.
  Every scene inherits one clean modern software-engineering explainer style;
  never invent a separate visual direction per scene.
- Preserve the ZIP contract: `script.json` and `images/` at archive root;
  `audio/` is optional; all asset paths are safe relative POSIX paths.
- Present the complete script and scene plan for review before generating
  images or the final ZIP, unless the user explicitly approves autonomous
  completion or requests a technical test package.
- Use the approved Mamase visual identity and mandatory outro rules. Every
  Reel concludes with one short question naturally inviting discussion matching
  the topic (opinion, prediction, or philosophical reaction). Strictly forbid generic
  CTAs ("อย่าลืมกดไลก์", "คอมเมนต์คุยกันหน่อย", "Thank you for watching", or legacy canned
  outros). The CTA is the final spoken sentence with zero spoken text after it.
  Use "Mamase" or "Mamase REELS" only; strictly no "MAMASE PODCAST", no bilingual
  badges ("AVAILABLE IN THAI & ENGLISH"), and no flags on Reel assets.
- Standard Mamase Reel generation output must return a machine-friendly JSON format
  containing `topic`, `title`, `description`, `estimated_duration_seconds` (<=75s),
  `hook`, `cta`, `tts` (production-ready, starting with hook and ending with cta),
  `voice` (Fenrir 1.05), and `validation` fields. Quick Reel compatibility
  (`{topic, description, tts}`) is preserved.
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
- For Quick Reel work (`/quick-reel`), respect the vertical 9:16 (1080×1920 30 FPS)
  ordered multi-image + single-script architecture (one image remains supported), Gemini Iapetus (1.10) defaults,
  cover/contain image framing, optional Kanit-Bold hook overlay, optional subtitles,
  optional BGM (default disabled), equal image timing with visual-only crossfades,
  and dedicated History routing (`/quick-reel-history`). Never split or crossfade narration audio at image boundaries.
- Quick Reel JSON import accepts `tts` as either one string or an ordered array
  of strings. Array item `tts[n]` belongs to uploaded image `images[n]`; require
  equal counts, generate each narration segment separately, and use its measured
  duration for the matching image. Preserve the legacy single-string mode.
- Quick Reel must expose its Gemini voice style, allow editing it, preview the
  current Voice/Speed/Style combination, and save or restore those preferences
  independently from the other AutoClip workflows.
- After code changes, run relevant tests and restart the native AutoClip service
  when required by `agent.md` or explicitly requested by the user.

If `agent.md` and a task-specific skill conflict, follow the more specific
task instruction while preserving security, repository safety, and explicit
user requirements. Keep this entry point concise; detailed operational history
belongs in `agent.md`, while reusable package procedures belong in the skill.
