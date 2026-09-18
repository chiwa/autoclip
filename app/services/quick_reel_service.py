from __future__ import annotations

import json
import logging
import math
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from app.config.settings import Settings
from app.domain.enums import JobStatus
from app.domain.errors import AppError, public_error
from app.domain.events import JobEvent, JobEventType
from app.domain.models import JobRecord, Scene, Script
from app.infrastructure.ffmpeg import FfmpegRunner, FfprobeRunner, build_ffmpeg_metadata_args
from app.infrastructure.tts import create_tts_provider
from app.services.bgm_service import resolve_podcast_bgm
from app.services.narration_audio_service import NarrationAudioProcessor
from app.services.persistence import Persistence
from app.services.video_service import RenderProfile, SceneRenderer, SubtitleRenderer, VideoComposer, srt_timestamp
from app.services.zodiac_service import TTS_STYLE as ZODIAC_TTS_STYLE

logger = logging.getLogger("autoclip.quick_reel")

SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
SAFE_MARGIN_WIDTH = 920
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
MAX_QUICK_REEL_IMAGES = 20
QUICK_REEL_TRANSITION_SECONDS = 0.4

QUICK_REEL_TTS_STYLE = ZODIAC_TTS_STYLE


class QuickReelService:
    @staticmethod
    def _synthesize_narration(provider, text: str, output: Path, voice: str, speed: float, style_prompt: str | None = None) -> Path:
        """Call every TTS provider through the shared positional contract."""
        if hasattr(provider, "style_prompt"):
            provider.style_prompt = (style_prompt or "").strip() or QUICK_REEL_TTS_STYLE
        return provider.synthesize(text, "th-TH", voice, speed, output)

    @staticmethod
    def _process_narration(processor, audio_path: Path) -> tuple[Path, float]:
        """The shared processor mutates the audio atomically and returns duration."""
        return audio_path, processor.process(audio_path)

    """Creates 9:16 Reels from one or more ordered images and one TTS script."""

    def __init__(
        self,
        settings: Settings,
        ffmpeg: FfmpegRunner,
        ffprobe: FfprobeRunner,
        job_service: Any,
        persistence: Persistence | None = None,
        assets_root: Path | None = None,
    ):
        self.settings = settings
        self.ffmpeg = ffmpeg
        self.ffprobe = ffprobe
        self.job_service = job_service
        self.persistence = persistence
        self.assets_root = assets_root or (Path(__file__).resolve().parents[2] / "assets")
        self.font_path = self.assets_root / "fonts" / "Kanit-Bold.ttf"
        if not self.font_path.is_file():
            alt_font = self.assets_root / "fonts" / "Prompt-Bold.ttf"
            if alt_font.is_file():
                self.font_path = alt_font

    def prepare_image(
        self,
        image_path: Path,
        output_path: Path,
        fit: str = "contain",
        target_width: int = TARGET_WIDTH,
        target_height: int = TARGET_HEIGHT,
    ) -> Path:
        """Processes and formats an image to target width/height frame.

        - cover: Center-crop to fill frame without distortion.
        - contain: Letterbox with dark background (18, 20, 26).
        """
        if not image_path.is_file() or image_path.suffix.lower() not in SUPPORTED_IMAGE_EXTS:
            raise AppError("QUICK_REEL_IMAGE_INVALID", "ไฟล์ภาพต้องเป็น PNG, JPG, JPEG หรือ WebP")

        try:
            with Image.open(image_path) as im:
                orig_w, orig_h = im.size

                if im.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", im.size, (18, 20, 26))
                    alpha = im.convert("RGBA").split()[-1]
                    bg.paste(im, mask=alpha)
                    rgb_im = bg
                else:
                    rgb_im = im.convert("RGB")

                fit_mode = (fit or "contain").strip().lower()

                if fit_mode == "contain":
                    scale = min(target_width / orig_w, target_height / orig_h)
                    new_w = max(1, int(round(orig_w * scale)))
                    new_h = max(1, int(round(orig_h * scale)))
                    scaled = rgb_im.resize((new_w, new_h), Image.Resampling.LANCZOS)

                    canvas = Image.new("RGB", (target_width, target_height), (18, 20, 26))
                    left = (target_width - new_w) // 2
                    top = (target_height - new_h) // 2
                    canvas.paste(scaled, (left, top))
                    result = canvas
                else:
                    scale = max(target_width / orig_w, target_height / orig_h)
                    new_w = max(1, int(round(orig_w * scale)))
                    new_h = max(1, int(round(orig_h * scale)))
                    scaled = rgb_im.resize((new_w, new_h), Image.Resampling.LANCZOS)

                    left = (new_w - target_width) // 2
                    top = (new_h - target_height) // 2
                    result = scaled.crop((left, top, left + target_width, top + target_height))

                output_path.parent.mkdir(parents=True, exist_ok=True)
                result.save(output_path, format="PNG")
                return output_path
        except AppError:
            raise
        except Exception as exc:
            raise AppError("QUICK_REEL_IMAGE_INVALID", f"ไม่สามารถประมวลผลไฟล์ภาพได้: {exc}") from exc

    def apply_hook_overlay(
        self,
        image_path: Path,
        hook_text: str,
        position: str = "top",
        output_path: Path | None = None,
    ) -> Path:
        """Overlays large mobile-readable hook text onto image with stroke/shadow."""
        target_path = output_path or image_path
        cleaned_text = (hook_text or "").strip()
        if not cleaned_text:
            return image_path

        with Image.open(image_path) as im:
            base = im.convert("RGBA")
            im_w, im_h = base.size
            overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            safe_margin_width = im_w - 160

            font_size = 64
            font: Any = None
            if self.font_path and self.font_path.is_file():
                try:
                    font = ImageFont.truetype(str(self.font_path), font_size)
                except Exception:
                    font = ImageFont.load_default()
            else:
                font = ImageFont.load_default()

            words = cleaned_text.split()
            lines: list[str] = []
            current_line = ""

            for word in words:
                test_line = f"{current_line} {word}".strip()
                bbox = draw.textbbox((0, 0), test_line, font=font)
                line_w = bbox[2] - bbox[0]
                if line_w <= safe_margin_width or not current_line:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            line_spacing = 18
            total_text_h = 0
            line_dimensions: list[tuple[int, int]] = []
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                lw = bbox[2] - bbox[0]
                lh = bbox[3] - bbox[1]
                line_dimensions.append((lw, lh))
                total_text_h += lh + line_spacing
            total_text_h = max(0, total_text_h - line_spacing)

            pos = (position or "top").strip().lower()
            if pos == "center":
                start_y = (im_h - total_text_h) // 2
            elif pos == "bottom":
                # For 1920 height, bottom was 1420 (500px from bottom)
                start_y = im_h - 500 - total_text_h
                if start_y < 0: start_y = (im_h - total_text_h) // 2
            else:
                start_y = 180

            curr_y = start_y
            for line, (lw, lh) in zip(lines, line_dimensions):
                x = (im_w - lw) // 2
                draw.text(
                    (x, curr_y),
                    line,
                    font=font,
                    fill=(255, 255, 255, 255),
                    stroke_width=5,
                    stroke_fill=(0, 0, 0, 230),
                )
                curr_y += lh + line_spacing

            composed = Image.alpha_composite(base, overlay).convert("RGB")
            composed.save(target_path, format="PNG")
            return target_path

    def _render_multi_image_slideshow(
        self,
        images: list[Path],
        narration: Path,
        subtitle: Path | None,
        audio_duration: float,
        motion: str,
        output: Path,
        image_durations: list[float] | None = None,
        target_width: int = TARGET_WIDTH,
        target_height: int = TARGET_HEIGHT,
    ) -> Path:
        """Render ordered images with equal screen time and visual crossfades.

        Narration stays as one continuous stream and is attached only after
        the visual timeline is complete, so a transition can never clip or
        crossfade spoken words.
        """
        if len(images) < 2:
            raise ValueError("multi-image slideshow requires at least two images")

        profile = RenderProfile(target_width, target_height, 30, "libx264", "yuv420p")
        renderer = SceneRenderer(self.ffmpeg, self.settings, profile)
        transition = min(
            QUICK_REEL_TRANSITION_SECONDS,
            max(0.05, audio_duration / (len(images) * 3)),
        )
        if image_durations is not None:
            if len(image_durations) != len(images) or any(duration <= 0 for duration in image_durations):
                raise ValueError("image durations must match images and be positive")
            source_durations = [
                duration + (transition if index < len(images) - 1 else 0.0)
                for index, duration in enumerate(image_durations)
            ]
        else:
            equal_duration = (audio_duration + transition * (len(images) - 1)) / len(images)
            source_durations = [equal_duration] * len(images)
        motion_cycle = (
            "slow_zoom_in",
            "documentary_pan",
            "slow_zoom_out",
            "pan_right_to_left",
        )

        visual_only = output.with_name("slideshow-visual.mp4")
        temp_dir = output.parent / "slideshow-temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        # 1. Render scene parts (head, main, tail)
        pieces = []
        for index, image in enumerate(images):
            is_last = (index == len(images) - 1)
            is_first = (index == 0)
            image_duration = source_durations[index]
            if motion in {"gentle_float", "cinematic_push_in", "hook_punch_in"}:
                selected_motion = motion
            elif motion != "none":
                selected_motion = motion_cycle[index % len(motion_cycle)]
            else:
                selected_motion = "none"

            input_args: list[str] = []
            if selected_motion == "none":
                input_args.extend(["-loop", "1", "-t", f"{image_duration:.3f}", "-i", str(image)])
            else:
                input_args.extend(["-i", str(image)])

            motion_speed = "normal" if selected_motion in {"cinematic_push_in", "hook_punch_in"} else "slow"
            motion_intensity = 0.18 if selected_motion in {"cinematic_push_in", "hook_punch_in"} else (0.12 if selected_motion == "gentle_float" else 0.04)

            visual_scene = Scene(
                id=f"quick-image-{index + 1:03d}",
                image=image.name,
                narration="visual only",
                tts_text="visual only",
                subtitle="",
                motion=selected_motion,
                motion_speed=motion_speed,
                motion_intensity=motion_intensity,
                focus="center",
                transition="dissolve",
                show_subtitle=False,
            )
            visual_filter = renderer.build_filter(visual_scene, image_duration, None)

            head_dur = transition if not is_first else 0.0
            tail_dur = transition if not is_last else 0.0
            main_dur = image_duration - head_dur - tail_dur

            splits = 1 + (1 if head_dur > 0 else 0) + (1 if tail_dur > 0 else 0)
            full_filter = f"[0:v]{visual_filter},trim=duration={image_duration:.3f},settb=AVTB,setpts=PTS-STARTPTS[v_full];[v_full]split={splits}"

            split_outs = []
            if head_dur > 0: split_outs.append("[v_head]")
            split_outs.append("[v_main]")
            if tail_dur > 0: split_outs.append("[v_tail]")

            full_filter += "".join(split_outs) + ";"

            maps = []
            piece_paths = {}

            if head_dur > 0:
                full_filter += f"[v_head]trim=start=0:end={head_dur:.3f},setpts=PTS-STARTPTS[out_head];"
                head_path = temp_dir / f"head_{index:03d}.mp4"
                maps.extend(["-map", "[out_head]", "-c:v", profile.codec, "-preset", "ultrafast", "-crf", "18", "-pix_fmt", profile.pixel_format, "-r", str(profile.fps), str(head_path)])
                piece_paths['head'] = head_path

            main_start = head_dur
            main_end = head_dur + main_dur
            full_filter += f"[v_main]trim=start={main_start:.3f}:end={main_end:.3f},setpts=PTS-STARTPTS[out_main];"
            main_path = temp_dir / f"main_{index:03d}.mp4"
            maps.extend(["-map", "[out_main]", "-c:v", profile.codec, "-preset", "veryfast", "-crf", "23", "-pix_fmt", profile.pixel_format, "-r", str(profile.fps), "-video_track_timescale", "30000", str(main_path)])
            piece_paths['main'] = main_path

            if tail_dur > 0:
                tail_start = image_duration - tail_dur
                full_filter += f"[v_tail]trim=start={tail_start:.3f}:end={image_duration:.3f},setpts=PTS-STARTPTS[out_tail];"
                tail_path = temp_dir / f"tail_{index:03d}.mp4"
                maps.extend(["-map", "[out_tail]", "-c:v", profile.codec, "-preset", "ultrafast", "-crf", "18", "-pix_fmt", profile.pixel_format, "-r", str(profile.fps), str(tail_path)])
                piece_paths['tail'] = tail_path

            full_filter = full_filter.rstrip(";")

            self.ffmpeg.run(
                [
                    *input_args,
                    "-filter_complex", full_filter,
                    "-an", *maps
                ],
                "QUICK_REEL_SLIDESHOW_FAILED",
            )
            pieces.append(piece_paths)

        # 2. Crossfade transitions and build concat list
        concat_list_path = temp_dir / "concat.txt"
        concat_lines = []

        for index, p in enumerate(pieces):
            concat_lines.append(f"file '{p['main'].name}'")
            if 'tail' in p:
                next_p = pieces[index + 1]
                trans_path = temp_dir / f"trans_{index:03d}.mp4"
                self.ffmpeg.run(
                    [
                        "-i", str(p['tail']),
                        "-i", str(next_p['head']),
                        "-filter_complex",
                        f"[0:v]setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS[v1];[v0][v1]xfade=transition=fade:duration={transition:.3f}:offset=0[v]",
                        "-map", "[v]", "-an", "-t", f"{transition:.3f}",
                        "-c:v", profile.codec, "-preset", "veryfast", "-crf", "23",
                        "-pix_fmt", profile.pixel_format, "-r", str(profile.fps),
                        "-video_track_timescale", "30000",
                        str(trans_path)
                    ],
                    "QUICK_REEL_SLIDESHOW_FAILED",
                )
                concat_lines.append(f"file '{trans_path.name}'")

        # 3. Concat all parts
        with open(concat_list_path, "w") as f:
            f.write("\n".join(concat_lines))

        self.ffmpeg.run(
            [
                "-f", "concat", "-safe", "0", "-i", str(concat_list_path),
                "-c", "copy", str(visual_only)
            ],
            "QUICK_REEL_SLIDESHOW_FAILED",
        )

        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        final_scene = Scene(
            id="quick-reel-slideshow",
            image=images[0].name,
            narration="continuous narration",
            tts_text="continuous narration",
            subtitle="",
            motion="none",
            motion_speed="slow",
            motion_intensity=0.04,
            focus="center",
            transition="none",
            show_subtitle=bool(subtitle),
        )
        final_filter = renderer.build_filter(final_scene, audio_duration, subtitle)
        # xfade/zoompan can finish one frame before the narration because of
        # frame-time rounding. Clone the final frame briefly, then cap at the
        # measured audio duration so the picture never ends first.
        final_filter += ",tpad=stop_mode=clone:stop_duration=0.100"
        self.ffmpeg.run(
            [
                "-i", str(visual_only), "-i", str(narration),
                "-t", f"{audio_duration:.3f}", "-vf", final_filter,
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", profile.codec, "-preset", "veryfast", "-crf", "23",
                "-pix_fmt", profile.pixel_format, "-r", str(profile.fps),
                "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "160k",
                "-movflags", "+faststart", "-shortest", str(output),
            ],
            "QUICK_REEL_SLIDESHOW_FAILED",
        )
        return output

    def _concat_narration_segments(self, segments: list[Path], output: Path) -> Path:
        if not segments:
            raise ValueError("at least one narration segment is required")
        if len(segments) == 1:
            shutil.copy(segments[0], output)
            return output
        inputs: list[str] = []
        for segment in segments:
            inputs.extend(["-i", str(segment)])
        concat_inputs = "".join(f"[{index}:a]" for index in range(len(segments)))
        self.ffmpeg.run(
            [
                *inputs,
                "-filter_complex", f"{concat_inputs}concat=n={len(segments)}:v=0:a=1[a]",
                "-map", "[a]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(output),
            ],
            "QUICK_REEL_TTS_CONCAT_FAILED",
        )
        return output

    @staticmethod
    def _write_segment_subtitles(texts: list[str], durations: list[float], output: Path) -> Path:
        if len(texts) != len(durations):
            raise ValueError("subtitle texts and durations must have the same length")
        blocks: list[str] = []
        start = 0.0
        for index, (text, duration) in enumerate(zip(texts, durations), 1):
            end = start + duration
            blocks.append(f"{index}\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{text}\n")
            start = end
        output.write_text("\n".join(blocks), encoding="utf-8")
        return output

    def submit_quick_reel(
        self,
        image_file: Any | None,
        script_text: str,
        image_files: list[Any] | None = None,
        tts_segments: list[str] | None = None,
        voice: str = "Iapetus",
        speed: float = 1.10,
        style_prompt: str | None = None,
        motion: str = "static",
        fit: str = "contain",
        hook_enabled: bool = False,
        hook_text: str = "",
        hook_position: str = "top",
        subtitles_enabled: bool = True,
        bgm_enabled: bool = False,
        bgm_track: str = "cosmic_drift",
        bgm_file: Any | None = None,
        bgm_volume: float = 0.10,
        title: str = "",
        description: str = "",
        hashtags: str = "",
        channel_id: str = "undefined",
    ) -> JobRecord:
        """Validates inputs, initializes workspace, and launches background render task."""
        cleaned_segments = [item.strip() for item in (tts_segments or []) if isinstance(item, str) and item.strip()]
        cleaned_script = "\n\n".join(cleaned_segments) if tts_segments is not None else (script_text or "").strip()
        if not cleaned_script:
            raise AppError("QUICK_REEL_SCRIPT_EMPTY", "กรุณาใส่บทพูดสำหรับ Quick Reel")

        cleaned_title = (title or "").strip() or "Quick Reel"
        if self.persistence:
            channel_id = self.persistence.valid_channel_id(channel_id)

        job_id = str(uuid.uuid4())
        workspace = self.job_service.workspaces.create(job_id)

        uploads = list(image_files or [])
        if not uploads and image_file is not None:
            uploads = [image_file]
        if not uploads:
            raise AppError("QUICK_REEL_IMAGE_INVALID", "กรุณาเลือกรูปภาพอย่างน้อย 1 รูป")
        if len(uploads) > MAX_QUICK_REEL_IMAGES:
            raise AppError("QUICK_REEL_IMAGE_LIMIT", f"Quick Reel รองรับได้สูงสุด {MAX_QUICK_REEL_IMAGES} รูปต่อคลิป")
        if tts_segments is not None and len(cleaned_segments) != len(uploads):
            raise AppError(
                "QUICK_REEL_TTS_IMAGE_COUNT_MISMATCH",
                f"จำนวนข้อความ tts ({len(cleaned_segments)}) ต้องเท่ากับจำนวนรูป ({len(uploads)})",
            )

        raw_image_paths: list[Path] = []
        original_names: list[str] = []
        for index, upload in enumerate(uploads, 1):
            if isinstance(upload, Path):
                img_ext = upload.suffix.lower()
                original_name = upload.name
            elif hasattr(upload, "file") and getattr(upload, "filename", None):
                img_ext = Path(upload.filename).suffix.lower()
                original_name = Path(upload.filename).name
            else:
                raise AppError("QUICK_REEL_IMAGE_INVALID", f"รูปภาพลำดับที่ {index} ไม่ถูกต้อง")
            if img_ext not in SUPPORTED_IMAGE_EXTS:
                raise AppError("QUICK_REEL_IMAGE_INVALID", "ไฟล์ภาพต้องเป็น PNG, JPG, JPEG หรือ WebP")
            destination = workspace.source / f"image-{index:03d}{img_ext}"
            if isinstance(upload, Path):
                shutil.copy(upload, destination)
            else:
                with destination.open("wb") as out:
                    shutil.copyfileobj(upload.file, out)
            raw_image_paths.append(destination)
            original_names.append(original_name)

        (workspace.source / "script.txt").write_text(cleaned_script, encoding="utf-8")

        saved_bgm: Path | None = None
        if bgm_enabled and bgm_file:
            import re
            from app.services.bgm_service import SOUNDS_DIR
            if isinstance(bgm_file, Path) and bgm_file.is_file():
                bgm_ext = bgm_file.suffix.lower()
                saved_bgm = workspace.source / f"bgm{bgm_ext}"
                shutil.copy(bgm_file, saved_bgm)
                clean_stem = re.sub(r'[^a-zA-Z0-9_\-\u0e00-\u0e7f]', '_', bgm_file.stem).strip('_') or "custom_bgm"
                shared_file = SOUNDS_DIR / f"{clean_stem}{bgm_ext}"
                if not shared_file.is_file():
                    try:
                        shutil.copy(bgm_file, shared_file)
                    except Exception:
                        pass
            elif hasattr(bgm_file, "file") and getattr(bgm_file, "filename", None):
                bgm_ext = Path(bgm_file.filename).suffix.lower()
                if bgm_ext in {".mp3", ".wav", ".m4a", ".aac", ".ogg"}:
                    saved_bgm = workspace.source / f"bgm{bgm_ext}"
                    with saved_bgm.open("wb") as out:
                        shutil.copyfileobj(bgm_file.file, out)
                    clean_stem = re.sub(r'[^a-zA-Z0-9_\-\u0e00-\u0e7f]', '_', Path(bgm_file.filename).stem).strip('_') or "custom_bgm"
                    shared_file = SOUNDS_DIR / f"{clean_stem}{bgm_ext}"
                    if not shared_file.is_file():
                        try:
                            shutil.copy(saved_bgm, shared_file)
                        except Exception:
                            pass

        selected_voice = voice or "Iapetus"
        selected_speed = float(speed if speed is not None else 1.10)
        selected_style = (style_prompt or "").strip() or QUICK_REEL_TTS_STYLE
        motion_map = {
            "none": "none",
            "static": "none",
            "gentle_float": "gentle_float",
            "cosmic_float": "gentle_float",
            "cinematic_push_in": "cinematic_push_in",
            "cinematic_pull_out": "cinematic_pull_out",
            "hook_punch_in": "hook_punch_in",
            "documentary_pan": "documentary_pan",
            "pan_up": "pan_up",
            "drift_diagonal": "drift_diagonal",
            "breathing_pulse": "breathing_pulse",
            "slow_zoom": "slow_zoom_in",
            "slow_zoom_in": "slow_zoom_in",
            "zoom": "slow_zoom_in",
        }
        selected_motion = motion_map.get(motion, "none")
        selected_fit = fit if fit in {"cover", "contain"} else "contain"
        selected_bgm_vol = float(bgm_volume if bgm_volume is not None else 0.10)

        config_data = {
            "title": cleaned_title,
            "script": cleaned_script,
            "ttsSegments": cleaned_segments if tts_segments is not None else None,
            "voice": selected_voice,
            "speed": selected_speed,
            "stylePrompt": selected_style,
            "motion": selected_motion if selected_motion != "none" else "static",
            "fit": selected_fit,
            "hookEnabled": hook_enabled,
            "hookText": hook_text if hook_enabled else "",
            "hookPosition": hook_position,
            "subtitlesEnabled": subtitles_enabled,
            "bgmEnabled": bgm_enabled,
            "bgmTrack": bgm_track,
            "bgmVolume": selected_bgm_vol,
            "description": description or "",
            "hashtags": hashtags or "",
            "imageCount": len(raw_image_paths),
            "imageOrder": original_names,
            "durationMode": "per_tts" if tts_segments is not None else "equal",
            "transition": "crossfade" if len(raw_image_paths) > 1 else "none",
            "transitionSeconds": QUICK_REEL_TRANSITION_SECONDS if len(raw_image_paths) > 1 else 0,
        }
        (workspace.source / "quick-reel-settings.json").write_text(
            json.dumps(config_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        project_id = f"quick-reel-{uuid.uuid4().hex[:8]}"
        record = self.job_service.registry.set(
            JobRecord(
                job_id=job_id,
                project_id=project_id,
                status=JobStatus.RECEIVED,
                progress=0,
                current_step="เตรียมข้อมูล Quick Reel",
                tts_provider="google-gemini",
                subtitle_mode="enable" if subtitles_enabled else "disable",
                render_engine="ffmpeg_motion",
                output_format="vertical",
            )
        )

        if self.persistence:
            self.persistence.ensure_project(project_id, cleaned_title, len(raw_image_paths), "RENDERING", "quick-reel", channel_id)
            self.persistence.upsert_job(record)

        self._log(job_id, "INFO", f"Quick Reel '{cleaned_title}' เริ่มต้นประมวลผล")
        self._progress(job_id, JobStatus.RECEIVED, 2, "เตรียมรูปภาพและบทพูด")

        self.job_service.executor.submit(
            self._process_quick_reel,
            job_id,
            project_id,
            cleaned_title,
            cleaned_script,
            cleaned_segments if tts_segments is not None else None,
            raw_image_paths,
            workspace,
            selected_voice,
            selected_speed,
            selected_style,
            selected_motion,
            selected_fit,
            hook_enabled,
            hook_text,
            hook_position,
            subtitles_enabled,
            bgm_enabled,
            bgm_track,
            saved_bgm,
            selected_bgm_vol,
            description,
            hashtags,
        )

        return record

    def _progress(self, job_id: str, status: JobStatus, progress: int, step: str) -> None:
        self.job_service.registry.update(job_id, status, progress, step)
        if self.persistence:
            current = self.job_service.registry.get(job_id)
            if current:
                self.persistence.upsert_job(current)
        self.job_service.events.publish(
            JobEvent(type=JobEventType.PROGRESS, job_id=job_id, payload={"progress": progress, "status": status, "currentStep": step})
        )

    def _log(self, job_id: str, level: str, message: str) -> None:
        entry = self.job_service.registry.add_log(job_id, level, message)
        self.job_service.events.publish(JobEvent(type=JobEventType.LOG, job_id=job_id, payload=entry))

    def _process_quick_reel(
        self,
        job_id: str,
        project_id: str,
        title: str,
        script_text: str,
        tts_segments: list[str] | None,
        raw_image_paths: list[Path],
        workspace: Any,
        voice: str,
        speed: float,
        style_prompt: str,
        motion: str,
        fit: str,
        hook_enabled: bool,
        hook_text: str,
        hook_position: str,
        subtitles_enabled: bool,
        bgm_enabled: bool,
        bgm_track: str,
        custom_bgm_path: Path | None,
        bgm_volume: float,
        description: str,
        hashtags: str,
    ) -> None:
        started = time.monotonic()
        try:
            image_count = len(raw_image_paths)
            target_width = TARGET_WIDTH
            target_height = TARGET_HEIGHT

            if image_count > 0:
                with Image.open(raw_image_paths[0]) as im:
                    orig_w, orig_h = im.size
                    if orig_w > orig_h:
                        target_width = 1920
                        target_height = 1080

            self._progress(job_id, JobStatus.VALIDATING, 10, f"จัดขนาดภาพ {image_count} รูปเป็น {target_width}x{target_height}")
            self._log(job_id, "INFO", f"จัดขนาดภาพ {image_count} รูปตามลำดับอัปโหลด โหมด {fit}")

            framed_images: list[Path] = []
            for index, raw_image_path in enumerate(raw_image_paths, 1):
                framed_image = workspace.source / f"framed-{index:03d}.png"
                self.prepare_image(raw_image_path, framed_image, fit=fit, target_width=target_width, target_height=target_height)
                if index == 1 and hook_enabled and hook_text.strip():
                    self._log(job_id, "INFO", f"ใส่ Hook Text Overlay บนภาพแรก: {hook_text.strip()[:40]}...")
                    self.apply_hook_overlay(framed_image, hook_text.strip(), position=hook_position)
                framed_images.append(framed_image)

            self._progress(job_id, JobStatus.GENERATING_AUDIO, 30, "กำลังสร้างเสียงบรรยาย Gemini TTS")
            self._log(job_id, "INFO", f"สร้างเสียงภาษาไทยด้วย Gemini Voice: {voice}, Speed: {speed}")

            tts_provider = create_tts_provider("google-gemini", self.settings)
            narration_processor = NarrationAudioProcessor(self.ffmpeg, self.ffprobe, self.settings)
            image_durations: list[float] | None = None
            if tts_segments is not None:
                segment_audio: list[Path] = []
                image_durations = []
                for index, segment_text in enumerate(tts_segments, 1):
                    self._progress(job_id, JobStatus.GENERATING_AUDIO, 30 + int(index / image_count * 15), f"สร้างเสียงภาพที่ {index}/{image_count}")
                    raw_segment = workspace.generated_audio / f"scene-{index:03d}.wav"
                    self._synthesize_narration(tts_provider, segment_text, raw_segment, voice, speed, style_prompt)
                    clean_segment, segment_duration = self._process_narration(narration_processor, raw_segment)
                    segment_audio.append(clean_segment)
                    image_durations.append(segment_duration)
                clean_audio = workspace.generated_audio / "quick-reel-narration.wav"
                self._concat_narration_segments(segment_audio, clean_audio)
                audio_duration = self.ffprobe.duration(clean_audio)
                measured_sum = sum(image_durations)
                if measured_sum > 0 and abs(audio_duration - measured_sum) > 0.001:
                    scale = audio_duration / measured_sum
                    image_durations = [duration * scale for duration in image_durations]
            else:
                raw_audio = workspace.generated_audio / "scene-01.wav"
                self._synthesize_narration(tts_provider, script_text, raw_audio, voice, speed, style_prompt)
                clean_audio, audio_duration = self._process_narration(narration_processor, raw_audio)
            self._log(job_id, "SUCCESS", f"สร้างเสียงบรรยายสำเร็จ ความยาว {audio_duration:.2f} วินาที")

            sub_path: Path | None = None
            if subtitles_enabled:
                self._progress(job_id, JobStatus.RENDERING_SCENES, 50, "สร้างซับไตเติลภาษาไทย")
                self._log(job_id, "INFO", "สร้างไฟล์ซับไตเติล .srt")
                sub_path = workspace.subtitles / "scene-01.srt"
                if tts_segments is not None and image_durations is not None:
                    self._write_segment_subtitles(tts_segments, image_durations, sub_path)
                else:
                    SubtitleRenderer().write(script_text, audio_duration, sub_path, start_seconds=0.0, end_seconds=audio_duration)

            self._progress(job_id, JobStatus.RENDERING_SCENES, 65, f"เรนเดอร์ {image_count} ภาพเป็นวิดีโอ {target_width}x{target_height}")
            motion_labels = {
                "none": "Static Frame",
                "gentle_float": "Cosmic Float / Gentle Drift",
                "cinematic_push_in": "Cinematic Push-in",
                "cinematic_pull_out": "Cinematic Pull-out / Reveal",
                "hook_punch_in": "Hook Punch-in + Slow Drift",
                "documentary_pan": "Documentary Pan",
                "pan_up": "Vertical Pan Up",
                "drift_diagonal": "Diagonal Drift",
                "breathing_pulse": "Breathing Pulse",
                "slow_zoom_in": "Slow Zoom",
            }
            motion_label = motion_labels.get(motion, "Static Frame" if motion == "none" else motion)
            self._log(job_id, "INFO", f"เรนเดอร์ภาพเคลื่อนไหวแบบ {motion_label}")

            render_profile = RenderProfile(target_width, target_height, 30, "libx264", "yuv420p")
            scene_renderer = SceneRenderer(self.ffmpeg, self.settings, render_profile)

            fast_motions = {"cinematic_push_in", "cinematic_pull_out", "hook_punch_in", "documentary_pan", "pan_up", "drift_diagonal"}
            motion_speed = "normal" if motion in fast_motions else "slow"
            motion_intensity = 0.18 if motion in {"cinematic_push_in", "hook_punch_in"} else (0.12 if motion in {"gentle_float", "breathing_pulse"} else 0.15)

            scene_model = Scene(
                id="scene-01",
                image=framed_images[0].name,
                narration=script_text,
                tts_text=script_text,
                subtitle=script_text if subtitles_enabled else "",
                motion=motion,
                motion_speed=motion_speed,
                motion_intensity=motion_intensity,
                focus="center",
                transition="none",
                show_subtitle=subtitles_enabled,
            )

            scene_output = workspace.rendered_scenes / "scene-01.mp4"
            if image_count == 1:
                scene_renderer.render(
                    scene_model, framed_images[0], clean_audio,
                    subtitle=sub_path if subtitles_enabled else None,
                    duration=audio_duration, output=scene_output,
                )
            else:
                self._render_multi_image_slideshow(
                    framed_images, clean_audio, sub_path if subtitles_enabled else None,
                    audio_duration, motion, scene_output, image_durations=image_durations,
                    target_width=target_width, target_height=target_height,
                )
            self._log(job_id, "SUCCESS", f"เรนเดอร์ภาพครบ {image_count} รูปตามลำดับแล้ว")

            self._progress(job_id, JobStatus.COMPOSING, 85, "รวมวิดีโอและระบบเสียง")
            final_output = workspace.output / "final.mp4"

            resolved_bgm: Path | None = None
            if bgm_enabled:
                if custom_bgm_path and custom_bgm_path.is_file():
                    resolved_bgm = custom_bgm_path
                else:
                    resolved_bgm = resolve_podcast_bgm(self.settings.app.workspace, bgm_track)
                self._log(job_id, "INFO", f"มิกซ์เสียง BGM (Volume: {bgm_volume})")

            meta_args = build_ffmpeg_metadata_args(
                title=title,
                description=description or title,
                artist="AutoClip Quick Reel",
            )

            if resolved_bgm and resolved_bgm.is_file():
                audio_filter = (
                    f"[0:a]volume=1.0[n];[1:a]volume={bgm_volume},"
                    "afade=t=in:st=0:d=0.5[bg];[bg][n]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300[duck];"
                    "[n][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:LRA=11:TP=-1.5[a]"
                )
                self.ffmpeg.run(
                    [
                        "-i", str(scene_output),
                        "-stream_loop", "-1", "-i", str(resolved_bgm),
                        "-filter_complex", audio_filter,
                        "-map", "0:v", "-map", "[a]",
                        "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-ac", "2",
                        "-shortest", "-movflags", "+faststart",
                        *meta_args, str(final_output)
                    ],
                    "QUICK_REEL_COMPOSITION_FAILED",
                )
            else:
                self.ffmpeg.run(
                    [
                        "-i", str(scene_output),
                        "-map", "0:v", "-map", "0:a",
                        "-c:v", "copy",
                        "-af", "volume=1.0,loudnorm=I=-16:LRA=11:TP=-1.5",
                        "-c:a", "aac", "-ar", "48000", "-ac", "2",
                        "-movflags", "+faststart",
                        *meta_args, str(final_output)
                    ],
                    "QUICK_REEL_COMPOSITION_FAILED",
                )

            probe = self.ffprobe.probe(final_output)
            v_stream = next(s for s in probe["streams"] if s.get("codec_type") == "video")
            dur = round(float(probe["format"]["duration"]), 3)

            metadata = {
                "projectTitle": title,
                "projectType": "quick-reel",
                "durationSeconds": dur,
                "resolution": f"{v_stream['width']}x{v_stream['height']}",
                "outputFormat": "vertical",
                "sceneCount": image_count,
                "fileSizeBytes": final_output.stat().st_size,
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "videoMetadata": {
                    "title": title,
                    "description": description,
                    "hashtags": hashtags,
                },
                "quickReel": {
                    "motion": motion,
                    "fit": fit,
                    "hookEnabled": hook_enabled,
                    "subtitlesEnabled": subtitles_enabled,
                    "bgmEnabled": bgm_enabled,
                    "imageCount": image_count,
                    "durationMode": "per_tts" if tts_segments is not None else "equal",
                    "transition": "crossfade" if image_count > 1 else "none",
                    "transitionSeconds": QUICK_REEL_TRANSITION_SECONDS if image_count > 1 else 0,
                },
            }

            self.job_service.registry.set_metadata(job_id, metadata)
            if self.persistence:
                current = self.job_service.registry.get(job_id)
                if current:
                    self.persistence.upsert_job(current, final_output, metadata)
                    self.persistence.update_project_status(project_id, "COMPLETED")

            self._progress(job_id, JobStatus.COMPLETED, 100, "วิดีโอพร้อมแล้ว")
            self._log(job_id, "SUCCESS", "สร้าง Quick Reel สำเร็จเรียบร้อย")
            self.job_service.events.publish(
                JobEvent(
                    type=JobEventType.COMPLETED,
                    job_id=job_id,
                    payload={
                        "progress": 100,
                        "status": JobStatus.COMPLETED,
                        "previewUrl": f"/jobs/{job_id}/preview",
                        "videoUrl": f"/api/quick-reel/{job_id}/video",
                    },
                )
            )
            logger.info("Quick Reel completed job_id=%s elapsed=%.2fs", job_id, time.monotonic() - started)

        except AppError as exc:
            current = self.job_service.registry.get(job_id)
            progress = current.progress if current else 0
            safe_error = public_error(exc)
            self.job_service.registry.update(job_id, JobStatus.FAILED, progress, "ประมวลผลล้มเหลว", safe_error)
            if self.persistence:
                cur = self.job_service.registry.get(job_id)
                if cur:
                    self.persistence.upsert_job(cur)
                    self.persistence.update_project_status(project_id, "FAILED")
            self._log(job_id, "ERROR", exc.message)
            self.job_service.events.publish(
                JobEvent(type=JobEventType.FAILED, job_id=job_id, payload={"progress": progress, "status": JobStatus.FAILED, "code": exc.code, "message": exc.message})
            )
            logger.exception("quick_reel job_id=%s failed: %s", job_id, exc.code)
        except Exception as exc:
            error = AppError("INTERNAL_ERROR", f"เกิดข้อผิดพลาดในการประมวลผล Quick Reel: {exc}")
            current = self.job_service.registry.get(job_id)
            progress = current.progress if current else 0
            self.job_service.registry.update(job_id, JobStatus.FAILED, progress, "ประมวลผลล้มเหลว", public_error(error))
            if self.persistence:
                cur = self.job_service.registry.get(job_id)
                if cur:
                    self.persistence.upsert_job(cur)
                    self.persistence.update_project_status(project_id, "FAILED")
            self._log(job_id, "ERROR", error.message)
            self.job_service.events.publish(
                JobEvent(type=JobEventType.FAILED, job_id=job_id, payload={"progress": progress, "status": JobStatus.FAILED, "code": error.code, "message": error.message})
            )
            logger.exception("quick_reel job_id=%s internal error", job_id)

    def get_job(self, job_id: str) -> dict:
        record = self.job_service.restore(job_id)
        if not record:
            raise AppError("JOB_NOT_FOUND", "ไม่พบงาน Quick Reel นี้")
        data = record.api_dict()
        video = self.job_service.final_video(job_id)
        data["videoAvailable"] = video.is_file()
        if video.is_file():
            data["videoUrl"] = f"/api/quick-reel/{job_id}/video"
            data["previewUrl"] = f"/jobs/{job_id}/preview"
        return data

    def video_path(self, job_id: str) -> Path:
        video = self.job_service.final_video(job_id)
        if not video.is_file():
            raise AppError("VIDEO_NOT_READY", "วิดีโอยังไม่พร้อมหรือเกิดข้อผิดพลาด")
        return video

    def delete_job(self, job_id: str) -> dict:
        record = self.job_service.restore(job_id)
        if not record:
            raise AppError("JOB_NOT_FOUND", "ไม่พบงาน Quick Reel นี้")
        if record.project_id and self.persistence:
            self.persistence.delete_project(record.project_id)
        root = self.settings.app.workspace.resolve()
        job_dir = (root / job_id).resolve()
        if root in job_dir.parents and job_dir.is_dir():
            shutil.rmtree(job_dir, ignore_errors=True)
        return {"status": "DELETED", "jobId": job_id}

    def remotion_quick_reel(self, job_id: str, new_motion: str | None = None, fit: str | None = None) -> dict:
        record = self.job_service.restore(job_id)
        if not record:
            raise AppError("JOB_NOT_FOUND", "ไม่พบงาน Quick Reel นี้")
        workspace = self.job_service.workspaces.get(job_id)
        if not workspace.root.is_dir():
            raise AppError("WORKSPACE_NOT_FOUND", "ไม่พบ workspace ของงานนี้")

        settings_file = workspace.source / "quick-reel-settings.json"
        settings_data: dict = {}
        if settings_file.is_file():
            try:
                settings_data = json.loads(settings_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        image_count = settings_data.get("imageCount", 1)
        if image_count > 1:
            raise AppError("REMOTION_NOT_SUPPORTED", "ระบบ Re-Motion รองรับเฉพาะ Quick Reel แบบ 1 รูปภาพในขณะนี้")

        framed_image = workspace.source / "framed-001.png"
        target_width = TARGET_WIDTH
        target_height = TARGET_HEIGHT

        current_fit = settings_data.get("fit", "contain")
        selected_fit = fit.strip().lower() if fit else current_fit
        if selected_fit not in {"cover", "contain"}:
            selected_fit = "contain"

        raw_candidates = sorted(list(workspace.source.glob("image-001.*")))
        if not raw_candidates:
            raw_candidates = sorted(list(workspace.source.glob("*.png")) + list(workspace.source.glob("*.jpg")) + list(workspace.source.glob("*.jpeg")) + list(workspace.source.glob("*.webp")))

        if raw_candidates:
            try:
                with Image.open(raw_candidates[0]) as im:
                    orig_w, orig_h = im.size
                    if orig_w > orig_h:
                        target_width = 1920
                        target_height = 1080
            except Exception:
                pass

        if fit is not None or not framed_image.is_file():
            if not raw_candidates:
                raise AppError("IMAGE_NOT_FOUND", "ไม่พบไฟล์รูปภาพต้นฉบับ")
            self.prepare_image(raw_candidates[0], framed_image, fit=selected_fit, target_width=target_width, target_height=target_height)
            if settings_data.get("hookEnabled"):
                self.apply_hook_overlay(
                    framed_image,
                    settings_data.get("hookText", ""),
                    settings_data.get("hookPosition", "top"),
                    framed_image,
                )
        elif framed_image.is_file():
            try:
                with Image.open(framed_image) as im:
                    target_width, target_height = im.size
            except Exception:
                pass

        settings_data["fit"] = selected_fit

        clean_audio = workspace.generated_audio / "scene-01.wav"
        if not clean_audio.is_file():
            clean_audio = workspace.generated_audio / "quick-reel-narration.wav"
        if not clean_audio.is_file():
            raise AppError("AUDIO_NOT_FOUND", "ไม่พบไฟล์เสียงบรรยายเดิม")

        audio_duration = self.ffprobe.duration(clean_audio)

        motion_map = {
            "none": "none",
            "static": "none",
            "gentle_float": "gentle_float",
            "cosmic_float": "gentle_float",
            "cinematic_push_in": "cinematic_push_in",
            "cinematic_pull_out": "cinematic_pull_out",
            "hook_punch_in": "hook_punch_in",
            "documentary_pan": "documentary_pan",
            "pan_up": "pan_up",
            "drift_diagonal": "drift_diagonal",
            "breathing_pulse": "breathing_pulse",
            "slow_zoom": "slow_zoom_in",
            "slow_zoom_in": "slow_zoom_in",
            "zoom": "slow_zoom_in",
        }
        effective_motion = new_motion if new_motion else settings_data.get("motion", "none")
        selected_motion = motion_map.get(effective_motion, "none")

        sub_path = workspace.subtitles / "scene-01.srt"
        has_subs = sub_path.is_file() and settings_data.get("subtitlesEnabled", True)

        render_profile = RenderProfile(target_width, target_height, 30, "libx264", "yuv420p")
        scene_renderer = SceneRenderer(self.ffmpeg, self.settings, render_profile)

        fast_motions = {"cinematic_push_in", "cinematic_pull_out", "hook_punch_in", "documentary_pan", "pan_up", "drift_diagonal"}
        motion_speed = "normal" if selected_motion in fast_motions else "slow"
        motion_intensity = 0.18 if selected_motion in {"cinematic_push_in", "hook_punch_in"} else (0.12 if selected_motion in {"gentle_float", "breathing_pulse"} else 0.15)

        script_text = settings_data.get("script", "")

        scene_model = Scene(
            id="scene-01",
            image=framed_image.name,
            narration=script_text,
            tts_text=script_text,
            subtitle=script_text if has_subs else "",
            motion=selected_motion,
            motion_speed=motion_speed,
            motion_intensity=motion_intensity,
            focus="center",
            transition="none",
            show_subtitle=has_subs,
        )

        scene_output = workspace.rendered_scenes / "scene-01.mp4"
        scene_renderer.render(
            scene_model, framed_image, clean_audio,
            subtitle=sub_path if has_subs else None,
            duration=audio_duration, output=scene_output,
        )

        final_output = workspace.output / "final.mp4"
        title = settings_data.get("title", "")
        description = settings_data.get("description", "")
        bgm_enabled = settings_data.get("bgmEnabled", False)
        bgm_track = settings_data.get("bgmTrack", "cosmic_drift")
        bgm_volume = float(settings_data.get("bgmVolume", 0.10))

        resolved_bgm: Path | None = None
        if bgm_enabled:
            custom_bgm_candidates = sorted(list(workspace.source.glob("bgm.*")))
            if custom_bgm_candidates and custom_bgm_candidates[0].is_file():
                resolved_bgm = custom_bgm_candidates[0]
            else:
                resolved_bgm = resolve_podcast_bgm(self.settings.app.workspace, bgm_track)

        meta_args = build_ffmpeg_metadata_args(
            title=title,
            description=description or title,
            artist="AutoClip Quick Reel",
        )

        if resolved_bgm and resolved_bgm.is_file():
            audio_filter = (
                f"[0:a]volume=1.0[n];[1:a]volume={bgm_volume},"
                "afade=t=in:st=0:d=0.5[bg];[bg][n]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300[duck];"
                "[n][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:LRA=11:TP=-1.5[a]"
            )
            self.ffmpeg.run(
                [
                    "-y", "-i", str(scene_output),
                    "-stream_loop", "-1", "-i", str(resolved_bgm),
                    "-filter_complex", audio_filter,
                    "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-ac", "2",
                    "-shortest", "-movflags", "+faststart",
                    *meta_args, str(final_output)
                ],
                "QUICK_REEL_COMPOSITION_FAILED",
            )
        else:
            self.ffmpeg.run(
                [
                    "-y", "-i", str(scene_output),
                    "-map", "0:v", "-map", "0:a",
                    "-c", "copy",
                    "-movflags", "+faststart",
                    *meta_args, str(final_output)
                ],
                "QUICK_REEL_COMPOSITION_FAILED",
            )

        probe = self.ffprobe.probe(final_output)
        v_stream = next(s for s in probe["streams"] if s.get("codec_type") == "video")
        dur = round(float(probe["format"]["duration"]), 3)

        settings_data["motion"] = selected_motion
        settings_file.write_text(json.dumps(settings_data, ensure_ascii=False, indent=2), encoding="utf-8")

        cur_meta = dict(record.metadata or {})
        qr_meta = dict(cur_meta.get("quickReel") or {})
        qr_meta["motion"] = selected_motion
        cur_meta["quickReel"] = qr_meta
        cur_meta["durationSeconds"] = dur
        cur_meta["resolution"] = f"{v_stream['width']}x{v_stream['height']}"
        cur_meta["outputFormat"] = "youtube" if v_stream['width'] > v_stream['height'] else "vertical"
        cur_meta["fileSizeBytes"] = final_output.stat().st_size
        record.metadata = cur_meta

        self.job_service.registry.set(record)
        if self.persistence:
            self.persistence.upsert_job(record)

        self._log(job_id, "SUCCESS", f"อัปเดต Motion เป็น {selected_motion} เรียบร้อยแล้ว")

        return {
            "jobId": job_id,
            "motion": selected_motion,
            "videoUrl": f"/api/jobs/{job_id}/video",
            "durationSeconds": dur,
            "message": f"เปลี่ยน Motion เป็น {selected_motion} สำเร็จแล้ว",
        }

    def edit_quick_reel(
        self,
        job_id: str,
        new_script: str | None = None,
        new_motion: str | None = None,
        fit: str | None = None,
        image_bytes: bytes | None = None,
        image_filename: str | None = None,
    ) -> dict:
        record = self.job_service.restore(job_id)
        if not record:
            raise AppError("JOB_NOT_FOUND", "ไม่พบงาน Quick Reel นี้")
        workspace = self.job_service.workspaces.get(job_id)
        if not workspace.root.is_dir():
            raise AppError("WORKSPACE_NOT_FOUND", "ไม่พบ workspace ของงานนี้")

        settings_file = workspace.source / "quick-reel-settings.json"
        settings_data: dict = {}
        if settings_file.is_file():
            try:
                settings_data = json.loads(settings_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        target_width = TARGET_WIDTH
        target_height = TARGET_HEIGHT
        current_fit = settings_data.get("fit", "contain")
        selected_fit = fit.strip().lower() if fit else current_fit
        if selected_fit not in {"cover", "contain"}:
            selected_fit = "contain"

        framed_image = workspace.source / "framed-001.png"

        # 1. Handle Image Replacement
        if image_bytes and len(image_bytes) > 0:
            ext = Path(image_filename or "image.png").suffix.lower() or ".png"
            if ext not in {".png", ".jpg", ".jpeg", ".webp"}:
                ext = ".png"
            for old_img in workspace.source.glob("image-001.*"):
                try:
                    old_img.unlink()
                except Exception:
                    pass
            new_raw_image = workspace.source / f"image-001{ext}"
            new_raw_image.write_bytes(image_bytes)

            try:
                with Image.open(new_raw_image) as im:
                    orig_w, orig_h = im.size
                    if orig_w > orig_h:
                        target_width = 1920
                        target_height = 1080
            except Exception:
                pass

            self.prepare_image(new_raw_image, framed_image, fit=selected_fit, target_width=target_width, target_height=target_height)
            if settings_data.get("hookEnabled"):
                self.apply_hook_overlay(
                    framed_image,
                    settings_data.get("hookText", ""),
                    settings_data.get("hookPosition", "top"),
                    framed_image,
                )
            thumb = workspace.source / "thumbnail.jpg"
            if thumb.is_file():
                thumb.unlink()
        elif framed_image.is_file():
            try:
                with Image.open(framed_image) as im:
                    target_width, target_height = im.size
            except Exception:
                pass

        settings_data["fit"] = selected_fit

        # 2. Handle Script / Narration
        clean_audio = workspace.generated_audio / "scene-01.wav"
        if not clean_audio.is_file():
            clean_audio = workspace.generated_audio / "quick-reel-narration.wav"

        audio_invalidated = False
        if new_script is not None and new_script.strip() and new_script.strip() != settings_data.get("script", "").strip():
            script_text = new_script.strip()
            voice = settings_data.get("voice") or self.settings.quick_reel.default_voice
            speed = float(settings_data.get("speed") or self.settings.quick_reel.default_speed)
            style_prompt = settings_data.get("stylePrompt") or self.settings.quick_reel.default_style_prompt

            tts_provider = create_tts_provider("google-gemini", self.settings)
            narration_processor = NarrationAudioProcessor(self.ffmpeg, self.ffprobe, self.settings)

            raw_audio = workspace.generated_audio / "scene-01.wav"
            self._synthesize_narration(tts_provider, script_text, raw_audio, voice, speed, style_prompt)
            clean_audio, audio_duration = self._process_narration(narration_processor, raw_audio)
            settings_data["script"] = script_text
            audio_invalidated = True
        else:
            if not clean_audio.is_file():
                raise AppError("AUDIO_NOT_FOUND", "ไม่พบไฟล์เสียงบรรยายเดิม")
            audio_duration = self.ffprobe.duration(clean_audio)
            script_text = settings_data.get("script", "")

        # 3. Subtitles
        sub_path = workspace.subtitles / "scene-01.srt"
        has_subs = settings_data.get("subtitlesEnabled", True)
        if has_subs:
            SubtitleRenderer().write(script_text, audio_duration, sub_path, start_seconds=0.0, end_seconds=audio_duration)

        # 4. Motion
        motion_map = {
            "none": "none",
            "static": "none",
            "gentle_float": "gentle_float",
            "cosmic_float": "gentle_float",
            "cinematic_push_in": "cinematic_push_in",
            "cinematic_pull_out": "cinematic_pull_out",
            "hook_punch_in": "hook_punch_in",
            "documentary_pan": "documentary_pan",
            "pan_up": "pan_up",
            "drift_diagonal": "drift_diagonal",
            "breathing_pulse": "breathing_pulse",
            "slow_zoom": "slow_zoom_in",
            "slow_zoom_in": "slow_zoom_in",
            "zoom": "slow_zoom_in",
        }
        effective_motion = new_motion if new_motion else settings_data.get("motion", "none")
        selected_motion = motion_map.get(effective_motion, "none")
        settings_data["motion"] = selected_motion

        # 5. Render Scene
        render_profile = RenderProfile(target_width, target_height, 30, "libx264", "yuv420p")
        scene_renderer = SceneRenderer(self.ffmpeg, self.settings, render_profile)

        fast_motions = {"cinematic_push_in", "cinematic_pull_out", "hook_punch_in", "documentary_pan", "pan_up", "drift_diagonal"}
        motion_speed = "normal" if selected_motion in fast_motions else "slow"
        motion_intensity = 0.18 if selected_motion in {"cinematic_push_in", "hook_punch_in"} else (0.12 if selected_motion in {"gentle_float", "breathing_pulse"} else 0.15)

        scene_model = Scene(
            id="scene-01",
            image=framed_image.name,
            narration=script_text,
            tts_text=script_text,
            subtitle=script_text if has_subs else "",
            motion=selected_motion,
            motion_speed=motion_speed,
            motion_intensity=motion_intensity,
            focus="center",
            transition="none",
            show_subtitle=has_subs,
        )

        scene_output = workspace.rendered_scenes / "scene-01.mp4"
        scene_renderer.render(
            scene_model, framed_image, clean_audio,
            subtitle=sub_path if has_subs else None,
            duration=audio_duration, output=scene_output,
        )

        # 6. Compose Final Video
        final_output = workspace.output / "final.mp4"
        title = settings_data.get("title", "")
        description = settings_data.get("description", "")
        bgm_enabled = settings_data.get("bgmEnabled", False)
        bgm_track = settings_data.get("bgmTrack", "cosmic_drift")
        bgm_volume = float(settings_data.get("bgmVolume", 0.10))

        resolved_bgm: Path | None = None
        if bgm_enabled:
            custom_bgm_candidates = sorted(list(workspace.source.glob("bgm.*")))
            if custom_bgm_candidates and custom_bgm_candidates[0].is_file():
                resolved_bgm = custom_bgm_candidates[0]
            else:
                resolved_bgm = resolve_podcast_bgm(self.settings.app.workspace, bgm_track)

        meta_args = build_ffmpeg_metadata_args(
            title=title,
            description=description or title,
            artist="AutoClip Quick Reel",
        )

        if resolved_bgm and resolved_bgm.is_file():
            audio_filter = (
                f"[0:a]volume=1.0[n];[1:a]volume={bgm_volume},"
                "afade=t=in:st=0:d=0.5[bg];[bg][n]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300[duck];"
                "[n][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:LRA=11:TP=-1.5[a]"
            )
            self.ffmpeg.run(
                [
                    "-y", "-i", str(scene_output),
                    "-stream_loop", "-1", "-i", str(resolved_bgm),
                    "-filter_complex", audio_filter,
                    "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-ac", "2",
                    "-shortest", "-movflags", "+faststart",
                    *meta_args, str(final_output)
                ],
                "QUICK_REEL_COMPOSITION_FAILED",
            )
        else:
            self.ffmpeg.run(
                [
                    "-y", "-i", str(scene_output),
                    "-map", "0:v", "-map", "0:a",
                    "-c", "copy",
                    "-movflags", "+faststart",
                    *meta_args, str(final_output)
                ],
                "QUICK_REEL_COMPOSITION_FAILED",
            )

        probe = self.ffprobe.probe(final_output)
        v_stream = next(s for s in probe["streams"] if s.get("codec_type") == "video")
        dur = round(float(probe["format"]["duration"]), 3)

        settings_file.write_text(json.dumps(settings_data, ensure_ascii=False, indent=2), encoding="utf-8")

        cur_meta = dict(record.metadata or {})
        qr_meta = dict(cur_meta.get("quickReel") or {})
        qr_meta["motion"] = selected_motion
        cur_meta["quickReel"] = qr_meta
        cur_meta["durationSeconds"] = dur
        cur_meta["resolution"] = f"{v_stream['width']}x{v_stream['height']}"
        cur_meta["outputFormat"] = "youtube" if v_stream['width'] > v_stream['height'] else "vertical"
        cur_meta["fileSizeBytes"] = final_output.stat().st_size
        record.metadata = cur_meta

        self.job_service.registry.set(record)
        if self.persistence:
            self.persistence.upsert_job(record)

        self._log(job_id, "SUCCESS", "อัปเดต Quick Reel เรียบร้อยแล้ว")

        return {
            "status": "QUICK_REEL_UPDATED",
            "jobId": job_id,
            "sceneId": "scene-01",
            "audioInvalidated": audio_invalidated,
            "videoInvalidated": True,
            "videoUrl": f"/api/jobs/{job_id}/video",
            "durationSeconds": dur,
            "message": "แก้ไข Quick Reel สำเร็จแล้ว",
        }


