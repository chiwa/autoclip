# Forever Young Story — AutoClip package rules (draft)

Use the repository's current AutoClip validator as the package authority.

## ZIP contract

```text
script.json
video-metadata.json
images/
audio/                 # optional BGM only
```

- Keep all paths safe, relative, and POSIX-style.
- Reel/TikTok defaults: `1080x1920`, 30 FPS, 9–12 scenes including outro.
- Keep `narration` viewer-facing and use `tts_text` for Thai pronunciation of
  English names, numbers, acronyms, and medical/scientific terms.
- Never include credentials, `.env`, local absolute paths, or service URLs.

## Rendering

Every scene has an image and FFmpeg `motion`, so the package always works in
FFmpeg Motion mode. Add `wan` only to scenes where living motion adds clear
value. If the user explicitly asks for Wan on every scene, add a valid,
narration-matched `wan` object to all scenes while retaining all FFmpeg fields.
Enable lip sync only for an approved presenter scene that visibly speaks.

## Voice and music

- Draft default voice: Google Gemini TTS using a warm adult voice selected in
  AutoClip after listening tests. Do not inherit Mamase's Fenrir default
  automatically.
- Default speed target: `1.0`; adjust after an actual listening test.
- Use warm acoustic, soft soul, gentle lo-fi, or restrained piano textures.
  Keep BGM below narration and avoid sentimental melodrama.

## Outro

The final scene uses the approved Forever Young Story asset and CTA. Never use
the Mamase planet outro or Mamase closing line.
