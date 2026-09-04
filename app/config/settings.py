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
    kokoro_enabled: bool = False
    kokoro_model_dir: Path = Path("voices/wayu-kokoro-thai")
    kokoro_worker_python: Path = Path(".kokoro-venv/bin/python")
    kokoro_speed: float = Field(0.85, ge=0.7, le=1.1)


class AudioSettings(BaseModel):
    narration_volume: float = Field(1.0, ge=0, le=4)
    background_volume: float = Field(0.08, ge=0, le=1)


class WanSettings(BaseModel):
    """Settings reserved for the optional RunPod Wan 2.2 scene renderer.

    The connector is intentionally disabled until its secure transport is
    implemented.  Keeping this explicit prevents a UI selection from silently
    falling back to FFmpeg motion.
    """
    enabled: bool = False
    comfy_url: str | None = None
    request_timeout_seconds: int = Field(120, gt=0, le=3600)
    generation_timeout_seconds: int = Field(900, gt=0, le=7200)
    poll_interval_seconds: float = Field(2.0, ge=0.5, le=30)
    # 640x1152 preserves 9:16 while materially reducing Wan's pixel work.
    # AutoClip upscales the completed scene during final 1080x1920 composition.
    width: int = Field(640, gt=0)
    height: int = Field(1152, gt=0)
    # 22 is the production balance for the A40: materially faster than 25
    # while retaining stable documentary details. Individual scenes may use
    # wan.steps (for example 25 for the opening hook).
    steps: int = Field(22, ge=10, le=50)
    cfg: float = Field(5.0, ge=1.0, le=15.0)
    sampler_name: str = "uni_pc"


class RunpodF5Settings(BaseModel):
    enabled: bool = False
    ssh_host: str = ""
    ssh_port: int = Field(22, gt=0, le=65535)
    ssh_user: str = "root"
    ssh_key_path: Path = Path("~/.ssh/id_ed25519_runpod")
    python_path: Path = Path("/workspace/tools/F5-TTS-THAI/.venv/bin/python")
    checkpoint_path: Path = Path("/workspace/models/f5-tts-th-v2/model_350000.pt")
    vocab_path: Path = Path("/workspace/models/f5-tts-th-v2/vocab.txt")
    workdir: Path = Path("/workspace/autoclip/f5")
    runner_path: Path = Path("/workspace/autoclip/runpod_f5_infer.py")
    timeout_seconds: int = Field(900, gt=0, le=7200)


class SubtitleSettings(BaseModel):
    enabled: bool = True
    font_size: int = Field(58, gt=0)
    margin_bottom: int = Field(180, ge=0)
    outline: int = Field(3, ge=0)
    font_file: Path = Path("/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf")

class YouTubeOAuthSettings(BaseModel):
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://127.0.0.1:8000/api/youtube/callback"
    scope: str = "https://www.googleapis.com/auth/youtube.upload"

class YouTubeSettings(BaseModel):
    oauth: YouTubeOAuthSettings = YouTubeOAuthSettings()
    api_key: str = ""


class Settings(BaseModel):
    app: AppSettings = AppSettings()
    server: ServerSettings = ServerSettings()
    video: VideoSettings = VideoSettings()
    tts: TtsSettings = TtsSettings()
    audio: AudioSettings = AudioSettings()
    wan: WanSettings = WanSettings()
    runpod_f5: RunpodF5Settings = RunpodF5Settings()
    subtitle: SubtitleSettings = SubtitleSettings()
    youtube: YouTubeSettings = YouTubeSettings()
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    image_model: str = "gpt-image-1"
    ai_instructions: str = "You are the AutoClip Mamase assistant. Create concise factual Thai short-form scripts. Return JSON with message and scenes when asked for a preview. Every scene needs id,narration,subtitle,image_prompt,motion,transition,estimated_duration. Always put the Mamase brand outro last."


