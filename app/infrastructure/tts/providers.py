from __future__ import annotations

import math
import struct
import threading
import json
import wave
from pathlib import Path
from typing import Protocol

from app.config.settings import Settings
from app.domain.errors import AppError


class TtsProvider(Protocol):
    def synthesize(self, text: str, language: str, voice: str, speed: float, output_path: Path) -> Path: ...


class DummyTtsProvider:
    """Deterministic test tone; it is deliberately not represented as real speech."""
    def synthesize(self, text: str, language: str, voice: str, speed: float, output_path: Path) -> Path:
        duration = max(1.0, min(15.0, len(text) * 0.075 / speed))
        sample_rate = 48000
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output_path), "wb") as wav:
            wav.setparams((1, 2, sample_rate, 0, "NONE", "not compressed"))
            frames = bytearray()
            for index in range(int(duration * sample_rate)):
                envelope = min(1.0, index / (sample_rate * 0.03), (duration * sample_rate - index) / (sample_rate * 0.03))
                sample = int(1600 * envelope * math.sin(2 * math.pi * 220 * index / sample_rate))
                frames.extend(struct.pack("<h", sample))
            wav.writeframes(frames)
        return output_path


class LocalThaiTtsProvider:
    VOICES = {
        "thai-female-01": "th_f_1",
        "thai-male-01": "th_m_1",
        "thai-female-02": "th_f_2",
        "thai-male-02": "th_m_2",
        "th_f_1": "th_f_1",
        "th_m_1": "th_m_1",
        "th_f_2": "th_f_2",
        "th_m_2": "th_m_2",
    }
    _inference_lock = threading.Lock()

    def synthesize(self, text: str, language: str, voice: str, speed: float, output_path: Path) -> Path:
        if language.lower() not in {"th", "th-th"}:
            raise AppError("TTS_GENERATION_FAILED", "Local TTS currently supports Thai language only", {"language": language})
        resolved_voice = self.VOICES.get(voice)
        if not resolved_voice:
            raise AppError("TTS_GENERATION_FAILED", "Requested local Thai voice is unavailable", {"voice": voice, "supportedVoices": sorted(self.VOICES)})
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            from vachanatts import TTS

            with self._inference_lock:
                TTS(text=text, voice=resolved_voice, output=str(output_path), speed=speed)
        except AppError:
            raise
        except Exception as exc:
            raise AppError("TTS_GENERATION_FAILED", "Local Thai narration generation failed", {"voice": voice}) from exc
        if not output_path.is_file() or output_path.stat().st_size <= 44:
            raise AppError("TTS_GENERATION_FAILED", "Local Thai narration generation produced no audio", {"voice": voice})
        return output_path


class ThonburianTtsProvider:
    """F5/Flow-Matching Thai provider; requires a licensed reference WAV and transcript."""

    _inference_lock = threading.Lock()

    def __init__(self, settings: Settings):
        self.settings = settings
        self._pipeline = None
        self._device = None

    def synthesize(self, text: str, language: str, voice: str, speed: float, output_path: Path) -> Path:
        if language.lower() not in {"th", "th-th"}:
            raise AppError("TTS_GENERATION_FAILED", "Thonburian TTS currently supports Thai language only")
        ref_voice = self.settings.tts.thonburian_ref_voice
        ref_text = self.settings.tts.thonburian_ref_text.strip()
        if not ref_voice.is_file() or not ref_text:
            raise AppError("TTS_GENERATION_FAILED", "Thonburian ต้องตั้งค่า reference voice WAV และ ref text ก่อน")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            import torch
            from flowtts.inference import AudioConfig, FlowTTSPipeline, ModelConfig
            if torch.cuda.is_available():
                device = "cuda"
            elif getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
                # Apple Silicon GPU (Metal Performance Shaders) for native macOS runs.
                device = "mps"
            else:
                device = "cpu"
            with self._inference_lock:
                if self._pipeline is None:
                    model_config = ModelConfig(
                        language="th", model_type="F5",
                        checkpoint="hf://biodatlab/ThonburianTTS/megaF5/mega_f5_last.safetensors",
                        vocab_file="hf://biodatlab/ThonburianTTS/megaF5/mega_vocab.txt",
                        vocoder="vocos", device=device,
                    )
                    self._pipeline = FlowTTSPipeline(
                        model_config=model_config,
                        audio_config=AudioConfig(silence_threshold=-45, cfg_strength=2.5, speed=speed),
                    )
                    self._device = device
                self._pipeline(
                    text=text,
                    ref_voice=str(ref_voice),
                    ref_text=ref_text,
                    output_file=str(output_path),
                    speed=speed,
                )
        except AppError:
            raise
        except Exception as exc:
            raise AppError("TTS_GENERATION_FAILED", "Thonburian Thai narration generation failed") from exc
        if not output_path.is_file() or output_path.stat().st_size <= 44:
            raise AppError("TTS_GENERATION_FAILED", "Thonburian produced no audio")
        return output_path


