from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import ReelTtsSettings, TtsSettings
from app.domain.models import Script


MAMASE_REEL_HOOK_STYLE = """Speak in an energetic, curious Thai male voice.

Deliver the opening question with immediate surprise and excitement, as if you have just discovered something unbelievable and need to tell a friend.

Use a slightly faster pace than normal.

Strongly emphasize the contrast between the surprising fact and the final mystery question.

Keep the delivery conversational, playful, and spontaneous.

Do not shout.
Do not sound like a commercial, movie trailer, news presenter, or exaggerated YouTuber.

The Hook is normally designed for the first 3–5 seconds."""

MAMASE_REEL_NORMAL_STYLE = """Speak like a charismatic Thai science storyteller with a playful personality.

Sound curious, friendly, warm, and conversational, as if telling an interesting science story to a friend.

Keep the delivery natural and connected, with light energy and genuine excitement when surprising facts appear.

Use small natural pauses for emphasis and comedic timing when appropriate.

Do not rush.
Do not over-dramatize.
Do not sound like a news anchor, lecturer, movie trailer, advertisement, or exaggerated YouTuber.

Keep the tone playful and engaging, but still clear enough for scientific explanations."""


@dataclass(frozen=True)
class ResolvedReelTts:
    mode: str
    voice: str
    speed: float
    style: str
    source: str


def is_reel_script(script: Script) -> bool:
    width, height = (int(value) for value in script.project.resolution.split("x", 1))
    return height > width


def _nonempty(value: str | None) -> str | None:
    return value.strip() if value and value.strip() else None


def resolve_reel_tts_config(
    script: Script,
    scene_index: int,
    saved: ReelTtsSettings | None,
    safe: TtsSettings,
) -> ResolvedReelTts:
    """Resolve one Reel scene without mutating job or global settings."""
    job = script.reel_tts
    job_normal = job.normal if job and job.normal else None
    job_hook = job.hook if job and job.hook else None
    normal_speed = next(
        value for value in (
            job_normal.speed if job_normal else None,
            saved.normal_speed if saved else None,
            1.05,
            script.voice.speed,
            safe.google_speaking_rate,
        ) if value is not None
    )
    normal_style = (
        _nonempty(job_normal.style if job_normal else None)
        or _nonempty(saved.normal_style if saved else None)
        or MAMASE_REEL_NORMAL_STYLE
        or _nonempty(script.voice.style_prompt)
        or safe.google_style_prompt
    )
    voice = (
        _nonempty(job.voice if job else None)
        or _nonempty(saved.voice if saved else None)
        or "Fenrir"
        or script.voice.voice
        or safe.google_voice
    )

    is_hook = scene_index == 0
    if is_hook:
        # A partial job override intentionally falls back within that same job
        # before consulting persistent or built-in defaults.
        speed = next(
            value for value in (
                job_hook.speed if job_hook else None,
                job_normal.speed if job_normal else None,
                saved.hook_speed if saved else None,
                saved.normal_speed if saved else None,
                1.10,
                normal_speed,
            ) if value is not None
        )
        style = (
            _nonempty(job_hook.style if job_hook else None)
            or _nonempty(job_normal.style if job_normal else None)
            or _nonempty(saved.hook_style if saved else None)
            or _nonempty(saved.normal_style if saved else None)
            or MAMASE_REEL_HOOK_STYLE
            or normal_style
        )
    else:
        speed = normal_speed
        style = normal_style

    if job and any(
        value is not None
        for value in (
            job.voice,
            job_hook.speed if is_hook and job_hook else None,
            job_hook.style if is_hook and job_hook else None,
            job_normal.speed if job_normal else None,
            job_normal.style if job_normal else None,
        )
    ):
        source = "job"
    elif saved and any(
        value is not None
        for value in (saved.voice, saved.hook_speed, saved.normal_speed, saved.hook_style, saved.normal_style)
    ):
        source = "saved settings"
    elif voice == "Fenrir" and style in {MAMASE_REEL_HOOK_STYLE, MAMASE_REEL_NORMAL_STYLE}:
        source = "built-in default"
    else:
        source = "fallback"
    return ResolvedReelTts("HOOK" if is_hook else "NORMAL", voice, float(speed), style, source)
