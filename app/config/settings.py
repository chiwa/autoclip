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


class ReelHookGateSettings(BaseModel):
    enabled: bool = True
    max_hook_characters: int = Field(120, ge=40, le=240)


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
    ffmpeg_scene_parallelism: int = Field(2, ge=1, le=4)


class SilenceTrimSettings(BaseModel):
    enabled: bool = False
    threshold_db: float = Field(-45.0, ge=-100, le=0)
    minimum_silence_seconds: float = Field(0.10, ge=0.01, le=2.0)
    retained_edge_seconds: float = Field(0.06, ge=0.0, le=0.5)


class TtsSettings(BaseModel):
    provider: str = "google-gemini"
    language: str = "th-TH"
    thonburian_ref_voice: Path = Path("/app/voices/thonburian-reference.wav")
    thonburian_ref_text: str = ""
    kokoro_enabled: bool = False
    kokoro_model_dir: Path = Path("voices/wayu-kokoro-thai")
    kokoro_worker_python: Path = Path(".kokoro-venv/bin/python")
    kokoro_speed: float = Field(0.85, ge=0.7, le=1.1)
    google_project_id: str = ""
    google_model: str = "gemini-2.5-flash-tts"
    google_voice: str = "Fenrir"
    google_pitch: float = Field(0.0, ge=-20, le=20)
    google_speaking_rate: float = Field(1.05, ge=0.5, le=2.0)
    google_parallelism: int = Field(6, ge=1, le=12)
    silence_trim: SilenceTrimSettings = SilenceTrimSettings()
    google_style_prompt: str = (
        "Read aloud in a natural, playful, conversational Thai voice. "
        "Sound confident, friendly, and slightly cheeky, like a charismatic Thai creator casually sharing a fascinating discovery with a close friend.\n\n"
        "Keep the delivery flowing and connected, with a medium-fast pace and clear pronunciation. "
        "Maintain forward momentum throughout each sentence. Use brief pauses only when they help comprehension or set up a genuinely surprising moment.\n\n"
        "Vary pitch and rhythm naturally, with a subtle smile in the voice. "
        "Give surprising facts a spontaneous, amused reaction, as if thinking: \"เฮ้ย... จริงดิ?\" "
        "Emphasize important words briefly through tone, not by stretching syllables or slowing down.\n\n"
        "Avoid slow openings, drawn-out words, long dramatic pauses, sleepy pacing, excessive emphasis, and perfectly even sentence timing. "
        "Never sound like a news presenter, announcer, formal narrator, advertisement, or someone reading from a script.\n\n"
        "Overall personality: friendly, curious, clever, playful, charming, energetic, and easy to listen to—lively without shouting, expressive without becoming theatrical."
    )


class ReelTtsSettings(BaseModel):
    voice: str | None = "Fenrir"
    hook_speed: float | None = Field(1.10, ge=0.5, le=2.0)
    normal_speed: float | None = Field(1.05, ge=0.5, le=2.0)
    hook_style: str | None = None
    normal_style: str | None = None


class ReelOutroSettings(BaseModel):
    enabled: bool = True
    image: Path = Path("assets/branding/mamase/reels-end-scene.png")
    duration: float = Field(2.0, ge=1.5, le=2.5)
    bgm_fade_out: bool = True


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


class LtxSettings(BaseModel):
    """Settings reserved for the RunPod LTX-Video 2B Distilled scene renderer."""
    enabled: bool = False
    ssh_host: str = ""
    ssh_port: int = Field(22, gt=0, le=65535)
    ssh_user: str = "root"
    ssh_key_path: Path = Path("~/.ssh/id_ed25519_runpod")
    poc_root: Path = Path("/workspace/ltx-video-poc")
    runner_path: Path = Path("/workspace/ltx-video-poc/run_i2v.sh")
    timeout_seconds: int = Field(900, gt=0, le=7200)
    # 448x768 (9:16) base resolution for LTX-Video 2B Distilled
    width: int = Field(448, gt=0)
    height: int = Field(768, gt=0)
    fps: int = Field(15, gt=0)
    steps: int = Field(8, ge=1, le=50)
    seed: int = 171198

    @property
    def runpod_host(self) -> str:
        return self.ssh_host

    @property
    def runpod_port(self) -> int:
        return self.ssh_port

    @property
    def runpod_user(self) -> str:
        return self.ssh_user

    @property
    def runpod_key_path(self) -> Path:
        return self.ssh_key_path


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