class BirdF5ThaiTtsProvider:
    """Bird/F5-TTS-THAI zero-shot Thai voice provider.

    The model uses the same reference-WAV + reference-transcript contract as
    Thonburian, but is loaded through the community ``f5-tts-th`` package.
    Loading is lazy so existing providers remain usable without this optional
    dependency.
    """
    _inference_lock = threading.Lock()

    def __init__(self, settings: Settings):
        self.settings = settings
        self._tts = None

    def synthesize(self, text: str, language: str, voice: str, speed: float, output_path: Path) -> Path:
        if language.lower() not in {"th", "th-th"}:
            raise AppError("TTS_GENERATION_FAILED", "Bird F5 Thai TTS currently supports Thai language only")
        ref_voice = self.settings.tts.thonburian_ref_voice
        ref_text = self.settings.tts.thonburian_ref_text.strip()
        if not ref_voice.is_file() or not ref_text:
            raise AppError("TTS_GENERATION_FAILED", "Bird F5-TTS-THAI ต้องตั้งค่า reference voice WAV และ ref text ก่อน")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            import soundfile as sf
            from f5_tts_th.tts import TTS
            with self._inference_lock:
                if self._tts is None:
                    self._tts = TTS(model="v1")
                # Keep normal scenes in one inference batch. The upstream
                # default (100 chars) splits Thai sentences and cross-fades
                # independently generated chunks, which can sound like
                # clicks/stutters. A larger bound preserves sentence
                # continuity; long text is still safely chunked upstream.
                wav = self._tts.infer(
                    ref_audio=str(ref_voice),
                    ref_text=ref_text,
                    gen_text=text,
                    step=48,
                    cfg=1.8,
                    speed=speed,
                    max_chars=240,
                )
                sf.write(str(output_path), wav, 24000)
        except AppError:
            raise
        except Exception as exc:
            raise AppError("TTS_GENERATION_FAILED", "Bird F5-TTS-THAI narration generation failed") from exc
        if not output_path.is_file() or output_path.stat().st_size <= 44:
            raise AppError("TTS_GENERATION_FAILED", "Bird F5-TTS-THAI produced no audio")
        return output_path


class KhanomTanTtsProvider:
    """Optional KhanomTan YourTTS provider (lazy Coqui-TTS integration)."""

    _inference_lock = threading.Lock()
    MODEL = "wannaphong/khanomtan-tts-v1.1"

    def __init__(self, settings: Settings):
        self.settings = settings
        self._tts = None

    def _load_model(self, TTS):
        """Load the Hugging Face checkpoint explicitly (Coqui's registry
        parser only accepts its four-part legacy names)."""
        from huggingface_hub import snapshot_download
        model_dir = Path(snapshot_download(self.MODEL))
        config = json.loads((model_dir / "config.json").read_text(encoding="utf-8"))
        args = config.setdefault("model_args", {})
        for key in ("speakers_file", "language_ids_file", "speaker_encoder_config_path", "speaker_encoder_model_path"):
            value = args.get(key)
            if value:
                args[key] = str(model_dir / value)
            value = config.get(key)
            if value:
                config[key] = str(model_dir / value)
        config_path = model_dir / "autoclip-config.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        return TTS(model_path=str(model_dir / "best_model.pth"), config_path=str(config_path), progress_bar=False, gpu=False)

    def synthesize(self, text: str, language: str, voice: str, speed: float, output_path: Path) -> Path:
        if language.lower() not in {"th", "th-th"}:
            raise AppError("TTS_GENERATION_FAILED", "KhanomTan currently supports Thai language only")
        try:
            from TTS.api import TTS
            with self._inference_lock:
                if self._tts is None:
                    self._tts = self._load_model(TTS)
                kwargs = {"text": text, "file_path": str(output_path), "language": "th-th"}
                # AutoClip scripts historically use provider-neutral names such
                # as ``thai-male-01``.  KhanomTan's YourTTS checkpoint only
                # contains its named speakers; map unknown names to the
                # deterministic Thai-capable default instead of letting Coqui
                # interpret them as a missing voice-cloning file.
                available = getattr(self._tts, "speakers", None) or []
                if voice in available:
                    speaker = voice
                elif "female" in (voice or "").lower():
                    speaker = "Linda" if "Linda" in available else (available[0] if available else None)
                else:
                    speaker = "Bernard" if "Bernard" in available else (available[0] if available else None)
                kwargs["speaker"] = speaker
                self._tts.tts_to_file(**kwargs)
                # KhanomTan's VITS checkpoint ignores Coqui's ``speed``
                # argument. Keep the model's native timing; callers can use
                # the explicit speed control of providers that support it.
        except ImportError as exc:
            raise AppError("TTS_GENERATION_FAILED", "KhanomTan ยังไม่ได้ติดตั้ง Coqui-TTS (ติดตั้ง requirements-khanomtan.txt)") from exc
        except Exception as exc:
            raise AppError("TTS_GENERATION_FAILED", "KhanomTan Thai narration generation failed") from exc
        if not output_path.is_file() or output_path.stat().st_size <= 44:
            raise AppError("TTS_GENERATION_FAILED", "KhanomTan produced no audio")
        return output_path


def create_tts_provider(name: str, settings: Settings | None = None) -> TtsProvider:
    if name == "dummy":
        return DummyTtsProvider()
    if name == "local":
        return LocalThaiTtsProvider()
    if name == "thonburian":
        if settings is None:
            raise AppError("TTS_GENERATION_FAILED", "Thonburian provider requires application settings")
        return ThonburianTtsProvider(settings)
    if name in {"bird", "bird-f5", "f5-thai", "f5-tts-thai"}:
        if settings is None:
            raise AppError("TTS_GENERATION_FAILED", "Bird F5-TTS-THAI provider requires application settings")
        return BirdF5ThaiTtsProvider(settings)
    if name in {"khanomtan", "khanom-tan", "khanomtan-tts"}:
        if settings is None:
            raise AppError("TTS_GENERATION_FAILED", "KhanomTan provider requires application settings")
        return KhanomTanTtsProvider(settings)
    raise AppError("TTS_GENERATION_FAILED", "Configured TTS provider is unavailable", {"provider": name})
