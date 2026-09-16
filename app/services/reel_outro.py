from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config.settings import ReelOutroSettings
from app.domain.errors import AppError
from app.domain.models import ReelOutroConfig, Scene, Script


LEGACY_OUTRO_MARKERS = ("brand-outro", "mamase-outro", "reels-end-scene", "reels-end-scence")


@dataclass(frozen=True)
class ResolvedReelOutro:
    enabled: bool
    image: Path | None
    duration: float
    bgm_fade_out: bool
    source: str


def is_legacy_outro_scene(scene: Scene) -> bool:
    haystack = f"{scene.id} {scene.image}".lower()
    return scene.role == "outro" or any(marker in haystack for marker in LEGACY_OUTRO_MARKERS)


def migrate_legacy_outro_scene(script: Script) -> tuple[Script, str | None]:
    """Move legacy end-card speech onto the prior content image.

    This preserves every spoken word while ensuring the branding image itself
    is never treated as a narration/subtitle scene.
    """
    if len(script.scenes) < 2 or not is_legacy_outro_scene(script.scenes[-1]):
        return script, None
    legacy = script.scenes[-1]
    previous = script.scenes[-2]
    narration = " ".join(part.strip() for part in (previous.narration, legacy.narration) if part and part.strip())
    previous_tts = previous.tts_text or previous.narration
    legacy_tts = legacy.tts_text or legacy.narration
    tts_text = " ".join(part.strip() for part in (previous_tts, legacy_tts) if part and part.strip())
    previous_subtitle = previous.subtitle if isinstance(previous.subtitle, str) else previous.narration
    legacy_subtitle = legacy.subtitle if isinstance(legacy.subtitle, str) else legacy.narration
    subtitle = " ".join(part.strip() for part in (previous_subtitle, legacy_subtitle) if part and part.strip())
    merged = previous.model_copy(update={
        "narration": narration,
        "tts_text": tts_text,
        "subtitle": subtitle,
        "keywords": [*previous.keywords, *(item for item in legacy.keywords if item not in previous.keywords)],
        "role": "content" if previous.role == "outro" else previous.role,
    })
    return script.model_copy(update={"scenes": [*script.scenes[:-2], merged]}), legacy.image


def resolve_reel_outro(
    script: Script,
    package_root: Path,
    saved: ReelOutroSettings,
    legacy_image: str | None = None,
) -> ResolvedReelOutro:
    config = script.outro
    enabled = config.enabled if config is not None else saved.enabled
    duration = config.duration if config is not None else saved.duration
    fade = config.bgm_fade_out if config is not None else saved.bgm_fade_out
    requested = config.image if config is not None else legacy_image
    source = "job" if config is not None else "saved settings"
    if not enabled:
        return ResolvedReelOutro(False, None, float(duration), bool(fade), source)

    candidates: list[Path] = []
    if requested:
        candidates.append(package_root / requested)
    configured = saved.image
    if not configured.is_absolute():
        configured = Path.cwd() / configured
    candidates.append(configured)
    for candidate in candidates:
        if candidate.is_file() and candidate.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            return ResolvedReelOutro(True, candidate.resolve(), float(duration), bool(fade), source)
    raise AppError(
        "REEL_OUTRO_ASSET_NOT_FOUND",
        "Mamase Reel outro is enabled but its image is missing or unreadable",
        {"image": requested or str(saved.image)},
    )