class MuseTalkSettings(BaseModel):
    """Settings reserved for the RunPod MuseTalk real-time audio-driven lip sync."""
    enabled: bool = True
    ssh_host: str = ""
    ssh_port: int = Field(22, gt=0, le=65535)
    ssh_user: str = "root"
    ssh_key_path: Path = Path("~/.ssh/id_ed25519_runpod")
    musetalk_root: Path = Path("/workspace/musetalk")
    runner_path: Path = Path("/workspace/musetalk/run_lip_sync.sh")
    timeout_seconds: int = Field(600, gt=0, le=3600)
    bbox_shift: int = 0
    use_float16: bool = True
    version: str = "v1.5"

    @property
    def runpod_host(self) -> str:
        return self.ssh_host

    @property
    def runpod_port(self) -> int:
        return self.ssh_port

    @property
    def runpod_user(self) -> str:
        return self.ssh_user

    @property
    def runpod_key_path(self) -> Path:
        return self.ssh_key_path


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


class PodcastEndingSceneSettings(BaseModel):
    enabled: bool = True
    image: Path = Path("assets/images/end-of-scence.png")
    song: Path = Path("assets/audio/end-scence-song.mp3")
    disable_subtitles: bool = True
    motion: str = "none"
    apply_to_thai_video: bool = True
    apply_to_english_audio: bool = True
    fade_in_seconds: float = Field(0.75, ge=0.0, le=2.0)
    fade_out_seconds: float = Field(1.0, ge=0.0, le=5.0)


class PodcastSettings(BaseModel):
    chunk_max_bytes: int = Field(1400, gt=100, le=5000)
    concurrency: int = Field(3, ge=1, le=10)
    max_retries: int = Field(5, ge=0, le=10)
    default_voice: str = "Iapetus"
    default_speed: float = Field(0.90, ge=0.5, le=2.0)
    default_bgm_track: str = "mamase-podcast-bg.mp3"
    default_bgm_volume: float = Field(0.08, ge=0.0, le=1.0)
    ending_scene: PodcastEndingSceneSettings = PodcastEndingSceneSettings()
    default_style_prompt: str = (
        "Speak smoothly with connected phrasing and a natural conversational rhythm. "
        "Avoid short choppy pauses between phrases. Keep sentence transitions fluid, "
        "with gentle pacing and subtle emphasis. Use brief natural pauses only at "
        "punctuation or topic changes."
    )
    default_english_style_prompt: str = default_style_prompt
    default_female_style_prompt: str = (
        "Read aloud in a calm, warm, and gently formal Thai voice (female speaker with a gentle, feminine, and soothing tone) suitable for a relaxing bedtime podcast. "
        "Speak smoothly and naturally, like a thoughtful female storyteller guiding the listener through a fascinating subject late at night. "
        "Maintain a soft, even volume and a relaxed, unhurried pace. "
        "Use subtle changes in pitch to keep the narration engaging without becoming energetic or dramatic. "
        "Keep pauses natural, brief, and well placed between ideas. "
        "Avoid sudden emphasis, sharp changes in volume, exaggerated emotion, playful teasing, advertising language, and news-anchor delivery. "
        "Pronounce scientific terms, names, and numbers clearly. "
        "The overall experience should feel peaceful, reassuring, intelligent, and comfortable enough for the listener to gradually fall asleep."
    )

    def resolve_style_prompt(self, voice: str | None = None, custom_style: str | None = None) -> str:
        """Resolves the appropriate style prompt, honoring custom prompts or selecting gendered bedtime defaults."""
        if custom_style and custom_style.strip():
            return custom_style.strip()
        females = {"achernar", "aoede", "autonoe", "callirrhoe", "despina", "erinome", "gacrux", "kore", "leda", "zephyr"}
        target_voice = (voice or self.default_voice).strip().lower()
        if target_voice in females:
            return self.default_female_style_prompt
        return self.default_style_prompt


