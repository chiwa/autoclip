from __future__ import annotations

import re
from datetime import datetime
from pathlib import PurePosixPath

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


class Scene(BaseModel):
    id: str
    image: str
    narration: str = Field(min_length=1)
    subtitle: str | bool | None = None
    show_subtitle: bool = True
    motion: str
    transition: str | None = None
    motion_speed: str = "slow"
    motion_intensity: float | None = None
    focus: str = "center"

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
        allowed = {"none", "auto", "slow_zoom_in", "slow_zoom_out", "pan_left_to_right", "pan_right_to_left", "pan_up", "pan_down", "zoom_in", "zoom_out", "zoom_in_top_left", "zoom_in_top_right", "zoom_in_bottom_left", "zoom_in_bottom_right", "pan_left_to_right_zoom_in", "pan_right_to_left_zoom_in", "pan_up_zoom_in", "pan_down_zoom_in", "drift_top_left", "drift_top_right", "drift_bottom_left", "drift_bottom_right", "cinematic_push_in", "cinematic_pull_out", "gentle_float", "documentary_pan"}
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
        if value is not None and not 0.05 <= value <= 0.35:
            raise ValueError("motion_intensity must be between 0.05 and 0.35")
        return value

    @field_validator("focus")
    @classmethod
    def valid_focus(cls, value: str) -> str:
        if value not in {"center", "top", "bottom", "left", "right", "top_left", "top_right", "bottom_left", "bottom_right"}:
            raise ValueError("unsupported focus point")
        return value

    @field_validator("transition")
    @classmethod
    def supported_transition(cls, value: str | None) -> str | None:
        allowed = {
            "none", "fade", "dissolve", "fade_black", "fade_white", "fade_slow", "fade_fast", "fade_grays",
            "wipe_left", "wipe_right", "wipe_up", "wipe_down", "wipe_top_left", "wipe_top_right",
            "wipe_bottom_left", "wipe_bottom_right", "slide_left", "slide_right", "slide_up", "slide_down",
            "smooth_left", "smooth_right", "smooth_up", "smooth_down", "circle_open", "circle_close",
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
    voice: Voice
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

    def api_dict(self) -> dict:
        result = {"jobId": self.job_id, "status": self.status, "progress": self.progress, "currentStep": self.current_step, "error": self.error, "logs": self.logs, "subtitleMode": self.subtitle_mode}
        if self.metadata is not None:
            result["metadata"] = self.metadata
        return result
