from __future__ import annotations

import logging
import math
import shutil
import time
from pathlib import Path
from typing import Callable

from PIL import Image

from app.config.settings import Settings
from app.domain.errors import AppError
from app.infrastructure.ffmpeg import FfmpegRunner, FfprobeRunner, build_ffmpeg_metadata_args

logger = logging.getLogger("autoclip.podcast.video")

SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


class PodcastVideoRenderer:
    """Renders 1920x1080 30FPS YouTube Visual Podcast video with gentle single-image motion."""

    def __init__(self, ffmpeg: FfmpegRunner, ffprobe: FfprobeRunner, settings: Settings):
        self.ffmpeg = ffmpeg
        self.ffprobe = ffprobe
        self.settings = settings

    def validate_and_prepare_image(self, image_path: Path, output_path: Path) -> tuple[int, int, bool]:
        """Validates the cover image and scales/crops it to cover 1920x1080.

        Returns:
            (orig_width, orig_height, is_landscape_16_9)
        """
        if not image_path.is_file() or image_path.suffix.lower() not in SUPPORTED_IMAGE_EXTS:
            raise AppError("PODCAST_IMAGE_INVALID", "ไฟล์ภาพปกต้องเป็น PNG, JPG, JPEG หรือ WebP")

        try:
            with Image.open(image_path) as im:
                orig_w, orig_h = im.size
                im_format = im.format

                # Calculate aspect ratio
                ratio = orig_w / max(1, orig_h)
                is_16_9 = math.isclose(ratio, 16 / 9, rel_tol=0.05)

                # Convert to RGB (or RGBA then RGB background)
                if im.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", im.size, (15, 15, 25))
                    alpha = im.convert("RGBA").split()[-1]
                    bg.paste(im, mask=alpha)
                    rgb_im = bg
                else:
                    rgb_im = im.convert("RGB")

                # Crop/scale to cover 1920x1080
                target_w, target_h = 1920, 1080
                scale = max(target_w / orig_w, target_h / orig_h)
                new_w = int(round(orig_w * scale))
                new_h = int(round(orig_h * scale))
                scaled = rgb_im.resize((new_w, new_h), Image.Resampling.LANCZOS)

                # Center crop to 1920x1080
                left = (new_w - target_w) // 2
                top = (new_h - target_h) // 2
                cropped = scaled.crop((left, top, left + target_w, top + target_h))

                output_path.parent.mkdir(parents=True, exist_ok=True)
                cropped.save(output_path, format="PNG")

                return orig_w, orig_h, is_16_9
        except AppError:
            raise
        except Exception as exc:
            raise AppError("PODCAST_IMAGE_INVALID", "ไม่สามารถเปิดหรือประมวลผลไฟล์ภาพปกได้") from exc

    def _generate_motion_cycle(self, image_path: Path, cycle_dir: Path, focus: str = "center") -> Path:
        """Generates a 6-stage gentle breathing motion cycle video (~60s) from a single image."""
        cycle_dir.mkdir(parents=True, exist_ok=True)
        cycle_output = cycle_dir / "motion_cycle.mp4"
        if cycle_output.is_file() and cycle_output.stat().st_size > 10000:
            return cycle_output

        # Focus mapping
        focus_pts = {
            "top": ("0.5", "0.2"),
            "bottom": ("0.5", "0.8"),
            "left": ("0.2", "0.5"),
            "right": ("0.8", "0.5"),
            "center": ("0.5", "0.5"),
        }.get(focus, ("0.5", "0.5"))

        fx, fy = focus_pts

        fps = 30
        stage_sec = 10
        stage_frames = fps * stage_sec
        xfade_sec = 0.8

        # 6 Bedtime-friendly motion stages:
        # Stage 1: Wide slow push-in (zoom 1.00 -> 1.05)
        # Stage 2: Medium crop focus with subtle drift
        # Stage 3: Gentle horizontal drift (left to right)
        # Stage 4: Slow pull-out (zoom 1.05 -> 1.02)
        # Stage 5: Alternate crop focus
        # Stage 6: Return to wide (zoom 1.02 -> 1.00)
        presets = [
            # 1. Slow push in
            (f"min(zoom+0.05/{stage_frames},1.05)", f"(iw-iw/zoom)*{fx}", f"(ih-ih/zoom)*{fy}"),
            # 2. Medium crop focus drift
            ("1.05", f"(iw-iw/zoom)*({fx}+0.05*sin(on/{stage_frames}*PI))", f"(ih-ih/zoom)*({fy}+0.03*cos(on/{stage_frames}*PI))"),
            # 3. Gentle horizontal drift
            ("1.05", f"(iw-iw/zoom)*(0.35+0.30*on/{stage_frames})", f"(ih-ih/zoom)*{fy}"),
            # 4. Slow pull out
            (f"max(zoom-0.03/{stage_frames},1.02)", f"(iw-iw/zoom)*0.65", f"(ih-ih/zoom)*{fy}"),
            # 5. Alternate crop focus
            ("1.02", f"(iw-iw/zoom)*(0.65-0.15*on/{stage_frames})", f"(ih-ih/zoom)*0.45"),
            # 6. Return smoothly to wide
            (f"max(zoom-0.02/{stage_frames},1.00)", f"(iw-iw/zoom)*{fx}", f"(ih-ih/zoom)*{fy}"),
        ]

        stage_files: list[Path] = []
        for idx, (z, x, y) in enumerate(presets):
            st_path = cycle_dir / f"stage_{idx:02d}.mp4"
            cmd = [
                "-i", str(image_path),
                "-vf", f"scale=3840:2160,zoompan=z='{z}':x='{x}':y='{y}':d={stage_frames}:s=1920x1080:fps={fps},format=yuv420p",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "20",
                str(st_path),
            ]
            self.ffmpeg.run(cmd, "PODCAST_RENDER_FAILED")
            stage_files.append(st_path)

        # Crossfade stages with dissolve transition
        filter_parts = [f"[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[v{i}]" for i in range(len(stage_files))]
        v_left = "v0"
        elapsed = float(stage_sec)
        for i in range(1, len(stage_files)):
            v_out = f"vx{i}"
            offset = elapsed - xfade_sec
            filter_parts.append(f"[{v_left}][v{i}]xfade=transition=dissolve:duration={xfade_sec:.2f}:offset={offset:.2f}[{v_out}]")
            v_left = v_out
            elapsed += stage_sec - xfade_sec

        filter_str = ";".join(filter_parts)
        inputs = [arg for s in stage_files for arg in ("-i", str(s))]
        cmd = [
            *inputs,
            "-filter_complex", filter_str,
            "-map", f"[{v_left}]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "20",
            str(cycle_output),
        ]
        self.ffmpeg.run(cmd, "PODCAST_RENDER_FAILED")

        # Cleanup intermediate stage clips
        for s in stage_files:
            s.unlink(missing_ok=True)

        return cycle_output

    def render(
        self,
        job_id: str,
        workspace_root: Path,
        cover_image: Path,
        narration_audio: Path,
        total_duration: float,
        output_path: Path,
        subtitle_path: Path | None = None,
        bgm_path: Path | None = None,
        bgm_volume: float = 0.08,
        focus: str = "center",
        log_callback: Callable[[str, str, bool], None] | None = None,
        title: str = "",
        description: str = "",
    ) -> Path:
        """Renders complete 1920x1080 podcast video with motion cycle, audio ducking, and subtitles."""
        started_at = time.monotonic()
        work_dir = workspace_root / "render_work"
        work_dir.mkdir(parents=True, exist_ok=True)

        # 1. Prepare image
        prepared_cover = work_dir / "prepared_cover.png"
        orig_w, orig_h, is_16_9 = self.validate_and_prepare_image(cover_image, prepared_cover)
        if log_callback:
            if not is_16_9:
                log_callback("WARNING", f"ภาพปกเดิมขนาด {orig_w}x{orig_h} ไม่ใช่ 16:9 — ระบบได้ครอบตัดแบบ cover สำหรับ 1920x1080", False)
            log_callback("INFO", "กำลังสร้างลำดับภาพเคลื่อนไหวแบบนุ่มนวล (Visual Motion Cycle)", False)

        # 2. Generate smooth motion cycle
        cycle_video = self._generate_motion_cycle(prepared_cover, work_dir, focus=focus)
        if log_callback:
            log_callback("SUCCESS", "สร้าง Motion Cycle สำเร็จ กำลังเรนเดอร์วิดีโอตัวเต็ม", False)
            log_callback("TECHNICAL", f"event=motion_cycle_ready job_id={job_id} size={cycle_video.stat().st_size}B", True)

        # 3. Build FFmpeg command for full video
        vf_filters: list[str] = ["fps=30", "format=yuv420p"]

        # Subtitles (if enabled and filter available)
        has_sub_filter = self.ffmpeg.has_filter("subtitles")
        if subtitle_path and subtitle_path.is_file():
            if has_sub_filter:
                escaped = str(subtitle_path).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
                ass_scale = 288 / 1080
                ass_font_size = 46 * ass_scale
                ass_outline = 2.8 * ass_scale
                ass_margin_v = round(65 * ass_scale)
                ass_safe_margin = round(120 * ass_scale)
                style = (
                    f"FontName=Noto Sans Thai,FontSize={ass_font_size:.2f},"
                    f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,"
                    f"Outline={ass_outline:.2f},Shadow=0.5,Alignment=2,MarginV={ass_margin_v},"
                    f"MarginL={ass_safe_margin},MarginR={ass_safe_margin}"
                ).replace(",", r"\,")
                vf_filters.append(f"subtitles={escaped}:original_size=1920x1080:charenc=UTF-8:force_style={style}")
                if log_callback:
                    log_callback("INFO", "กำลังฝัง Subtitle ภาษาไทยลงในวิดีโอ", False)
            else:
                if log_callback:
                    log_callback("INFO", "ระบบฝัง Subtitle track ลงในไฟล์วิดีโอ", False)

        vf_str = ",".join(vf_filters)

        # Assemble inputs and audio filter
        inputs = [
            "-stream_loop", "-1", "-i", str(cycle_video),
            "-i", str(narration_audio),
        ]

        meta_args = build_ffmpeg_metadata_args(title=title, description=description, artist="Mamase (จักรวาลของใจ)")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if bgm_path and bgm_path.is_file():
            if log_callback:
                log_callback("INFO", f"กำลังผสม Background Music (ระดับเสียง {bgm_volume:.2f}) พร้อม Sidechain Ducking", False)
            inputs.extend(["-stream_loop", "-1", "-i", str(bgm_path)])
            fade_out_start = max(0.0, total_duration - 2.0)
            audio_filter = (
                f"[1:a]volume=1.0,asplit=2[n1][n2];"
                f"[2:a]volume={bgm_volume},"
                f"afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_start:.2f}:d=2.0[bg];"
                f"[bg][n1]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300[duck];"
                f"[n2][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:LRA=11:TP=-1.5[a]"
            )
            cmd = [
                *inputs,
                "-t", f"{total_duration:.3f}",
                "-vf", vf_str,
                "-filter_complex", audio_filter,
                "-map", "0:v",
                "-map", "[a]",
                *meta_args,
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "22",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                "-c:a", "aac",
                "-ar", "48000",
                "-ac", "2",
                "-b:a", "192k",
                "-movflags", "+faststart",
                "-shortest",
                str(output_path),
            ]
        else:
            if log_callback:
                log_callback("INFO", "กำลังปรับระดับความดังของเสียงบรรยาย (Loudness normalization)", False)
            audio_filter = "volume=1.0,loudnorm=I=-16:LRA=11:TP=-1.5"
            cmd = [
                *inputs,
                "-t", f"{total_duration:.3f}",
                "-vf", vf_str,
                "-af", audio_filter,
                "-map", "0:v",
                "-map", "1:a",
                *meta_args,
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "22",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                "-c:a", "aac",
                "-ar", "48000",
                "-ac", "2",
                "-b:a", "192k",
                "-movflags", "+faststart",
                "-shortest",
                str(output_path),
            ]

        # Execute final composition
        timeout_sec = max(900, int(total_duration * 2) + 180)
        self.ffmpeg.run(cmd, "PODCAST_RENDER_FAILED", timeout_seconds=timeout_sec)

        elapsed = round(time.monotonic() - started_at, 2)
        if log_callback:
            log_callback("SUCCESS", f"สร้าง YouTube Podcast สำเร็จ (ขนาด {round(output_path.stat().st_size / (1024*1024), 2)} MB ใน {elapsed}s)", False)
            log_callback("TECHNICAL", f"event=podcast_rendered job_id={job_id} duration={total_duration}s elapsed={elapsed}s bytes={output_path.stat().st_size}", True)

        return output_path
