---
name: khon-nuea-duang-zodiac
description: Build or maintain คนเหนือดวง weekly 12-zodiac AutoClip batches, including JSON import, fixed-template date overlays, Thai TTS, MP4 rendering, publishing metadata, CSV export, retry, and History. Use for ดวง 12 ราศี or คนเหนือดวง work; do not apply Mamase branding.
---

# คนเหนือดวง — Weekly 12 Zodiac

Keep this workflow isolated from Mamase Reels and Podcast. Its permanent UI is
`/zodiac-weekly`, and its fixed artwork lives in `assets/12ราศี`.

## Batch contract

Accept one `autoclip.zodiac-weekly-batch.v1` JSON containing a `week` and either
an empty `zodiacs` list (safe generated defaults) or all 12 unique readings.
Produce 12 independently retryable jobs and deliver:

- 12 MP4 files named `01-capricorn.mp4` through `12-sagittarius.mp4`
- 12 AutoClip ZIP packages
- 12 durable `*.metadata.json` files
- one UTF-8 spreadsheet-safe `youtube-upload.csv` with exactly 12 rows

Use each matching fixed master image and change only its weekly date plaque.
Never regenerate, rewrite, or cover the embedded zodiac name, English name,
birth range, artwork, or คนเหนือดวง branding.

Honor the JSON `visual` contract. Keep `use_template_as_primary_visual: true`,
`generate_new_images: false`, and `date_overlay.preserve_master_image: true`.
`date_overlay.text_source` is `week.display_th`. When
`motion.enabled: false` with `preset: none`, write `motion: none` to every
scene; do not silently add pan, zoom, float, or other movement.

## Locked voice and script

- Provider: Google Gemini TTS
- Voice: `Iapetus`
- Language: `th-TH`
- Speed: `1.10`
- Style source of truth: `TTS_STYLE` in `app/services/zodiac_service.py`
- Mood: warm, calm, confident, slightly mysterious, reassuring; never a news
  anchor, advertisement, theatrical fortune teller, horror voice, chant, or
  exaggerated whisper
- Keep pacing natural, smooth, and slightly brisk. Avoid slow drawn-out
  delivery, elongated vowels, and long dramatic pauses.
- Spoken order: Hook within 1–3 seconds → Work → Money → Love → Advice → an
  encouraging close that invites the listener back next week
- Curator hook templates are fallback only. Do not force all 12 signs into the
  same hook structure. Across each weekly batch, hooks must remain distinct in
  wording, central tension, and curiosity pattern.
- Hook editorial rules: target 45–90 Thai characters (hard maximum 120 characters;
  shorten if over 120). When shortening an overlong hook, prefer sources in this
  strict priority order: 1. original hook meaning (sub-clauses), 2. overview central
  tension, 3. work/finance/love strongest tension, 4. advice only as LAST resort.
  Do not generate a hook that is merely passive advice without tension or contrast.
  Strip polite endings (`ครับ`, `ค่ะ`, `นะครับ`, `นะคะ`, `ครับผม`) from
  the hook opening only (preserve in body). Never duplicate body section text
  (overview, work, finance, love, advice) in the hook. Preserve strong DeepSeek hooks
  possessing semantic curiosity or tension even if they do not contain predefined
  keyword tokens. Clean duplicated section prefixes (e.g. 'ด้านความรัก ความรัก...' -> 'ด้านความรัก...').

`1.10` is the fallback speed. If the batch JSON explicitly supplies a valid
`voice.speed`, preserve that value in all 12 generated `script.json` files.

Describe predictions as tendencies, opportunities, or things to consider.
Avoid deterministic claims about death, disaster, illness, guaranteed wealth,
or other harmful outcomes.

## Publishing metadata is not rendering

Generate a truthful, unique title, concise teaser description, focused hashtags,
search tags, week, filename, visibility, language, and made-for-kids value for
every sign. Always include:

`การดูดวงเป็นความเชื่อส่วนบุคคล โปรดใช้วิจารณญาณในการรับชม`

Editing or regenerating Title, Description, Hashtags, or Tags must never submit
a render job, invoke TTS, or encode scenes. Update JSON and CSV immediately.
For an already completed MP4, synchronize container tags only with FFmpeg
stream-copy/remux when the metadata hash changes; never re-encode the video.

Before completing a batch, verify 12 unique zodiac IDs, 12 unique truthful
titles, correct sign/date/filename references, 12 MP4s, 12 metadata records, and
12 CSV data rows. Keep status/logging per child, retry failed children only, and
persist enough state to reopen the batch after restart.

## Weekly History

Use `/zodiac-history` as the dedicated คนเหนือดวง History. One weekly batch is
the primary management unit for viewing, expanding 12 child jobs, bulk retry,
MP4-only download, complete ZIP download, and safe batch deletion. A partial
batch remains downloadable and its complete archive must include
`batch-report.json`. Delete only the exact batch directory and recorded child
job directories under the workspace; never touch `assets/12ราศี`.
