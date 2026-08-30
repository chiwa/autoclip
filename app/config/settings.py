from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    name: str = "autoclip"
    workspace: Path = Path("workspaces")
    max_upload_mb: int = Field(100, gt=0)
    max_extracted_mb: int = Field(500, gt=0)
    cleanup_on_startup: bool = False


class ServerSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = Field(8000, gt=0, le=65535)


class VideoSettings(BaseModel):
    width: int = Field(1080, gt=0)
    height: int = Field(1920, gt=0)
    fps: int = Field(30, gt=0)
    codec: str = "libx264"
    pixel_format: str = "yuv420p"
    scene_padding_seconds: float = Field(0.25, ge=0, le=10)
    transition: str = "fade"
    transition_seconds: float = Field(0.45, ge=0, le=2)


class TtsSettings(BaseModel):
    provider: str = "local"
    language: str = "th-TH"
    thonburian_ref_voice: Path = Path("/app/voices/thonburian-reference.wav")
    thonburian_ref_text: str = ""


class AudioSettings(BaseModel):
    narration_volume: float = Field(1.0, ge=0, le=4)
    background_volume: float = Field(0.12, ge=0, le=1)


class SubtitleSettings(BaseModel):
    enabled: bool = True
    font_size: int = Field(58, gt=0)
    margin_bottom: int = Field(180, ge=0)
    outline: int = Field(3, ge=0)
    font_file: Path = Path("/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf")


class Settings(BaseModel):
    app: AppSettings = AppSettings()
    server: ServerSettings = ServerSettings()
    video: VideoSettings = VideoSettings()
    tts: TtsSettings = TtsSettings()
    audio: AudioSettings = AudioSettings()
    subtitle: SubtitleSettings = SubtitleSettings()
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    image_model: str = "gpt-image-1"
    ai_instructions: str = "You are the AutoClip Mamase assistant. Create concise factual Thai short-form scripts. Return JSON with message and scenes when asked for a preview. Every scene needs id,narration,subtitle,image_prompt,motion,transition,estimated_duration. Always put the Mamase brand outro last."


def _set_nested(data: dict[str, Any], path: tuple[str, str], value: str) -> None:
    section, key = path
    data.setdefault(section, {})[key] = value


def load_settings(path: str | Path | None = None) -> Settings:
    config_path = Path(path or os.getenv("AUTOCLIP_CONFIG", "config.yaml"))
    data: dict[str, Any] = {}
    if config_path.exists():
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    overrides = {
        "AUTOCLIP_WORKSPACE": ("app", "workspace"),
        "AUTOCLIP_TTS_PROVIDER": ("tts", "provider"),
        "AUTOCLIP_MAX_UPLOAD_MB": ("app", "max_upload_mb"),
        "AUTOCLIP_MAX_EXTRACTED_MB": ("app", "max_extracted_mb"),
    }
    openai_key = os.getenv("OPENAI_API_KEY")
    # Native development does not get Docker Compose's automatic .env
    # interpolation. Accept a conventional dotenv line and, for backwards
    # compatibility with an older local setup, a compose-style
    # `OPENAI_API_KEY: ...` line. Never log or return the value.
    if not openai_key:
        for candidate in (Path(".env"), config_path.parent / ".env"):
            if not candidate.is_file():
                continue
            for line in candidate.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped.startswith("OPENAI_API_KEY") and ("=" in stripped or ":" in stripped):
                    _, value = stripped.replace(":", "=", 1).split("=", 1)
                    value = value.strip().strip('"\'')
                    if value:
                        openai_key = value
                        break
            if openai_key:
                break
    if openai_key:
        data["openai_api_key"] = openai_key
    if os.getenv("AUTOCLIP_OPENAI_MODEL"):
        data["openai_model"] = os.environ["AUTOCLIP_OPENAI_MODEL"]
    if os.getenv("AUTOCLIP_IMAGE_MODEL"):
        data["image_model"] = os.environ["AUTOCLIP_IMAGE_MODEL"]
    if os.getenv("AUTOCLIP_THONBURIAN_REF_VOICE"):
        data.setdefault("tts", {})["thonburian_ref_voice"] = os.environ["AUTOCLIP_THONBURIAN_REF_VOICE"]
    if os.getenv("AUTOCLIP_THONBURIAN_REF_TEXT"):
        data.setdefault("tts", {})["thonburian_ref_text"] = os.environ["AUTOCLIP_THONBURIAN_REF_TEXT"]
    for env_name, target in overrides.items():
        if env_name in os.environ:
            _set_nested(data, target, os.environ[env_name])
    settings = Settings.model_validate(data)
    # The checked-in config uses Docker paths (for example /app/voices/...)
    # while native development runs from the repository directory. Resolve a
    # missing Docker-style asset against the config directory so the same
    # package works in both runtimes without requiring another config file.
    ref_voice = settings.tts.thonburian_ref_voice
    if not ref_voice.is_file() and ref_voice.is_absolute() and str(ref_voice).startswith("/app/"):
        native_candidate = config_path.parent / str(ref_voice).removeprefix("/app/")
        if native_candidate.is_file():
            settings.tts.thonburian_ref_voice = native_candidate
    ws = settings.app.workspace
    if str(ws).startswith("/app/") and not ws.is_dir():
        settings.app.workspace = (config_path.parent / str(ws).removeprefix("/app/")).resolve()
    return settings