class Settings(BaseModel):
    app: AppSettings = AppSettings()
    server: ServerSettings = ServerSettings()
    video: VideoSettings = VideoSettings()
    tts: TtsSettings = TtsSettings()
    reel_tts: ReelTtsSettings = ReelTtsSettings()
    reel_outro: ReelOutroSettings = ReelOutroSettings()
    audio: AudioSettings = AudioSettings()
    wan: WanSettings = WanSettings()
    ltx: LtxSettings = LtxSettings()
    musetalk: MuseTalkSettings = MuseTalkSettings()
    runpod_f5: RunpodF5Settings = RunpodF5Settings()
    subtitle: SubtitleSettings = SubtitleSettings()
    youtube: YouTubeSettings = YouTubeSettings()
    podcast: PodcastSettings = PodcastSettings()
    reel_hook_gate: ReelHookGateSettings = ReelHookGateSettings()
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    image_model: str = "gpt-image-1"
    # Read only by the server. Never return it from an API or put it in a ZIP.
    gemini_api_key: str | None = None
    gemini_text_model: str = "gemini-3.6-flash"
    gemini_image_model: str = "gemini-2.5-flash-image"
    # Server-side only. Never expose this value to the browser or packages.
    deepseek_api_key: str | None = None
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_base_url: str = "https://api.deepseek.com"
    # `/ai` uses the locally authenticated Antigravity CLI by default. This
    # keeps its session credentials outside AutoClip's configuration.
    ai_provider: str = "antigravity"
    ai_image_provider: str = "gemini"
    antigravity_cli_path: Path = Path("/opt/homebrew/bin/agy")
    antigravity_model: str = "gemini-3.8-flash-medium"
    antigravity_timeout_seconds: int = Field(900, gt=30, le=3600)
    ai_instructions: str = "You are the AutoClip Mamase assistant. Create concise factual Thai short-form scripts. Return JSON with message and narrated content scenes when asked for a preview. Every scene needs id,narration,subtitle,image_prompt,motion,transition,estimated_duration. Do not create a brand-outro scene; AutoClip appends the silent Mamase post-roll after narration ends."


