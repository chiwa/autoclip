from __future__ import annotations

import math
import wave
from pathlib import Path
from typing import Any

# Registry of space-themed relaxing background music tracks for Podcasts
PODCAST_BGM_TRACKS: list[dict[str, Any]] = [
    {
        "id": "cosmic_drift",
        "name": "🌌 Cosmic Drift (ล่องลอยในความเงียบงัน)",
        "description": "โทนอวกาศเวิ้งว้าง นุ่มลึก เบสอุ่นละมุน ไม่รบกวนเสียงพูด เหมาะสำหรับการพักผ่อน",
        "filename": "cosmic-drift.wav",
        "base_freqs": [130.81, 196.00, 246.94, 293.66],  # Cmaj9
        "cutoff_hz": 550.0,
        "lfo_rate": 0.04,
        "binaural_diff": 5.5,
    },
    {
        "id": "starlight_lullaby",
        "name": "✨ Starlight Lullaby (แสงดาวกล่อมนอน)",
        "description": "เสียงแอมเบียนต์ละมุนผสมฮาร์โมนิกดาวระยิบระยับแผ่วเบา ชวนเคลิ้มหลับสบาย",
        "filename": "starlight-lullaby.wav",
        "base_freqs": [174.61, 261.63, 329.63, 392.00],  # Fmaj9
        "cutoff_hz": 750.0,
        "lfo_rate": 0.05,
        "binaural_diff": 4.5,
    },
    {
        "id": "deep_nebula",
        "name": "🪐 Deep Nebula (เนบิวลาลึกภวังค์)",
        "description": "เสียงพัดพาของลมสุริยะและฮาร์โมนิกสมาธิ คลื่นเสียงเพื่อความผ่อนคลายลึก (Theta Waves)",
        "filename": "deep-nebula.wav",
        "base_freqs": [110.00, 164.81, 220.00, 277.18],  # A major warm drone
        "cutoff_hz": 500.0,
        "lfo_rate": 0.03,
        "binaural_diff": 6.0,
    },
    {
        "id": "interstellar_voyage",
        "name": "🚀 Interstellar Voyage (การเดินทางข้ามกาแล็กซี)",
        "description": "คอร์ดเมเจอร์อบอุ่น ให้ความรู้สึกสงบสุข ปลอดภัย และกว้างใหญ่ไร้ขอบเขต",
        "filename": "interstellar-voyage.wav",
        "base_freqs": [146.83, 185.00, 220.00, 329.63],  # Dadd9
        "cutoff_hz": 700.0,
        "lfo_rate": 0.05,
        "binaural_diff": 5.0,
    },
    {
        "id": "enceladus_ocean",
        "name": "🌊 Enceladus Ocean (มหาสมุทรใต้ผืนน้ำแข็ง)",
        "description": "เสียงบรรยากาศละมุนดั่งคลื่นเสียงสะท้อนใต้พิภพน้ำแข็ง อบอุ่นและน่าค้นหา",
        "filename": "enceladus-ocean.wav",
        "base_freqs": [164.81, 246.94, 369.99, 415.30],  # Eadd9
        "cutoff_hz": 600.0,
        "lfo_rate": 0.04,
        "binaural_diff": 5.5,
    },
]


def ensure_default_bgm(workspace: Path) -> Path:
    """Create a tiny, royalty-free ambient fallback once for packages without BGM."""
    target = workspace / "shared" / "music" / "default-ambient-v2.wav"
    if target.is_file():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    rate = 48000
    seconds = 30
    chords = ((220.0, 277.18, 329.63), (196.0, 246.94, 293.66), (174.61, 220.0, 261.63))
    with wave.open(str(target), "wb") as out:
        out.setparams((2, 2, rate, 0, "NONE", "not compressed"))
        for i in range(rate * seconds):
            t = i / rate
            chord = chords[int(t / 10) % len(chords)]
            sample = sum(math.sin(2 * math.pi * f * t) for f in chord) / 3 * 0.18
            value = int(32767 * sample)
            out.writeframesraw(value.to_bytes(2, "little", signed=True) * 2)
    return target


