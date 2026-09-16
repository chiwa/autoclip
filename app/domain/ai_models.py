from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from app.domain.events import local_now
from app.domain.models import SAFE_ID, validate_relative_asset


class AiProjectStatus(StrEnum):
    CHATTING = "CHATTING"
    SCRIPT_GENERATING = "SCRIPT_GENERATING"
    SCRIPT_READY = "SCRIPT_READY"
    IMAGES_GENERATING = "IMAGES_GENERATING"
    PREVIEW_GENERATING = "PREVIEW_GENERATING"
    PREVIEW_READY = "PREVIEW_READY"
    PREVIEW_NEEDS_REVIEW = "PREVIEW_NEEDS_REVIEW"
    PREVIEW_CONFIRMED = "PREVIEW_CONFIRMED"
    PACKAGING = "PACKAGING"
    PACKAGE_READY = "PACKAGE_READY"
    RENDERING = "RENDERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AiScene(BaseModel):
    id: str
    narration: str = Field(min_length=1, max_length=4000)
    tts_text: str | None = Field(default=None, max_length=4000)
    subtitle: str | None = Field(default=None, max_length=4000)
    show_subtitle: bool = True
    image_prompt: str = Field(min_length=1, max_length=2000)
    motion: str = "slow_zoom_in"
    transition: str | None = "fade"
    image_path: str | None = None
    estimated_duration: float = Field(ge=0.5, le=120, default=5.0)
    approved: bool = False
    role: str | None = None
    keywords: list[str] = Field(default_factory=list)
    sfx: str | None = None
    wan: dict | None = None

    @field_validator("id")
    @classmethod
    def valid_id(cls, value: str) -> str:
        if not SAFE_ID.fullmatch(value):
            raise ValueError("scene id is not filesystem-safe")
        return value

    @field_validator("image_path")
    @classmethod
    def valid_image_path(cls, value: str | None) -> str | None:
        return validate_relative_asset(value) if value else value


class AiChatMessage(BaseModel):
    role: str
    content: str = Field(min_length=1, max_length=8000)
    timestamp: datetime = Field(default_factory=local_now)


class AiProgressEntry(BaseModel):
    timestamp: datetime = Field(default_factory=local_now)
    level: str = "INFO"
    message: str = Field(min_length=1, max_length=2000)


class AiProject(BaseModel):
    project_id: str
    topic: str = ""
    channel_id: str = "undefined"
    status: AiProjectStatus = AiProjectStatus.CHATTING
    messages: list[AiChatMessage] = Field(default_factory=list)
    scenes: list[AiScene] = Field(default_factory=list)
    revision: int = 0
    confirmed_revision: int | None = None
    package_versions: list[str] = Field(default_factory=list)
    progress: int = Field(default=0, ge=0, le=100)
    current_step: str = "พร้อมเริ่มสร้าง ZIP"
    logs: list[AiProgressEntry] = Field(default_factory=list)
    error: dict | None = None
    package_path: str | None = None
    package_summary: dict | None = None
    hook_gate: dict | None = None
    created_at: datetime = Field(default_factory=local_now)
    updated_at: datetime = Field(default_factory=local_now)

    def invalidate_confirmation(self) -> None:
        self.confirmed_revision = None
        self.status = AiProjectStatus.PREVIEW_NEEDS_REVIEW
        self.revision += 1
        self.updated_at = local_now()