def _set_nested(data: dict[str, Any], path: tuple[str, str] | tuple[str, str, str], value: str) -> None:
    if len(path) == 2:
        section, key = path
        data.setdefault(section, {})[key] = value
    elif len(path) == 3:
        sec1, sec2, key = path
        data.setdefault(sec1, {}).setdefault(sec2, {})[key] = value


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
            if not stripped or stripped.startswith("#") or ("=" not in stripped and ":" not in stripped):
                continue
            key, value = stripped.split("=", 1) if "=" in stripped else stripped.split(":", 1)
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
        "AUTOCLIP_GOOGLE_CLOUD_PROJECT": ("tts", "google_project_id"),
        "AUTOCLIP_GOOGLE_TTS_MODEL": ("tts", "google_model"),
        "AUTOCLIP_GOOGLE_TTS_VOICE": ("tts", "google_voice"),
        "AUTOCLIP_GOOGLE_TTS_PARALLELISM": ("tts", "google_parallelism"),
        "AUTOCLIP_TTS_SILENCE_TRIM_ENABLED": ("tts", "silence_trim", "enabled"),
        "AUTOCLIP_TTS_SILENCE_THRESHOLD_DB": ("tts", "silence_trim", "threshold_db"),
        "AUTOCLIP_TTS_MINIMUM_SILENCE_SECONDS": ("tts", "silence_trim", "minimum_silence_seconds"),
        "AUTOCLIP_TTS_RETAINED_EDGE_SECONDS": ("tts", "silence_trim", "retained_edge_seconds"),
        "AUTOCLIP_FFMPEG_SCENE_PARALLELISM": ("video", "ffmpeg_scene_parallelism"),
        "AUTOCLIP_MAX_UPLOAD_MB": ("app", "max_upload_mb"),
        "AUTOCLIP_MAX_EXTRACTED_MB": ("app", "max_extracted_mb"),
        "AUTOCLIP_REEL_HOOK_GATE_ENABLED": ("reel_hook_gate", "enabled"),
        "AUTOCLIP_REEL_HOOK_MAX_CHARACTERS": ("reel_hook_gate", "max_hook_characters"),
        "AUTOCLIP_LTX_ENABLED": ("ltx", "enabled"),
        "AUTOCLIP_LTX_SSH_HOST": ("ltx", "ssh_host"),
        "AUTOCLIP_LTX_RUNPOD_HOST": ("ltx", "ssh_host"),
        "AUTOCLIP_LTX_SSH_PORT": ("ltx", "ssh_port"),
        "AUTOCLIP_LTX_RUNPOD_PORT": ("ltx", "ssh_port"),
        "AUTOCLIP_LTX_SSH_USER": ("ltx", "ssh_user"),
        "AUTOCLIP_LTX_RUNPOD_USER": ("ltx", "ssh_user"),
        "AUTOCLIP_LTX_SSH_KEY_PATH": ("ltx", "ssh_key_path"),
        "AUTOCLIP_LTX_RUNPOD_KEY_PATH": ("ltx", "ssh_key_path"),
        "AUTOCLIP_LTX_STEPS": ("ltx", "steps"),
        "AUTOCLIP_LTX_SEED": ("ltx", "seed"),
        "AUTOCLIP_LTX_FPS": ("ltx", "fps"),
        "AUTOCLIP_LTX_WIDTH": ("ltx", "width"),
        "AUTOCLIP_LTX_HEIGHT": ("ltx", "height"),
        "AUTOCLIP_LTX_TIMEOUT_SECONDS": ("ltx", "timeout_seconds"),
        "AUTOCLIP_MUSETALK_ENABLED": ("musetalk", "enabled"),
        "AUTOCLIP_MUSETALK_SSH_HOST": ("musetalk", "ssh_host"),
        "AUTOCLIP_MUSETALK_RUNPOD_HOST": ("musetalk", "ssh_host"),
        "AUTOCLIP_MUSETALK_SSH_PORT": ("musetalk", "ssh_port"),
        "AUTOCLIP_MUSETALK_RUNPOD_PORT": ("musetalk", "ssh_port"),
        "AUTOCLIP_MUSETALK_SSH_USER": ("musetalk", "ssh_user"),
        "AUTOCLIP_MUSETALK_RUNPOD_USER": ("musetalk", "ssh_user"),
        "AUTOCLIP_MUSETALK_SSH_KEY_PATH": ("musetalk", "ssh_key_path"),
        "AUTOCLIP_MUSETALK_RUNPOD_KEY_PATH": ("musetalk", "ssh_key_path"),
        "AUTOCLIP_MUSETALK_BBOX_SHIFT": ("musetalk", "bbox_shift"),
        "AUTOCLIP_MUSETALK_VERSION": ("musetalk", "version"),
        "AUTOCLIP_MUSETALK_TIMEOUT_SECONDS": ("musetalk", "timeout_seconds"),
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
        "PODCAST_TTS_CHUNK_MAX_BYTES": ("podcast", "chunk_max_bytes"),
        "PODCAST_TTS_CONCURRENCY": ("podcast", "concurrency"),
        "PODCAST_TTS_MAX_RETRIES": ("podcast", "max_retries"),
        "PODCAST_DEFAULT_VOICE": ("podcast", "default_voice"),
        "PODCAST_DEFAULT_SPEED": ("podcast", "default_speed"),
        "PODCAST_DEFAULT_BGM_TRACK": ("podcast", "default_bgm_track"),
        "PODCAST_DEFAULT_BGM_VOLUME": ("podcast", "default_bgm_volume"),
        "PODCAST_DEFAULT_STYLE_PROMPT": ("podcast", "default_style_prompt"),
        "PODCAST_DEFAULT_ENGLISH_STYLE_PROMPT": ("podcast", "default_english_style_prompt"),
        "PODCAST_ENDING_SCENE_ENABLED": ("podcast", "ending_scene", "enabled"),
        "PODCAST_ENDING_SCENE_IMAGE": ("podcast", "ending_scene", "image"),
        "PODCAST_ENDING_SCENE_SONG": ("podcast", "ending_scene", "song"),
        "PODCAST_ENDING_SCENE_APPLY_TO_THAI_VIDEO": ("podcast", "ending_scene", "apply_to_thai_video"),
        "PODCAST_ENDING_SCENE_APPLY_TO_ENGLISH_AUDIO": ("podcast", "ending_scene", "apply_to_english_audio"),
        "AUTOCLIP_PODCAST_ENDING_SCENE_ENABLED": ("podcast", "ending_scene", "enabled"),
        "AUTOCLIP_PODCAST_ENDING_SCENE_IMAGE": ("podcast", "ending_scene", "image"),
        "AUTOCLIP_PODCAST_ENDING_SCENE_SONG": ("podcast", "ending_scene", "song"),
        "AUTOCLIP_PODCAST_CHUNK_MAX_BYTES": ("podcast", "chunk_max_bytes"),
        "AUTOCLIP_PODCAST_CONCURRENCY": ("podcast", "concurrency"),
        "AUTOCLIP_PODCAST_MAX_RETRIES": ("podcast", "max_retries"),
        "AUTOCLIP_PODCAST_DEFAULT_VOICE": ("podcast", "default_voice"),
        "AUTOCLIP_PODCAST_DEFAULT_SPEED": ("podcast", "default_speed"),
        "AUTOCLIP_PODCAST_DEFAULT_BGM_TRACK": ("podcast", "default_bgm_track"),
        "AUTOCLIP_PODCAST_DEFAULT_BGM_VOLUME": ("podcast", "default_bgm_volume"),
        "AUTOCLIP_PODCAST_DEFAULT_STYLE_PROMPT": ("podcast", "default_style_prompt"),
        "AUTOCLIP_PODCAST_DEFAULT_ENGLISH_STYLE_PROMPT": ("podcast", "default_english_style_prompt"),
        "AUTOCLIP_AI_PROVIDER": ("ai_provider",),
        "AUTOCLIP_AI_IMAGE_PROVIDER": ("ai_image_provider",),
        "AUTOCLIP_ANTIGRAVITY_CLI_PATH": ("antigravity_cli_path",),
        "AUTOCLIP_ANTIGRAVITY_MODEL": ("antigravity_model",),
        "AUTOCLIP_ANTIGRAVITY_TIMEOUT_SECONDS": ("antigravity_timeout_seconds",),
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
    gemini_key = _dotenv_value("GEMINI_API_KEY", config_path)
    if gemini_key:
        data["gemini_api_key"] = gemini_key
    if value := _dotenv_value("DEEPSEEK_API_KEY", config_path):
        data["deepseek_api_key"] = value
    if value := _dotenv_value("AUTOCLIP_DEEPSEEK_MODEL", config_path):
        data["deepseek_model"] = value
    if value := _dotenv_value("AUTOCLIP_DEEPSEEK_BASE_URL", config_path):
        data["deepseek_base_url"] = value.rstrip("/")
    if os.getenv("AUTOCLIP_OPENAI_MODEL"):
        data["openai_model"] = os.environ["AUTOCLIP_OPENAI_MODEL"]
    if os.getenv("AUTOCLIP_IMAGE_MODEL"):
        data["image_model"] = os.environ["AUTOCLIP_IMAGE_MODEL"]
    if value := _dotenv_value("AUTOCLIP_GEMINI_TEXT_MODEL", config_path):
        data["gemini_text_model"] = value
    if value := _dotenv_value("AUTOCLIP_GEMINI_IMAGE_MODEL", config_path):
        data["gemini_image_model"] = value
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
            if len(target) == 1:
                data[target[0]] = value
            elif len(target) == 2:
                _set_nested(data, target, value)
            else:
                section, parent, key = target
                data.setdefault(section, {}).setdefault(parent, {})[key] = value
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
    if str(ws).startswith("/app/"):
        settings.app.workspace = (config_path.parent / str(ws).removeprefix("/app/")).resolve()
    return settings