def _set_nested(data: dict[str, Any], path: tuple[str, str], value: str) -> None:
    section, key = path
    data.setdefault(section, {})[key] = value


def _dotenv_value(name: str, config_path: Path) -> str | None:
    """Read one conventional dotenv value for native development.

    Deliberately do not load every dotenv value into process environment: this
    keeps secrets out of child processes and lets explicit shell environment
    values take precedence.
    """
    if value := os.getenv(name):
        return value
    for candidate in (Path(".env"), config_path.parent / ".env"):
        if not candidate.is_file():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            if key.strip() == name:
                return value.strip().strip('"\'')
    return None


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
        "AUTOCLIP_WAN_ENABLED": ("wan", "enabled"),
        "AUTOCLIP_WAN_COMFY_URL": ("wan", "comfy_url"),
        "AUTOCLIP_WAN_REQUEST_TIMEOUT_SECONDS": ("wan", "request_timeout_seconds"),
        "AUTOCLIP_WAN_GENERATION_TIMEOUT_SECONDS": ("wan", "generation_timeout_seconds"),
        "AUTOCLIP_WAN_POLL_INTERVAL_SECONDS": ("wan", "poll_interval_seconds"),
        "AUTOCLIP_RUNPOD_F5_ENABLED": ("runpod_f5", "enabled"),
        "RUNPOD_SSH_HOST": ("runpod_f5", "ssh_host"),
        "RUNPOD_SSH_PORT": ("runpod_f5", "ssh_port"),
        "RUNPOD_SSH_USER": ("runpod_f5", "ssh_user"),
        "RUNPOD_SSH_KEY_PATH": ("runpod_f5", "ssh_key_path"),
        "AUTOCLIP_RUNPOD_F5_TIMEOUT_SECONDS": ("runpod_f5", "timeout_seconds"),
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
    # Also accept the existing compose-style YAML secrets file without ever
    # exposing its values. This keeps native and Compose configuration aligned.
    for candidate in (Path(".env"), config_path.parent / ".env"):
        if not candidate.is_file():
            continue
        try:
            secret_data = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
            yt = (secret_data.get("services", {}).get("youtube", {}) if isinstance(secret_data, dict) else {})
            oauth = yt.get("oauth", {}) if isinstance(yt, dict) else {}
            if oauth:
                data.setdefault("youtube", {}).setdefault("oauth", {}).update({"client_id": oauth.get("client-id", oauth.get("client_id", "")), "client_secret": oauth.get("client-secret", oauth.get("client_secret", ""))})
            if isinstance(yt, dict) and yt.get("api-key"):
                data.setdefault("youtube", {})["api_key"] = yt["api-key"]
        except Exception:
            # Some legacy local files use compose-style `key:value` without
            # a space and are not valid YAML. Parse only the two credential
            # keys needed by this integration; never log their values.
            import re
            raw = candidate.read_text(encoding="utf-8")
            oauth = data.setdefault("youtube", {}).setdefault("oauth", {})
            for key, field in (("client-id", "client_id"), ("client-secret", "client_secret")):
                match = re.search(rf"{key}\s*:\s*([^\s#]+)", raw)
                if match: oauth[field] = match.group(1).strip("'\"")
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
    yt = data.setdefault("youtube", {}).setdefault("oauth", {})
    for env_name, key in (("YOUTUBE_CLIENT_ID", "client_id"), ("YOUTUBE_CLIENT_SECRET", "client_secret"), ("YOUTUBE_REDIRECT_URI", "redirect_uri"), ("YOUTUBE_SCOPE", "scope")):
        if os.getenv(env_name): yt[key] = os.environ[env_name]
    if os.getenv("YOUTUBE_API_KEY"): data.setdefault("youtube", {})["api_key"] = os.environ["YOUTUBE_API_KEY"]
    for env_name, target in overrides.items():
        if value := _dotenv_value(env_name, config_path):
            _set_nested(data, target, value)
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