def _synthesize_space_track(
    output_path: Path,
    base_freqs: list[float],
    duration: float = 36.0,
    sample_rate: int = 48000,
    lfo_rate: float = 0.04,
    cutoff_hz: float = 600.0,
    binaural_diff: float = 5.5,
) -> Path:
    """Synthesize high-quality, seamlessly loopable relaxing space ambient audio."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import numpy as np
        import scipy.signal as signal

        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        n_samples = len(t)
        left = np.zeros(n_samples, dtype=np.float32)
        right = np.zeros(n_samples, dtype=np.float32)

        for idx, f in enumerate(base_freqs):
            amp = 1.0 / (idx + 1) ** 0.65
            detune_l = -0.35 + 0.1 * idx
            detune_r = 0.35 - 0.1 * idx

            sig_l = np.sin(2 * np.pi * (f + detune_l) * t)
            sig_l += 0.22 * np.sin(2 * np.pi * (f * 1.5 + detune_l) * t)
            sig_l += 0.12 * np.sin(2 * np.pi * (f * 2.0 + detune_l) * t)

            sig_r = np.sin(2 * np.pi * (f + detune_r + binaural_diff * (0.5 if idx == 0 else 0)) * t)
            sig_r += 0.22 * np.sin(2 * np.pi * (f * 1.5 + detune_r) * t)
            sig_r += 0.12 * np.sin(2 * np.pi * (f * 2.0 + detune_r) * t)

            lfo = 0.7 + 0.3 * np.sin(2 * np.pi * lfo_rate * (idx + 1) * 0.7 * t)
            left += sig_l * amp * lfo
            right += sig_r * amp * (1.4 - lfo)

        # Gentle filtered noise bed (solar wind)
        np.random.seed(int(base_freqs[0]) * 17)
        noise_l = np.random.normal(0, 0.06, n_samples).astype(np.float32)
        noise_r = np.random.normal(0, 0.06, n_samples).astype(np.float32)
        b_noise, a_noise = signal.butter(2, 200.0 / (sample_rate / 2), btype="low")
        left += signal.lfilter(b_noise, a_noise, noise_l) * 0.35
        right += signal.lfilter(b_noise, a_noise, noise_r) * 0.35

        # Warm lowpass filter
        b_lp, a_lp = signal.butter(2, cutoff_hz / (sample_rate / 2), btype="low")
        left = signal.lfilter(b_lp, a_lp, left)
        right = signal.lfilter(b_lp, a_lp, right)

        # Seamless loop crossfade (last 4 seconds into first 4 seconds)
        xfade_len = int(sample_rate * 4.0)
        fade_out = np.linspace(1.0, 0.0, xfade_len, dtype=np.float32)
        fade_in = np.linspace(0.0, 1.0, xfade_len, dtype=np.float32)
        tail_l = left[-xfade_len:] * fade_out
        tail_r = right[-xfade_len:] * fade_out
        left[:xfade_len] = left[:xfade_len] * fade_in + tail_l
        right[:xfade_len] = right[:xfade_len] * fade_in + tail_r

        loop_len = n_samples - xfade_len
        left = left[:loop_len]
        right = right[:loop_len]

        peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-6)
        target_peak = 0.65
        left = (left / peak) * target_peak
        right = (right / peak) * target_peak

        left_int16 = (left * 32767).astype(np.int16)
        right_int16 = (right * 32767).astype(np.int16)
        interleaved = np.empty((len(left_int16) * 2,), dtype=np.int16)
        interleaved[0::2] = left_int16
        interleaved[1::2] = right_int16

        with wave.open(str(output_path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(interleaved.tobytes())
    except Exception:
        # Fallback pure-python synthesis if numpy/scipy encounter any issue
        with wave.open(str(output_path), "wb") as wf:
            wf.setparams((2, 2, sample_rate, 0, "NONE", "not compressed"))
            for i in range(int(sample_rate * 30)):
                t_sec = i / sample_rate
                val = sum(math.sin(2 * math.pi * f * t_sec) for f in base_freqs) / len(base_freqs) * 0.2
                int_val = int(32767 * val)
                wf.writeframesraw(int_val.to_bytes(2, "little", signed=True) * 2)

    return output_path


SOUNDS_DIR = Path(__file__).resolve().parents[2] / "assets" / "sounds"
SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
DEFAULT_PODCAST_BGM = "mamase-podcast-bg.mp3"


KNOWN_METADATA: dict[str, dict[str, str]] = {
    "mamase-podcast-bg.mp3": {
        "name": "🎧 Mamase Podcast BGM (ค่าเริ่มต้นใหม่)",
        "description": "เพลงประกอบ Podcast หลักของ Mamase จากไฟล์ที่พี่พีเลือก",
    },
    "space.mp3": {
        "name": "🌌 space.mp3 (เพลงเดิม)",
        "description": "เพลงอวกาศผ่อนคลายเดิมจาก /assets/sounds/space.mp3",
    },
    "deep-nebula.wav": {
        "name": "🪐 deep-nebula.wav — Deep Nebula (เนบิวลาลึกภวังค์ — แนะนำ)",
        "description": "เนบิวลาลึกภวังค์ เสียงแอมเบียนต์อบอุ่นโอบอุ้มจิตใจ ผสมผสานคลื่น Theta Wave ช่วยให้ผ่อนคลายลึกและหลับสบาย",
    },
    "cosmic-drift.wav": {
        "name": "🌌 cosmic-drift.wav — Cosmic Drift (ล่องลอยในความเงียบงัน)",
        "description": "โทนอวกาศเวิ้งว้าง นุ่มลึก เบสอุ่นละมุน ไม่รบกวนเสียงพูด เหมาะสำหรับการพักผ่อน",
    },
    "starlight-lullaby.wav": {
        "name": "✨ starlight-lullaby.wav — Starlight Lullaby (แสงดาวกล่อมนอน)",
        "description": "แสงดาวกล่อมนอน แอมเบียนต์นุ่มละมุนผสมประกายดาวแผ่วเบา ช่วยคลายความเหนื่อยล้า",
    },
    "interstellar-voyage.wav": {
        "name": "🚀 interstellar-voyage.wav — Interstellar Voyage (การเดินทางข้ามกาแล็กซี)",
        "description": "การเดินทางข้ามกาแล็กซี คอร์ดเมเจอร์อบอุ่น ช้าๆ ให้ความรู้สึกสงบ ปลอดภัย ไร้กังวล",
    },
    "enceladus-ocean.wav": {
        "name": "🌊 enceladus-ocean.wav — Enceladus Ocean (มหาสมุทรใต้ผืนน้ำแข็ง)",
        "description": "มหาสมุทรใต้ผืนน้ำแข็ง คลื่นเสียงกังวานลุ่มลึก ชวนหลับสนิทตลอดคืน",
    },
}


def get_podcast_bgm_catalog(sounds_dir: Path | None = None) -> list[dict[str, Any]]:
    """Return client-safe catalog of podcast background tracks.

    Includes:
    1. The configured Mamase MP3 as default, plus other files in /assets/sounds.
    2. Priority ordering: default track first, then other asset files.
    3. Built-in ambient tracks (aliased or fallback).
    """
    directory = (sounds_dir or SOUNDS_DIR).resolve()
    directory.mkdir(parents=True, exist_ok=True)

    tracks: list[dict[str, Any]] = []
    builtin_filenames = {t["filename"].lower() for t in PODCAST_BGM_TRACKS}

    # 1. Files from /assets/sounds (excluding built-in files to avoid duplicate entries)
    found_files = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS and not f.name.startswith(".") and f.name.lower() not in builtin_filenames
    ]

    def sort_key(p: Path) -> tuple[int, str]:
        name = p.name.lower()
        if name == DEFAULT_PODCAST_BGM:
            return (0, name)
        return (1, name)

    sorted_files = sorted(found_files, key=sort_key)

    for f in sorted_files:
        is_default = (f.name.lower() == DEFAULT_PODCAST_BGM)
        meta = KNOWN_METADATA.get(f.name.lower())
        display_name = meta["name"] if meta else f"🎵 {f.name}"
        desc = meta["description"] if meta else f"ไฟล์เสียง {f.name} จาก /assets/sounds"
        tracks.append({
            "id": f.name,
            "name": display_name,
            "description": desc,
            "filename": f.name,
            "is_default": is_default,
            "source": "assets_sounds",
        })

    # Keep a client-safe default entry even if the local asset is temporarily missing.
    if not any(t["id"] == DEFAULT_PODCAST_BGM for t in tracks):
        tracks.insert(0, {
            "id": DEFAULT_PODCAST_BGM,
            "name": "🎧 Mamase Podcast BGM (ค่าเริ่มต้นใหม่)",
            "description": "เพลงประกอบ Podcast หลักของ Mamase จากไฟล์ที่พี่พีเลือก",
            "filename": DEFAULT_PODCAST_BGM,
            "is_default": True,
            "source": "assets_sounds",
        })

    # 2. Built-in ambient space tracks
    for t in PODCAST_BGM_TRACKS:
        tracks.append({
            "id": t["id"],
            "name": t["name"],
            "description": t["description"],
            "filename": t["filename"],
            "is_default": False,
            "source": "builtin",
        })

    return tracks


def ensure_space_ambient_track(workspace: Path, track_id: str) -> Path:
    """Ensure procedural space ambient BGM track exists on disk and return its path."""
    track_info = next(
        (t for t in PODCAST_BGM_TRACKS if t["id"] == track_id or t["filename"] == track_id),
        None,
    )
    if track_info is None:
        track_info = PODCAST_BGM_TRACKS[0]

    target = workspace / "shared" / "music" / track_info["filename"]
    if target.is_file() and target.stat().st_size > 1000:
        return target

    return _synthesize_space_track(
        output_path=target,
        base_freqs=track_info["base_freqs"],
        duration=36.0,
        sample_rate=48000,
        lfo_rate=track_info["lfo_rate"],
        cutoff_hz=track_info["cutoff_hz"],
        binaural_diff=track_info["binaural_diff"],
    )


def ensure_podcast_bgm(workspace: Path, track_id: str = DEFAULT_PODCAST_BGM) -> Path:
    """Ensure podcast BGM track is available on disk and return its path."""
    return resolve_podcast_bgm(workspace, track_id)


def resolve_podcast_bgm(
    workspace: Path,
    track_id: str | None = None,
    sounds_dir: Path | None = None,
) -> Path:
    """Resolve a Podcast BGM, defaulting to the selected Mamase track."""
    directory = (sounds_dir or SOUNDS_DIR).resolve()
    directory.mkdir(parents=True, exist_ok=True)

    target_name = (track_id or "").strip()
    if not target_name or target_name in {"default", "system"}:
        target_name = DEFAULT_PODCAST_BGM
    elif "/" in target_name or "\\" in target_name:
        target_name = Path(target_name).name

    # 1. Check if it's a file in /assets/sounds
    candidate = (directory / target_name).resolve()
    if candidate.is_file() and candidate.parent == directory:
        return candidate

    # 2. Check if it's one of the built-in ambient tracks (id or filename)
    ambient_match = next(
        (t for t in PODCAST_BGM_TRACKS if t["id"] == target_name or t["filename"] == target_name),
        None,
    )
    if ambient_match:
        return ensure_space_ambient_track(workspace, ambient_match["id"])

    # Fallback 1: selected Mamase default, then the legacy space.mp3.
    for fallback_name in (DEFAULT_PODCAST_BGM, "space.mp3"):
        fallback = directory / fallback_name
        if fallback.is_file():
            return fallback

    # Fallback 2: default workspace bgm
    return ensure_default_bgm(workspace)
