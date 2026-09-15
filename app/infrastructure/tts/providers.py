from __future__ import annotations

import math
import struct
import threading
import json
import subprocess
import wave
import base64
import hashlib
import uuid
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
        "default": "th_m_1",
        "thai-female-01": "th_f_1",
        "thai-male-01": "th_m_1",
        "thai-female-02": "th_f_2",
        "thai-male-02": "th_m_2",
        "th_f_1": "th_f_1",
        "th_m_1": "th_m_1",
        "th_f_2": "th_f_2",
        "th_m_2": "th_m_2",
        # Legacy UI labels belong to Kokoro, but accept them defensively when
        # an older package/page submits them with the Local Vachana provider.
        "m_young_clear": "th_m_1",
        "m_mid_warm": "th_m_1",
        "m_elderly_deep": "th_m_1",
        "m_teen_bright": "th_m_1",
        "f_young_clear": "th_f_1",
        "f_young_warm": "th_f_1",
        "f_young_bright": "th_f_2",
        "f_mid_clear": "th_f_1",
        "f_mid_warm": "th_f_2",
        "f_elderly_soft": "th_f_1",
        "f_elderly_low": "th_f_2",
        "f_teen_bright": "th_f_2",
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


class GoogleGeminiTtsProvider:
    """Google Gemini TTS using local Application Default Credentials (ADC)."""

    _concurrency_limiter = threading.Semaphore(3)

    def __init__(self, settings: Settings):
        self.settings = settings
        self.style_prompt: str | None = None

    def synthesize(self, text: str, language: str, voice: str, speed: float, output_path: Path) -> Path:
        import time
        max_retries = 3

        with self._concurrency_limiter:
            for attempt in range(max_retries):
                try:
                    import google.auth
                    from google.auth.transport.requests import AuthorizedSession
                    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
                    # Native ADC stores the quota project selected through
                    # `gcloud auth application-default set-quota-project`; honor it so
                    # no credential path or duplicate secret configuration is needed.
                    project_id = self.settings.tts.google_project_id.strip() or getattr(credentials, "quota_project_id", "") or ""
                    if not project_id:
                        raise AppError("GOOGLE_TTS_NOT_CONFIGURED", "Google Gemini TTS ต้องตั้ง Google quota project ก่อน")
                    payload = {
                        "input": {
                            "prompt": self.style_prompt or self.settings.tts.google_style_prompt,
                            "text": text,
                        },
                        "voice": {
                            "languageCode": language,
                            "name": voice or self.settings.tts.google_voice,
                            "modelName": self.settings.tts.google_model,
                        },
                        "audioConfig": {"audioEncoding": "LINEAR16", "pitch": self.settings.tts.google_pitch, "speakingRate": speed},
                    }
                    response = AuthorizedSession(credentials).post(
                        "https://texttospeech.googleapis.com/v1beta1/text:synthesize",
                        headers={"x-goog-user-project": project_id}, json=payload, timeout=90,
                    )
                    if not response.ok:
                        try:
                            error = response.json().get("error", {})
                            reason = str(error.get("message") or "")[:300]
                        except Exception:
                            reason = ""
                        details = {"status": response.status_code}
                        if reason:
                            details["reason"] = reason
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            try:
                                details["retryAfterSeconds"] = max(0.0, float(retry_after))
                            except ValueError:
                                pass
                        details["retryable"] = response.status_code == 429 or response.status_code >= 500

                        if response.status_code == 429 and attempt < max_retries - 1:
                            sleep_time = details.get("retryAfterSeconds", 10.0 * (attempt + 1))
                            time.sleep(sleep_time)
                            continue

                        raise AppError("TTS_GENERATION_FAILED", "Google Gemini TTS สร้างเสียงไม่สำเร็จ", details)
                    audio = base64.b64decode(response.json().get("audioContent", ""))
                    break
                except AppError:
                    raise
                except Exception as exc:
                    if attempt < max_retries - 1:
                        time.sleep(5.0 * (attempt + 1))
                        continue
                    raise AppError("GOOGLE_TTS_NOT_CONFIGURED", "ไม่พบ Google Application Default Credentials หรือ Google TTS ใช้งานไม่ได้") from exc

        if len(audio) <= 44:
            raise AppError("TTS_GENERATION_FAILED", "Google Gemini TTS ไม่ได้ส่งไฟล์เสียงกลับมา")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio)
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


