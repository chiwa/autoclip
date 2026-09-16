# Mamase Brand Outro Specification

Every Mamase Reel ends with a separate silent branding post-roll. It is not a
story scene and must not appear in the `scenes` array of a new package.

| Attribute | Canonical value |
| :--- | :--- |
| Position | After the final content narration and subtitle end |
| Master asset | `assets/branding/mamase/reels-end-scene.png` |
| Duration | `2.0` seconds (allowed `1.5–2.5`) |
| Narration / TTS | None |
| Subtitle | None |
| BGM | Continue briefly, then fade to silence |

Use the optional top-level `outro` contract from
`docs/mamase-reels-standard.md`. AutoClip resolves the global locked asset, so
packages normally do not need a duplicate image. Never regenerate, recolor,
retouch, crop, change its text, or add another logo. Legacy narrated outro
scenes are accepted only for backward compatibility and are migrated by
AutoClip; never create them in new work.
