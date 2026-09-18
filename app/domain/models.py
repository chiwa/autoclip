from __future__ import annotations

import re
from datetime import datetime
from pathlib import PurePosixPath
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from app.domain.events import local_now

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
RESOLUTION = re.compile(r"^[1-9]\d*x[1-9]\d*$")


def validate_relative_asset(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or "\\" in value or ".." in path.parts:
        raise ValueError("asset path must be a safe relative POSIX path")
    return value


class Project(BaseModel):
    id: str
    title: str
    language: str
    resolution: str = "1080x1920"
    fps: int = Field(30, gt=0, le=120)

    @field_validator("id")
    @classmethod
    def safe_id(cls, value: str) -> str:
        if not SAFE_ID.fullmatch(value):
            raise ValueError("project.id is not filesystem-safe")
        return value

    @field_validator("resolution")
    @classmethod
    def valid_resolution(cls, value: str) -> str:
        if not RESOLUTION.fullmatch(value):
            raise ValueError("resolution must be WIDTHxHEIGHT")
        return value


class Voice(BaseModel):
    provider: str = Field(min_length=1)
    voice: str = Field(min_length=1)
    speed: float = Field(ge=0.5, le=2.0)
    style_prompt: str | None = Field(default=None, max_length=4_000)


class ReelTtsModeConfig(BaseModel):
    speed: float | None = Field(default=None, ge=0.5, le=2.0)
    style: str | None = Field(default=None, max_length=4_000)

    @field_validator("speed", mode="before")
    @classmethod
    def invalid_speed_is_missing(cls, value: Any) -> Any:
        if value is None:
            return None
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return None
        return parsed if 0.5 <= parsed <= 2.0 else None

    @field_validator("style")
    @classmethod
    def empty_style_is_missing(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None


class ReelTtsConfig(BaseModel):
    voice: str | None = Field(default=None, min_length=1, max_length=80)
    hook: ReelTtsModeConfig | None = None
    normal: ReelTtsModeConfig | None = None

    @field_validator("voice", mode="before")
    @classmethod
    def empty_voice_is_missing(cls, value: Any) -> Any:
        return value.strip() or None if isinstance(value, str) else value


class ReelOutroConfig(BaseModel):
    enabled: bool = True
    image: str = "mamase-reels-end-scence.png"
    duration: float = Field(2.0, ge=1.5, le=2.5)
    bgm_fade_out: bool = True

    @field_validator("image")
    @classmethod
    def safe_image(cls, value: str) -> str:
        return validate_relative_asset(value)


class WanSceneOptions(BaseModel):
    """Optional, portable visual-generation hints for a Wan 2.2 / LTX-Video scene.

    These contain creative intent only. Connection details, reference-audio
    paths, API tokens, and RunPod host details are configuration, never ZIP
    content.
    """
    prompt: str = Field(min_length=3, max_length=2_000)
    negative_prompt: str = Field(default="text, watermark, flicker, jitter", max_length=2_000)
    seed: int | None = Field(default=None, ge=0, le=2_147_483_647)
    frames: int | None = Field(default=None, ge=9, le=300)
    # Optional per-scene quality override. Omit to use the configured default.
    steps: int | None = Field(default=None, ge=1, le=50)
    lip_sync: bool = False
    character_id: str | None = None

    @field_validator("character_id")
    @classmethod
    def safe_character_id(cls, value: str | None) -> str | None:
        if value is not None and not SAFE_ID.fullmatch(value):
            raise ValueError("character_id is not filesystem-safe")
        return value


LtxSceneOptions = WanSceneOptions


class Scene(BaseModel):
    id: str
    image: str
    narration: str = Field(min_length=1)
    tts_text: str | None = None
    subtitle: str | bool | None = None
    show_subtitle: bool = True
    motion: str
    transition: str | None = None
    motion_speed: str = "slow"
    motion_intensity: float | None = None
    focus: str = "center"
    role: str | None = None
    keywords: list[str] = Field(default_factory=list)
    sfx: str | None = None
    wan: WanSceneOptions | None = None
    ltx: WanSceneOptions | None = None

    @model_validator(mode="before")
    @classmethod
    def sync_ai_motion_plan(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "ltx" in data and data["ltx"] is not None and ("wan" not in data or data["wan"] is None):
                data["wan"] = data["ltx"]
            elif "wan" in data and data["wan"] is not None and ("ltx" not in data or data["ltx"] is None):
                data["ltx"] = data["wan"]
        return data

    @field_validator("id")
    @classmethod
    def safe_id(cls, value: str) -> str:
        if not SAFE_ID.fullmatch(value):
            raise ValueError("scene id is not filesystem-safe")
        return value

    @field_validator("image")
    @classmethod
    def safe_image(cls, value: str) -> str:
        return validate_relative_asset(value)

    @field_validator("motion")
    @classmethod
    def supported_motion(cls, value: str) -> str:
        allowed = {"none", "auto", "slow_zoom_in", "slow_zoom_out", "pan_left_to_right", "pan_right_to_left", "pan_up", "pan_down", "zoom_in", "zoom_out", "zoom_in_top_left", "zoom_in_top_right", "zoom_in_bottom_left", "zoom_in_bottom_right", "pan_left_to_right_zoom_in", "pan_right_to_left_zoom_in", "pan_up_zoom_in", "pan_down_zoom_in", "drift_top_left", "drift_top_right", "drift_bottom_left", "drift_bottom_right", "cinematic_push_in", "cinematic_pull_out", "gentle_float", "documentary_pan", "hook_punch_in", "drift_diagonal", "breathing_pulse"}
        if value not in allowed:
            raise ValueError("unsupported motion preset")
        return value

    @field_validator("motion_speed")
    @classmethod
    def valid_motion_speed(cls, value: str) -> str:
        if value not in {"slow", "normal", "fast"}:
            raise ValueError("motion_speed must be slow, normal, or fast")
        return value

    @field_validator("motion_intensity")
    @classmethod
    def valid_motion_intensity(cls, value: float | None) -> float | None:
        if value is not None and not 0.01 <= value <= 0.35:
            raise ValueError("motion_intensity must be between 0.01 and 0.35")
        return value

    @field_validator("focus")
    @classmethod
    def valid_focus(cls, value: str) -> str:
        if value not in {"center", "top", "bottom", "left", "right", "top_left", "top_right", "bottom_left", "bottom_right"}:
            raise ValueError("unsupported focus point")
        return value

    @field_validator("role")
    @classmethod
    def valid_role(cls, value: str | None) -> str | None:
        if value is not None and value not in {"hook", "content", "outro"}:
            raise ValueError("scene role must be hook, content, or outro")
        return value

    @field_validator("keywords")
    @classmethod
    def clean_keywords(cls, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        for value in values:
            keyword = value.strip()
            if keyword and keyword not in cleaned:
                cleaned.append(keyword)
        return cleaned

    @field_validator("sfx")
    @classmethod
    def safe_sfx(cls, value: str | None) -> str | None:
        if value is not None and not SAFE_ID.fullmatch(value):
            raise ValueError("sfx must be a safe identifier")
        return value

    @field_validator("transition")
    @classmethod
    def supported_transition(cls, value: str | None) -> str | None:
        allowed = {
            "none", "fade", "dissolve", "fade_black", "fade_white", "fade_slow", "fade_fast", "fade_grays",
            "wipe_left", "wipe_right", "wipe_up", "wipe_down", "wipe_top_left", "wipe_top_right",
            "wipe_bottom_left", "wipe_bottom_right", "slide_left", "slide_right", "slide_up", "slide_down",
            "smooth", "smooth_left", "smooth_right", "smooth_up", "smooth_down", "circle_open", "circle_close",
            "circle_crop", "rect_crop", "vertical_open", "vertical_close", "horizontal_open", "horizontal_close",
            "zoom_in", "pixelize", "radial", "horizontal_blur", "distance", "squeeze_horizontal",
            "squeeze_vertical", "diagonal_top_left", "diagonal_top_right", "diagonal_bottom_left",
            "diagonal_bottom_right", "horizontal_slice_left", "horizontal_slice_right", "vertical_slice_up",
            "vertical_slice_down",
        }
        if value is not None and value not in allowed:
            raise ValueError("unsupported transition preset")
        return value

    @model_validator(mode="after")
    def default_subtitle(self) -> "Scene":
        if self.subtitle is False or self.subtitle == "none" or self.subtitle == "false" or self.show_subtitle is False:
            self.show_subtitle = False
            self.subtitle = None
        elif isinstance(self.subtitle, str) and self.subtitle.strip():
            self.show_subtitle = True
            self.subtitle = self.subtitle.strip()
        else:
            self.show_subtitle = True
            self.subtitle = self.narration
        return self


class Script(BaseModel):
    project: Project
    voice: Voice = Field(default_factory=lambda: Voice(provider="google-gemini", voice="Fenrir", speed=1.05))
    reel_tts: ReelTtsConfig | None = None
    outro: ReelOutroConfig | None = None
    scenes: list[Scene] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_scene_ids(self) -> "Script":
        ids = [scene.id for scene in self.scenes]
        if len(ids) != len(set(ids)):
            raise ValueError("scene ids must be unique")
        return self


class JobRecord(BaseModel):
    job_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    current_step: str
    error: dict | None = None
    logs: list[dict] = Field(default_factory=list)
    metadata: dict | None = None
    created_at: datetime = Field(default_factory=local_now)
    project_id: str | None = None
    tts_provider: str | None = None
    subtitle_mode: str | None = None
    render_engine: str = "ffmpeg_motion"
    output_format: str = "use_json"

    def api_dict(self) -> dict:
        result = {"jobId": self.job_id, "status": self.status, "progress": self.progress, "currentStep": self.current_step, "error": self.error, "logs": self.logs, "subtitleMode": self.subtitle_mode, "renderEngine": self.render_engine, "outputFormat": self.output_format}
        if self.metadata is not None:
            result["metadata"] = self.metadata
        return result