class RunpodF5ThaiTtsProvider:
    """F5-TTS-THAI V2 executed on the configured RunPod GPU through SSH/SCP."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._prepared_reference: str | None = None

    def synthesize(self, text: str, language: str, voice: str, speed: float, output_path: Path) -> Path:
        if language.lower() not in {"th", "th-th"}:
            raise AppError("TTS_GENERATION_FAILED", "RunPod F5-TTS-THAI V2 currently supports Thai language only")
        remote = self.settings.runpod_f5
        reference = self.settings.tts.thonburian_ref_voice
        reference_text = self.settings.tts.thonburian_ref_text.strip()
        if not remote.enabled or not remote.ssh_host or not remote.ssh_key_path.expanduser().is_file():
            raise AppError("RUNPOD_F5_NOT_CONFIGURED", "RunPod F5-TTS-THAI V2 ยังไม่ได้ตั้งค่า SSH connector")
        if not reference.is_file() or not reference_text:
            raise AppError("TTS_GENERATION_FAILED", "RunPod F5-TTS-THAI V2 ต้องตั้งค่า reference voice WAV และ ref text ก่อน")
        try:
            remote_reference = self._prepare(reference)
            remote_output = f"{remote.workdir}/outputs/{uuid.uuid4().hex}.wav"
            payload = base64.urlsafe_b64encode(json.dumps({
                "text": text,
                "reference": remote_reference,
                "reference_text": reference_text,
                "output": remote_output,
                "checkpoint": str(remote.checkpoint_path),
                "vocab": str(remote.vocab_path),
                "speed": speed,
            }, ensure_ascii=False).encode("utf-8")).decode("ascii")
            self._ssh([str(remote.python_path), str(remote.runner_path), payload])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self._scp_from(remote_output, output_path)
        except AppError:
            raise
        except (OSError, subprocess.SubprocessError) as exc:
            raise AppError("RUNPOD_F5_FAILED", "RunPod F5-TTS-THAI V2 สร้างเสียงไม่สำเร็จ") from exc
        if not output_path.is_file() or output_path.stat().st_size <= 44:
            raise AppError("RUNPOD_F5_FAILED", "RunPod F5-TTS-THAI V2 ไม่ได้ส่งไฟล์ WAV กลับมา")
        return output_path

    def _prepare(self, reference: Path) -> str:
        remote = self.settings.runpod_f5
        digest = hashlib.sha256(reference.read_bytes()).hexdigest()[:16]
        remote_reference = f"{remote.workdir}/references/{digest}.wav"
        self._ssh(["mkdir", "-p", f"{remote.workdir}/references", f"{remote.workdir}/outputs"])
        if self._prepared_reference != remote_reference:
            runner = Path.cwd() / "scripts" / "runpod_f5_infer.py"
            if not runner.is_file():
                raise AppError("RUNPOD_F5_NOT_CONFIGURED", "ไม่พบ RunPod F5 inference runner ในโปรเจกต์")
            self._scp_to(runner, str(remote.runner_path))
            self._scp_to(reference, remote_reference)
            self._prepared_reference = remote_reference
        return remote_reference

    def _ssh(self, remote_args: list[str]) -> None:
        remote = self.settings.runpod_f5
        command = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-i", str(remote.ssh_key_path.expanduser()), "-p", str(remote.ssh_port), f"{remote.ssh_user}@{remote.ssh_host}", *remote_args]
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=remote.timeout_seconds, check=False)
        if completed.returncode:
            raise AppError("RUNPOD_F5_FAILED", "RunPod F5-TTS-THAI V2 remote command failed")

    def _scp_to(self, source: Path, remote_path: str) -> None:
        remote = self.settings.runpod_f5
        command = ["scp", "-P", str(remote.ssh_port), "-i", str(remote.ssh_key_path.expanduser()), str(source), f"{remote.ssh_user}@{remote.ssh_host}:{remote_path}"]
        if subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=remote.timeout_seconds, check=False).returncode:
            raise AppError("RUNPOD_F5_FAILED", "ไม่สามารถส่งไฟล์ไปยัง RunPod F5 ได้")

    def _scp_from(self, remote_path: str, output: Path) -> None:
        remote = self.settings.runpod_f5
        command = ["scp", "-P", str(remote.ssh_port), "-i", str(remote.ssh_key_path.expanduser()), f"{remote.ssh_user}@{remote.ssh_host}:{remote_path}", str(output)]
        if subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=remote.timeout_seconds, check=False).returncode:
            raise AppError("RUNPOD_F5_FAILED", "ไม่สามารถรับไฟล์เสียงจาก RunPod F5 ได้")


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
                # Keep Bird/F5 in the natural, stable range for Thai narration.
                # Values outside this range tend to produce rushed or unstable
                # prosody even when the caller requests a different speed.
                bird_speed = min(1.0, max(0.95, float(speed)))
                wav = self._tts.infer(
                    ref_audio=str(ref_voice),
                    ref_text=ref_text,
                    gen_text=text,
                    step=48,
                    cfg=2.2,
                    speed=bird_speed,
                    max_chars=240,
                )
                sf.write(str(output_path), wav, 24000)
                # Remove only long, low-level edges; retain a small natural
                # lead-in/out so words are not clipped.
                try:
                    import numpy as np
                    audio, sample_rate = sf.read(str(output_path))
                    level = np.max(np.abs(audio), axis=1) if getattr(audio, "ndim", 1) > 1 else np.abs(audio)
                    active = np.flatnonzero(level > 10 ** (-45 / 20))
                    if active.size:
                        pad = int(sample_rate * 0.06)
                        start = max(0, int(active[0]) - pad)
                        end = min(len(audio), int(active[-1]) + pad + 1)
                        sf.write(str(output_path), audio[start:end], sample_rate)
                except Exception:
                    # Trimming is an enhancement; never fail an otherwise
                    # valid generated narration because it is unavailable.
                    pass
        except AppError:
            raise
        except Exception as exc:
            raise AppError("TTS_GENERATION_FAILED", "Bird F5-TTS-THAI narration generation failed") from exc
        if not output_path.is_file() or output_path.stat().st_size <= 44:
            raise AppError("TTS_GENERATION_FAILED", "Bird F5-TTS-THAI produced no audio")
        return output_path


class KokoroThaiTtsProvider:
    """Wayu Kokoro Thai ONNX provider running in the dedicated Python 3.12 env."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def synthesize(self, text: str, language: str, voice: str, speed: float, output_path: Path) -> Path:
        if language.lower() not in {"th", "th-th"}:
            raise AppError("TTS_GENERATION_FAILED", "Kokoro Thai currently supports Thai language only")
        model_dir = Path(self.settings.tts.kokoro_model_dir)
        if not model_dir.is_absolute():
            model_dir = (Path.cwd() / model_dir).resolve()
        python = Path(self.settings.tts.kokoro_worker_python)
        if not python.is_absolute():
            # Do not call resolve(): venv/bin/python is a symlink and resolving
            # it would bypass the virtualenv back to the system interpreter.
            python = Path.cwd() / python
        worker = Path(__file__).with_name("kokoro_worker.py")
        if not model_dir.is_dir() or not python.is_file():
            raise AppError("TTS_GENERATION_FAILED", "Wayu Kokoro Thai runtime is not configured")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [str(python), str(worker), "--model-dir", str(model_dir), "--text", text,
                   "--voice", voice, "--speed", str(min(1.15, max(0.85, float(speed) * self.settings.tts.kokoro_speed))),
                   "--output", str(output_path)]
        last_diagnostic = ""
        for attempt in range(2):
            try:
                result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, check=False)
            except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
                if attempt == 1:
                    raise AppError("TTS_GENERATION_FAILED", "Wayu Kokoro Thai narration generation timed out") from exc
                continue
            if result.returncode == 0 and output_path.is_file() and output_path.stat().st_size > 44:
                return output_path
            last_diagnostic = (result.stderr or result.stdout or "").strip()[-400:]
        raise AppError("TTS_GENERATION_FAILED", "Wayu Kokoro Thai narration generation failed", {"diagnostic": last_diagnostic} if last_diagnostic else None)


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
    if name in {"google", "google-gemini", "gemini", "gemini-tts"}:
        if settings is None:
            raise AppError("TTS_GENERATION_FAILED", "Google Gemini TTS provider requires application settings")
        return GoogleGeminiTtsProvider(settings)
    if name in {"runpod-f5", "runpod-f5-thai"}:
        if settings is None:
            raise AppError("TTS_GENERATION_FAILED", "RunPod F5-TTS-THAI V2 provider requires application settings")
        return RunpodF5ThaiTtsProvider(settings)
    if name == "thonburian":
        if settings is None:
            raise AppError("TTS_GENERATION_FAILED", "Thonburian provider requires application settings")
        return ThonburianTtsProvider(settings)
    if name in {"bird", "bird-f5", "f5-thai", "f5-tts-thai"}:
        if settings is None:
            raise AppError("TTS_GENERATION_FAILED", "Bird F5-TTS-THAI provider requires application settings")
        return BirdF5ThaiTtsProvider(settings)
    if name in {"kokoro", "kokoro-thai", "wayu-kokoro-thai"}:
        if settings is None:
            raise AppError("TTS_GENERATION_FAILED", "Kokoro Thai provider requires application settings")
        if not settings.tts.kokoro_enabled:
            raise AppError("TTS_GENERATION_FAILED", "Wayu Kokoro Thai is disabled in configuration")
        return KokoroThaiTtsProvider(settings)
    if name in {"khanomtan", "khanom-tan", "khanomtan-tts"}:
        if settings is None:
            raise AppError("TTS_GENERATION_FAILED", "KhanomTan provider requires application settings")
        return KhanomTanTtsProvider(settings)
    raise AppError("TTS_GENERATION_FAILED", "Configured TTS provider is unavailable", {"provider": name})
