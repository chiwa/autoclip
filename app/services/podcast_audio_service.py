from __future__ import annotations

import hashlib
import json
import logging
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable

from app.config.settings import Settings
from app.domain.errors import AppError
from app.infrastructure.ffmpeg import FfmpegRunner, FfprobeRunner
from app.infrastructure.tts.providers import TtsProvider

logger = logging.getLogger("autoclip.podcast.audio")


class PodcastAudioService:
    """Manages parallel TTS synthesis, retries, chunk caching, and stitching for podcast scripts."""

    def __init__(self, ffmpeg: FfmpegRunner, ffprobe: FfprobeRunner, settings: Settings):
        self.ffmpeg = ffmpeg
        self.ffprobe = ffprobe
        self.settings = settings

    @staticmethod
    def _text_hash(text: str, style_prompt: str | None = None) -> str:
        content = f"v2\n{text}\n---\n{style_prompt or ''}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _polish_chunk_audio(self, chunk_file: Path, pad_seconds: float = 0.35, fade_ms: float = 20.0) -> None:
        """Applies gentle micro-fades (de-click) and natural breath pause padding to a synthesized chunk."""
        if not chunk_file.is_file() or chunk_file.stat().st_size <= 44:
            return
        tmp_file = chunk_file.with_name(f"{chunk_file.stem}_polished{chunk_file.suffix}")
        try:
            dur = self.ffprobe.duration(chunk_file)
            if dur <= 0.1:
                return
            fade_sec = fade_ms / 1000.0
            fade_out_st = max(0.0, dur - fade_sec)
            self.ffmpeg.run(
                [
                    "-y",
                    "-i", str(chunk_file),
                    "-af", f"afade=t=in:st=0:d={fade_sec:.3f},afade=t=out:st={fade_out_st:.3f}:d={fade_sec:.3f},apad=pad_dur={pad_seconds:.3f}",
                    str(tmp_file),
                ],
                "PODCAST_AUDIO_POLISH_FAILED",
            )
            if tmp_file.is_file() and tmp_file.stat().st_size > 44:
                tmp_file.replace(chunk_file)
        except Exception:
            logger.warning("Failed to polish chunk audio for %s; using unpolished audio", chunk_file.name)
            if tmp_file.is_file():
                tmp_file.unlink(missing_ok=True)

    def synthesize_and_stitch(
        self,
        job_id: str,
        workspace_root: Path,
        chunks: list[str],
        provider: TtsProvider,
        voice: str,
        speed: float,
        style_prompt: str | None = None,
        language: str = "th-TH",
        progress_callback: Callable[[int, int, str], None] | None = None,
        log_callback: Callable[[str, str, bool], None] | None = None,
    ) -> tuple[Path, list[float], float]:
        """Synthesizes audio for all chunks in parallel with retries, caching, and stitches them.

        Returns:
            (stitched_audio_path, chunk_durations, total_duration)
        """
        if not chunks:
            raise AppError("PODCAST_SCRIPT_EMPTY", "บทพูดพอดแคสต์ว่างเปล่า")

        chunks_dir = workspace_root / "podcast_chunks"
        chunks_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = chunks_dir / "manifest.json"

        cached_manifest: dict[str, dict] = {}
        if manifest_path.is_file():
            try:
                cached_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                cached_manifest = {}

        total_chunks = len(chunks)
        max_retries = self.settings.podcast.max_retries
        concurrency = min(total_chunks, self.settings.podcast.concurrency)

        if log_callback:
            log_callback("INFO", f"แบ่งบทเป็น {total_chunks} ส่วน (ประมวลผลพร้อมกัน {concurrency} ส่วน)", False)

        # Set style prompt on provider if supported
        if style_prompt and hasattr(provider, "style_prompt"):
            provider.style_prompt = style_prompt

        def process_chunk(index: int, text: str) -> tuple[int, Path, float]:
            chunk_file = chunks_dir / f"chunk_{index:04d}.wav"
            text_h = self._text_hash(text, style_prompt)
            byte_count = len(text.encode("utf-8"))

            # Check cache / reuse
            cache_key = str(index)
            cached_info = cached_manifest.get(cache_key)
            if (
                cached_info
                and cached_info.get("hash") == text_h
                and cached_info.get("voice") == voice
                and math.isclose(cached_info.get("speed", 1.0), speed, rel_tol=1e-3)
                and chunk_file.is_file()
                and chunk_file.stat().st_size > 44
            ):
                duration = float(cached_info.get("duration") or self.ffprobe.duration(chunk_file))
                if log_callback:
                    log_callback("INFO", f"ใช้เสียงเดิมส่วนที่ {index + 1} จาก {total_chunks} (cache)", False)
                    log_callback("TECHNICAL", f"event=chunk_cache_hit job_id={job_id} chunk={index+1}/{total_chunks} bytes={byte_count} duration={round(duration, 3)}s", True)
                return index, chunk_file, duration

            # Synthesize with exponential backoff retries
            attempt = 0
            start_time = time.monotonic()
            last_exception: Exception | None = None

            while attempt <= max_retries:
                try:
                    if log_callback and attempt > 0:
                        log_callback("WARNING", f"ลองสร้างเสียงส่วนที่ {index + 1} ใหม่ (ครั้งที่ {attempt})", False)

                    provider.synthesize(text, language, voice, speed, chunk_file)
                    self._polish_chunk_audio(chunk_file)
                    duration = self.ffprobe.duration(chunk_file)
                    elapsed = round(time.monotonic() - start_time, 2)

                    if log_callback:
                        log_callback("TECHNICAL", f"event=chunk_synthesized job_id={job_id} chunk={index+1}/{total_chunks} bytes={byte_count} voice={voice} speed={speed} retry={attempt} duration={round(duration, 3)}s elapsed={elapsed}s", True)

                    return index, chunk_file, duration
                except Exception as exc:
                    last_exception = exc
                    attempt += 1
                    if attempt <= max_retries:
                        backoff = min(10.0, (2 ** (attempt - 1)) * 1.5)
                        time.sleep(backoff)

            elapsed = round(time.monotonic() - start_time, 2)
            if log_callback:
                log_callback("ERROR", f"สร้างเสียงส่วนที่ {index + 1} ไม่สำเร็จ (ลอง {max_retries} ครั้ง)", False)
                log_callback("TECHNICAL", f"event=chunk_failed job_id={job_id} chunk={index+1}/{total_chunks} bytes={byte_count} retry={attempt} elapsed={elapsed}s error={str(last_exception)}", True)

            raise AppError(
                "PODCAST_TTS_CHUNK_FAILED",
                f"สร้างเสียงส่วนที่ {index + 1} ไม่สำเร็จหลังลองซ้ำ {max_retries} ครั้ง",
                {"chunkIndex": index, "totalChunks": total_chunks},
            ) from last_exception

        durations_by_index: dict[int, float] = {}
        paths_by_index: dict[int, Path] = {}
        completed_count = 0

        with ThreadPoolExecutor(max_workers=concurrency, thread_name_prefix="podcast-tts") as executor:
            futures = {
                executor.submit(process_chunk, idx, chunk_text): (idx, chunk_text)
                for idx, chunk_text in enumerate(chunks)
            }

            for future in as_completed(futures):
                idx, chunk_text = futures[future]
                try:
                    index, path, duration = future.result()
                    durations_by_index[index] = duration
                    paths_by_index[index] = path
                    completed_count += 1

                    # Update manifest entry
                    cached_manifest[str(index)] = {
                        "hash": self._text_hash(chunk_text, style_prompt),
                        "voice": voice,
                        "speed": speed,
                        "style_prompt": style_prompt or "",
                        "duration": duration,
                        "file": path.name,
                    }
                    try:
                        manifest_path.write_text(json.dumps(cached_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
                    except Exception:
                        pass

                    if progress_callback:
                        progress_callback(completed_count, total_chunks, f"กำลังสร้างเสียงส่วนที่ {completed_count} จาก {total_chunks}")
                    if log_callback:
                        log_callback("SUCCESS", f"สร้างเสียงส่วนที่ {completed_count} จาก {total_chunks} สำเร็จ", False)
                except Exception:
                    # Cancel remaining pending tasks
                    for pending in futures:
                        pending.cancel()
                    raise

        # Order chunk results deterministically 0..N-1
        chunk_paths = [paths_by_index[i] for i in range(total_chunks)]
        chunk_durations = [durations_by_index[i] for i in range(total_chunks)]

        # Stitch audio files together using FFmpeg concat demuxer
        concat_list_file = chunks_dir / "concat_list.txt"
        with concat_list_file.open("w", encoding="utf-8") as f:
            for p in chunk_paths:
                f.write(f"file '{p.resolve().as_posix()}'\n")

        output_audio = workspace_root / "full_narration.wav"
        if log_callback:
            log_callback("INFO", "กำลังต่อเสียงแต่ละส่วนตามลำดับเดิม", False)
            log_callback("TECHNICAL", f"event=stitch_started job_id={job_id} total_chunks={total_chunks}", True)

        self.ffmpeg.run(
            [
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list_file),
                "-c:a", "pcm_s16le",
                "-ar", "48000",
                "-ac", "2",
                str(output_audio),
            ],
            "PODCAST_AUDIO_STITCH_FAILED",
        )

        total_duration = self.ffprobe.duration(output_audio)
        if log_callback:
            log_callback("SUCCESS", f"รวมเสียงบรรยายเสร็จสิ้น ความยาวรวม {round(total_duration, 1)} วินาที", False)
            log_callback("TECHNICAL", f"event=stitch_completed job_id={job_id} total_duration={round(total_duration, 3)}s", True)

        return output_audio, chunk_durations, total_duration
