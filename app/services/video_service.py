from __future__ import annotations

import html
import re
from dataclasses import dataclass
from math import ceil
from pathlib import Path

from app.config.settings import Settings
from app.domain.errors import AppError
from app.domain.models import Scene
from app.infrastructure.ffmpeg import FfmpegRunner, build_ffmpeg_metadata_args


@dataclass(frozen=True)
class RenderProfile:
    """Per-job output settings resolved from the validated project script."""

    width: int
    height: int
    fps: int
    codec: str
    pixel_format: str

    @classmethod
    def from_project(cls, settings: Settings, resolution: str, fps: int | None = None) -> "RenderProfile":
        width, height = (int(part) for part in resolution.split("x", 1))
        return cls(width, height, fps or settings.video.fps, settings.video.codec, settings.video.pixel_format)

    @classmethod
    def from_settings(cls, settings: Settings) -> "RenderProfile":
        return cls(settings.video.width, settings.video.height, settings.video.fps, settings.video.codec, settings.video.pixel_format)


def srt_timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


class SubtitleRenderer:
    KEYWORD_COLOR = "#55D7FF"

    @classmethod
    def emphasize_keywords(cls, text: str, keywords: list[str] | None = None) -> str:
        rendered = html.escape(text, quote=False)
        for keyword in (keywords or [])[:3]:
            escaped_keyword = html.escape(keyword.strip(), quote=False)
            if not escaped_keyword:
                continue
            rendered = re.sub(
                re.escape(escaped_keyword),
                lambda match: f'<font color="{cls.KEYWORD_COLOR}"><b>{match.group(0)}</b></font>',
                rendered,
                flags=re.IGNORECASE,
            )
        return rendered

    def write(self, text: str, duration: float, output: Path, start_seconds: float = 0, end_seconds: float | None = None, keywords: list[str] | None = None) -> Path:
        end = duration if end_seconds is None else min(duration, end_seconds)
        start = max(0, min(start_seconds, end))
        caption = self.emphasize_keywords(text, keywords)
        output.write_text(f"1\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{caption}\n", encoding="utf-8")
        return output


class SceneRenderer:
    MOTION_DEFAULT_INTENSITY = {
        "slow_zoom_in": 0.10, "slow_zoom_out": 0.10,
        "zoom_in": 0.18, "zoom_out": 0.16,
        "cinematic_push_in": 0.18, "cinematic_pull_out": 0.16,
        "gentle_float": 0.12, "documentary_pan": 0.15,
        "hook_punch_in": 0.18,
        "drift_diagonal": 0.15,
        "breathing_pulse": 0.12,
        "pan_up": 0.15,
    }
    SPEED_FACTOR = {"slow": 0.9, "normal": 1.2, "fast": 1.5}
    def __init__(self, ffmpeg: FfmpegRunner, settings: Settings, profile: RenderProfile | None = None):
        self.ffmpeg = ffmpeg
        self.settings = settings
        self.profile = profile or RenderProfile.from_settings(settings)

    def build_filter(self, scene: Scene, duration: float, subtitle: Path | None = None) -> str:
        video = self.profile
        frames = max(1, round(duration * video.fps))
        w, h, fps = video.width, video.height, video.fps
        crop_focus = {
            "top": ("(iw-ow)/2", "0"), "bottom": ("(iw-ow)/2", "ih-oh"),
            "left": ("0", "(ih-oh)/2"), "right": ("iw-ow", "(ih-oh)/2"),
            "top_left": ("0", "0"), "top_right": ("iw-ow", "0"),
            "bottom_left": ("0", "ih-oh"), "bottom_right": ("iw-ow", "ih-oh"),
            "center": ("(iw-ow)/2", "(ih-oh)/2"),
        }[scene.focus]
        base = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}:{crop_focus[0]}:{crop_focus[1]},setsar=1"
        # Keep a larger working canvas for camera motion; an output-sized
        # frame leaves zoompan with almost no room to pan or zoom visibly.
        # Do not crop this working canvas: zoompan needs the overscan area to
        # move even when zoom is exactly 1.0 (pure pan presets).
        motion_base = f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,setsar=1"
        auto_motion = {
            "left": "pan_left_to_right_zoom_in", "top_left": "pan_left_to_right_zoom_in", "bottom_left": "pan_left_to_right_zoom_in",
            "right": "pan_right_to_left_zoom_in", "top_right": "pan_right_to_left_zoom_in", "bottom_right": "pan_right_to_left_zoom_in",
            "top": "pan_down_zoom_in", "bottom": "pan_up_zoom_in", "center": "cinematic_push_in",
        }
        motion = auto_motion[scene.focus] if scene.motion == "auto" else scene.motion
        if motion == "none":
            animated = base
        else:
            intensity = min(0.35, max(0.05, scene.motion_intensity or self.MOTION_DEFAULT_INTENSITY.get(motion, 0.10)))
            rate = self.SPEED_FACTOR[scene.motion_speed]
            # Map the user-facing intensity to a visible total scale change.
            # The old formula treated 0.10 as only a 9% change and pure pans
            # had no intensity-dependent travel at all. These ranges are
            # deliberately camera-like while remaining smooth over a scene.
            if motion in {"zoom_in", "zoom_out"}:
                delta = min(0.35, (0.20 + intensity * 0.43) * rate)
            elif motion in {"cinematic_push_in", "cinematic_pull_out"}:
                delta = min(0.35, (0.16 + intensity * 0.34) * rate)
            else:
                delta = min(0.35, (0.12 + intensity * 0.45) * rate)
            pan_travel = min(0.65, max(0.14, (0.10 + intensity * 0.9) * rate))
            zoom_in = motion not in {"slow_zoom_out", "zoom_out", "cinematic_pull_out"}
            if motion in {"slow_zoom_in", "zoom_in", "cinematic_push_in", "pan_left_to_right_zoom_in", "pan_right_to_left_zoom_in", "pan_up_zoom_in", "pan_down_zoom_in"}:
                zoom_in = True
            zoom = f"min(zoom+{delta / frames:.7f},{1.0 + delta:.5f})" if zoom_in else f"if(eq(on,1),{1.0 + delta:.5f},max(zoom-{delta / frames:.7f},1.0))"
            focus = {
                "top": ("0.5", "0.0"), "bottom": ("0.5", "1.0"), "left": ("0.0", "0.5"), "right": ("1.0", "0.5"),
                "top_left": ("0.0", "0.0"), "top_right": ("1.0", "0.0"), "bottom_left": ("0.0", "1.0"), "bottom_right": ("1.0", "1.0"), "center": ("0.5", "0.5"),
            }[scene.focus]
            pan_x = "(iw-iw/zoom)*on/{0}".format(max(1, frames - 1))
            pan_y = "(ih-ih/zoom)*on/{0}".format(max(1, frames - 1))
            if motion in {"pan_right_to_left", "pan_right_to_left_zoom_in", "drift_top_right", "drift_bottom_right"}: pan_x = f"(iw-iw/zoom)*{pan_travel:.4f}*(1-on/{max(1, frames-1)})"
            elif motion in {"pan_left_to_right", "pan_left_to_right_zoom_in", "drift_top_left", "drift_bottom_left", "documentary_pan"}: pan_x = f"(iw-iw/zoom)*{pan_travel:.4f}*on/{max(1, frames-1)}"
            else: pan_x = f"(iw-iw/zoom)*{focus[0]}"
            if motion in {"pan_up", "pan_up_zoom_in", "drift_top_left", "drift_top_right"}: pan_y = f"(ih-ih/zoom)*{pan_travel:.4f}*(1-on/{max(1, frames-1)})"
            elif motion in {"pan_down", "pan_down_zoom_in", "drift_bottom_left", "drift_bottom_right"}: pan_y = f"(ih-ih/zoom)*{pan_travel:.4f}*on/{max(1, frames-1)}"
            else: pan_y = f"(ih-ih/zoom)*{focus[1]}"
            if motion == "gentle_float":
                base_zoom = 1.06
                # Time-based zero-gravity orbital float (7.5s period for X, 11.5s for Y)
                # plus continuous steady forward push, clearly visible regardless of video duration
                zoom = f"min({base_zoom:.3f}+0.005*(on/{fps}),1.25)"
                pan_x = f"(iw-iw/zoom)*(0.5+0.18*sin((on-1)/{fps}*2*PI/7.5))"
                pan_y = f"(ih-ih/zoom)*(0.5+0.16*sin((on-1)/{fps}*2*PI/11.5))"
            elif motion == "hook_punch_in":
                hook_duration = min(duration, 3.0)
                hook_frames = max(1, round(hook_duration * fps))
                # 3-second rapid punch-in (+12%) followed by steady forward drift and cosmic float
                zoom = (
                    f"if(lte(on,{hook_frames}),"
                    f"1.0+0.12*(on/{hook_frames}),"
                    f"min(1.12+0.004*((on-{hook_frames})/{fps}),1.28))"
                )
                pan_x = f"(iw-iw/zoom)*(0.5+if(lte(on,{hook_frames}),0,0.18*sin((on-{hook_frames})/{fps}*2*PI/7.5)))"
                pan_y = f"(ih-ih/zoom)*(0.5+if(lte(on,{hook_frames}),0,0.16*sin((on-{hook_frames})/{fps}*2*PI/11.5)))"
            elif motion == "cinematic_pull_out":
                # Start close (1.25) and smoothly pull back to reveal wider context
                zoom = f"max(1.05,1.25-0.005*(on/{fps}))"
                pan_x = f"(iw-iw/zoom)*0.5"
                pan_y = f"(ih-ih/zoom)*0.5"
            elif motion == "documentary_pan":
                # Smooth slow horizontal sweep across the scenery with subtle zoom
                zoom = f"min(1.08+0.003*(on/{fps}),1.20)"
                pan_x = f"(iw-iw/zoom)*(0.15+0.70*(on/{max(1, frames-1)}))"
                pan_y = f"(ih-ih/zoom)*0.5"
            elif motion == "pan_up":
                # Vertical upward sweep from bottom to top
                zoom = f"min(1.08+0.003*(on/{fps}),1.20)"
                pan_x = f"(iw-iw/zoom)*0.5"
                pan_y = f"(ih-ih/zoom)*(0.85-0.70*(on/{max(1, frames-1)}))"
            elif motion == "drift_diagonal":
                # Diagonal drift from bottom-left towards top-right with depth
                zoom = f"min(1.06+0.004*(on/{fps}),1.22)"
                pan_x = f"(iw-iw/zoom)*(0.20+0.60*(on/{max(1, frames-1)}))"
                pan_y = f"(ih-ih/zoom)*(0.80-0.60*(on/{max(1, frames-1)}))"
            elif motion == "breathing_pulse":
                # Gentle rhythmic in-out breathing zoom with subtle float
                zoom = f"1.08+0.06*0.5*(1-cos((on-1)/{fps}*2*PI/6.0))"
                pan_x = f"(iw-iw/zoom)*(0.5+0.08*sin((on-1)/{fps}*2*PI/12.0))"
                pan_y = f"(ih-ih/zoom)*(0.5+0.08*cos((on-1)/{fps}*2*PI/12.0))"
            # Use the oversized canvas for all animated presets; the existing
            # zoompan expression below then crops it back to the output size.
            base = motion_base
            x, y = pan_x, pan_y
            animated = f"{base},zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s={w}x{h}:fps={fps}"
            # Expand the single source image for the complete scene. Using
            # d=1 with a looping input resets zoompan's frame counter and
            # freezes the camera after the first frame.
            animated = animated.replace(":d=1:", f":d={frames}:")
            animated += f",scale={w}:{h}"
        if self.settings.subtitle.enabled and subtitle and subtitle.is_file() and getattr(scene, "show_subtitle", True) and self.ffmpeg.has_filter("subtitles"):
            escaped = str(subtitle).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
            # Plain SRT has no PlayRes metadata; libass uses a 288-unit vertical
            # script space. Convert pixel-facing configuration to those units.
            ass_scale = 288 / h
            scale_from_default = h / self.settings.video.height
            ass_font_size = max(1, self.settings.subtitle.font_size * scale_from_default * ass_scale)
            ass_outline = max(0, self.settings.subtitle.outline * ass_scale)
            ass_margin_v = round(self.settings.subtitle.margin_bottom * scale_from_default * ass_scale)
            ass_safe_margin = round(70 * ass_scale)
            style = (f"FontName=Noto Sans Thai,FontSize={ass_font_size:.2f},"
                     f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,"
                     f"Outline={ass_outline:.2f},Shadow=0.5,Alignment=2,MarginV={ass_margin_v},"
                     f"MarginL={ass_safe_margin},MarginR={ass_safe_margin}")
            filter_style = style.replace(",", r"\,")
            # The filter is passed as an argv element (not through a shell), so
            # shell-style single quotes would become literal characters and
            # make FFmpeg treat the option suffix as part of the subtitle
            # filename on some builds. Keep the path/style unquoted and escape
            # only filter-significant characters.
            animated += f",subtitles={escaped}:original_size={w}x{h}:charenc=UTF-8:force_style={filter_style}"
        return animated + f",fps={fps},format={video.pixel_format}"

    def render(self, scene: Scene, image: Path, narration: Path, subtitle: Path | None, duration: float, output: Path) -> Path:
        video = self.profile
        image_input = ["-loop", "1"] if scene.motion == "none" else []
        args = [
            *image_input, "-i", str(image), "-i", str(narration), "-t", f"{duration:.3f}",
            "-vf", self.build_filter(scene, duration, subtitle),
            "-c:v", video.codec, "-preset", "veryfast", "-crf", "23", "-pix_fmt", video.pixel_format,
            "-r", str(video.fps), "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "160k",
            "-af", "apad", "-movflags", "+faststart", "-shortest", str(output),
        ]
        self.ffmpeg.run(args, "SCENE_RENDER_FAILED")
        return output

    def render_outro(self, image: Path, duration: float, output: Path) -> Path:
        """Render a silent branding post-roll with no narration or subtitles."""
        video = self.profile
        vf = (
            f"scale={video.width}:{video.height}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={video.width}:{video.height},setsar=1,fps={video.fps},format={video.pixel_format}"
        )
        self.ffmpeg.run(
            ["-loop", "1", "-i", str(image), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
             "-t", f"{duration:.3f}", "-map", "0:v:0", "-map", "1:a:0", "-vf", vf,
             "-c:v", video.codec, "-preset", "veryfast", "-crf", "23", "-pix_fmt", video.pixel_format,
             "-r", str(video.fps), "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "160k",
             "-movflags", "+faststart", "-shortest", str(output)],
            "REEL_OUTRO_RENDER_FAILED",
        )
        return output

    def render_wan_video(self, scene: Scene, source_video: Path, narration: Path, subtitle: Path | None, duration: float, output: Path) -> Path:
        """Normalize an AI clip and attach AutoClip narration/subtitles.

        Wan's render is visual-only.  Keeping narration, subtitles and final
        timing here means the existing composer can treat FFmpeg and Wan
        scenes identically, including transitions and BGM ducking.
        """
        video = self.profile
        subtitle_filter = ""
        if self.settings.subtitle.enabled and subtitle and subtitle.is_file() and getattr(scene, "show_subtitle", True) and self.ffmpeg.has_filter("subtitles"):
            escaped = str(subtitle).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
            ass_scale = 288 / video.height
            scale_from_default = video.height / self.settings.video.height
            style = (
                f"FontName=Noto Sans Thai,FontSize={max(1, self.settings.subtitle.font_size * scale_from_default * ass_scale):.2f},"
                f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,"
                f"Outline={max(0, self.settings.subtitle.outline * ass_scale):.2f},Shadow=0.5,Alignment=2,"
                f"MarginV={round(self.settings.subtitle.margin_bottom * scale_from_default * ass_scale)},"
                f"MarginL={round(70 * ass_scale)},MarginR={round(70 * ass_scale)}"
            ).replace(",", r"\,")
            subtitle_filter = f",subtitles={escaped}:original_size={video.width}x{video.height}:charenc=UTF-8:force_style={style}"
        vf = (
            f"scale={video.width}:{video.height}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={video.width}:{video.height},setsar=1{subtitle_filter},framerate=fps={video.fps},format={video.pixel_format}"
        )
        self.ffmpeg.run(
            ["-stream_loop", "-1", "-i", str(source_video), "-i", str(narration), "-t", f"{duration:.3f}",
             "-map", "0:v:0", "-map", "1:a:0",
             "-vf", vf, "-c:v", video.codec, "-preset", "veryfast", "-crf", "18", "-pix_fmt", video.pixel_format,
             "-r", str(video.fps), "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
             "-af", "apad", "-movflags", "+faststart", str(output)],
            "WAN_SCENE_NORMALIZATION_FAILED",
        )
        return output


class VideoComposer:
    # Very long transition chains make FFmpeg keep every source stream and
    # every intermediate xfade surface alive in one filter graph.  Apart from
    # consuming a lot of memory, that becomes disproportionately slow past a
    # few dozen scenes.  Compose modest groups first, then transition the
    # group outputs.  This preserves every boundary transition while keeping
    # each FFmpeg graph bounded.
    MAX_TRANSITION_INPUTS = 10
    TRANSITIONS = {
        "fade": "fade",
        "dissolve": "dissolve",
        "fade_black": "fadeblack",
        "fade_white": "fadewhite",
        "fade_slow": "fadeslow",
        "fade_fast": "fadefast",
        "fade_grays": "fadegrays",
        "wipe_left": "wipeleft",
        "wipe_right": "wiperight",
        "wipe_up": "wipeup",
        "wipe_down": "wipedown",
        "wipe_top_left": "wipetl",
        "wipe_top_right": "wipetr",
        "wipe_bottom_left": "wipebl",
        "wipe_bottom_right": "wipebr",
        "slide_left": "slideleft",
        "slide_right": "slideright",
        "slide_up": "slideup",
        "slide_down": "slidedown",
        "smooth": "smoothleft",
        "smooth_left": "smoothleft",
        "smooth_right": "smoothright",
        "smooth_up": "smoothup",
        "smooth_down": "smoothdown",
        "circle_open": "circleopen",
        "circle_close": "circleclose",
        "circle_crop": "circlecrop",
        "rect_crop": "rectcrop",
        "vertical_open": "vertopen",
        "vertical_close": "vertclose",
        "horizontal_open": "horzopen",
        "horizontal_close": "horzclose",
        "zoom_in": "zoomin",
        "pixelize": "pixelize",
        "radial": "radial",
        "horizontal_blur": "hblur",
        "distance": "distance",
        "squeeze_horizontal": "squeezeh",
        "squeeze_vertical": "squeezev",
        "diagonal_top_left": "diagtl",
        "diagonal_top_right": "diagtr",
        "diagonal_bottom_left": "diagbl",
        "diagonal_bottom_right": "diagbr",
        "horizontal_slice_left": "hlslice",
        "horizontal_slice_right": "hrslice",
        "vertical_slice_up": "vuslice",
        "vertical_slice_down": "vdslice",
    }

    def __init__(self, ffmpeg: FfmpegRunner, settings: Settings, profile: RenderProfile | None = None):
        self.ffmpeg = ffmpeg
        self.settings = settings
        self.profile = profile or RenderProfile.from_settings(settings)

    def build_transition_filter(self, durations: list[float], transitions: list[str], transition_seconds: float) -> tuple[str, str, str]:
        video_parts = [f"[{index}:v]settb=AVTB,setpts=PTS-STARTPTS[v{index}]" for index in range(len(durations))]
        audio_parts = [f"[{index}:a]asetpts=PTS-STARTPTS[a{index}]" for index in range(len(durations))]
        video_left, audio_left = "v0", "a0"
        elapsed = durations[0]
        for index in range(1, len(durations)):
            video_out, audio_out = f"vx{index}", f"ax{index}"
            transition = transitions[index - 1]
            if transition == "none":
                video_parts.append(f"[{video_left}][v{index}]concat=n=2:v=1:a=0[{video_out}]")
                audio_parts.append(f"[{audio_left}][a{index}]concat=n=2:v=0:a=1[{audio_out}]")
                elapsed += durations[index]
            else:
                offset = elapsed - transition_seconds
                ffmpeg_transition = self.TRANSITIONS[transition]
                video_parts.append(
                    f"[{video_left}][v{index}]xfade=transition={ffmpeg_transition}:"
                    f"duration={transition_seconds:.3f}:offset={offset:.3f}[{video_out}]"
                )
                audio_parts.append(
                    f"[{audio_left}][a{index}]acrossfade=d={transition_seconds:.3f}:c1=nofade:c2=nofade[{audio_out}]"
                )
                elapsed += durations[index] - transition_seconds
            video_left, audio_left = video_out, audio_out
        return ";".join(video_parts + audio_parts), video_left, audio_left

    def _transition_duration(self, durations: list[float], transitions: list[str], transition_seconds: float) -> float:
        """Return the duration after only non-hard-cut transitions overlap."""
        return sum(durations) - sum(transition_seconds for item in transitions if item != "none")

    @staticmethod
    def _composition_timeout(durations: list[float]) -> int:
        """Allow a long final encode enough time without relaxing scene jobs.

        Composition has to decode and re-encode the complete timeline.  Two
        times the intended running time plus a short startup margin protects
        long-form projects on modest CPUs, while the existing 15-minute
        default remains the floor for ordinary clips.
        """
        return max(900, ceil(sum(durations) * 2) + 120)

    def _compose_transition_group(
        self,
        scenes: list[Path],
        durations: list[float],
        transitions: list[str],
        transition_seconds: float,
        output: Path,
    ) -> None:
        filter_complex, video_label, audio_label = self.build_transition_filter(durations, transitions, transition_seconds)
        inputs = [item for scene in scenes for item in ("-i", str(scene))]
        video = self.profile
        self.ffmpeg.run(
            [*inputs, "-filter_complex", filter_complex, "-map", f"[{video_label}]", "-map", f"[{audio_label}]",
             "-c:v", video.codec, "-preset", "veryfast", "-crf", "23", "-pix_fmt", video.pixel_format,
             "-r", str(video.fps), "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "160k",
             "-movflags", "+faststart", str(output)],
            "VIDEO_COMPOSITION_FAILED",
            timeout_seconds=self._composition_timeout(durations),
        )

    def _compose_transition_segments(
        self,
        scenes: list[Path],
        durations: list[float],
        transitions: list[str],
        transition_seconds: float,
        output_dir: Path,
        joined: Path,
    ) -> None:
        """Compose a long timeline in bounded transition graphs.

        The original scene-to-scene transition at a group boundary is applied
        in the final pass; all other transitions are rendered in that group's
        pass.  Therefore there is no visual or audio hard-cut introduced by
        batching.
        """
        segment_dir = output_dir / "transition-segments"
        segment_dir.mkdir(parents=True, exist_ok=True)
        segment_paths: list[Path] = []
        segment_durations: list[float] = []
        boundary_transitions: list[str] = []

        for start in range(0, len(scenes), self.MAX_TRANSITION_INPUTS):
            end = min(len(scenes), start + self.MAX_TRANSITION_INPUTS)
            group_scenes = scenes[start:end]
            group_durations = durations[start:end]
            group_transitions = transitions[start:end - 1]
            segment_path = segment_dir / f"segment-{start // self.MAX_TRANSITION_INPUTS + 1:02}.mp4"

            if len(group_scenes) == 1:
                # This only happens for a one-scene package or a one-scene
                # final group. Passing the already-normalized scene through
                # avoids a needless re-encode.
                segment_path = group_scenes[0]
                segment_duration = group_durations[0]
            else:
                self._compose_transition_group(group_scenes, group_durations, group_transitions, transition_seconds, segment_path)
                segment_duration = self._transition_duration(group_durations, group_transitions, transition_seconds)

            segment_paths.append(segment_path)
            segment_durations.append(segment_duration)
            if end < len(scenes):
                boundary_transitions.append(transitions[end - 1])

        if len(segment_paths) == 1:
            self.ffmpeg.run(["-i", str(segment_paths[0]), "-c", "copy", str(joined)], "VIDEO_COMPOSITION_FAILED", timeout_seconds=self._composition_timeout(segment_durations))
            return
        self._compose_transition_group(segment_paths, segment_durations, boundary_transitions, transition_seconds, joined)

    def compose(
        self,
        scenes: list[Path],
        output_dir: Path,
        bgm: Path | None,
        durations: list[float] | None = None,
        transitions: list[str] | None = None,
        title: str | None = None,
        description: str | None = None,
        artist: str | None = "Mamase",
        bgm_fade_out_seconds: float | None = None,
    ) -> Path:
        joined = output_dir / "joined.mp4"
        transition = self.settings.video.transition_seconds
        if len(scenes) > 1 and durations and transition > 0:
            transition = min(transition, min(durations) / 2)
            selected = transitions or [self.settings.video.transition] * (len(scenes) - 1)
            if len(scenes) > self.MAX_TRANSITION_INPUTS:
                self._compose_transition_segments(scenes, durations, selected, transition, output_dir, joined)
            else:
                self._compose_transition_group(scenes, durations, selected, transition, joined)
        else:
            concat_file = output_dir / "scenes.txt"
            concat_file.write_text("".join(f"file '{path.as_posix()}'\n" for path in scenes), encoding="utf-8")
            self.ffmpeg.run(["-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(joined)], "VIDEO_COMPOSITION_FAILED")
        final = output_dir / "final.mp4"
        meta_args = build_ffmpeg_metadata_args(title=title, description=description, artist=artist or "Mamase")
        if bgm:
            bg_volume = self.settings.audio.background_volume
            narration_volume = self.settings.audio.narration_volume
            fade_out = ""
            if bgm_fade_out_seconds and bgm_fade_out_seconds > 0:
                total_duration = self._transition_duration(durations or [], transitions or [], transition) if durations else 0.0
                fade_duration = min(float(bgm_fade_out_seconds), total_duration)
                fade_start = max(0.0, total_duration - fade_duration)
                fade_out = f",afade=t=out:st={fade_start:.3f}:d={fade_duration:.3f}"
            audio_filter = (
                f"[0:a]volume={narration_volume}[n];[1:a]volume={bg_volume},"
                f"afade=t=in:st=0:d=0.5{fade_out}[bg];[bg][n]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300[duck];"
                "[n][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:LRA=11:TP=-1.5[a]"
            )
            self.ffmpeg.run(["-i", str(joined), "-stream_loop", "-1", "-i", str(bgm), "-filter_complex", audio_filter, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", *meta_args, str(final)], "VIDEO_COMPOSITION_FAILED", timeout_seconds=self._composition_timeout(durations or []))
        else:
            self.ffmpeg.run(["-i", str(joined), "-map", "0:v", "-map", "0:a", "-c:v", "copy", "-af", f"volume={self.settings.audio.narration_volume},loudnorm=I=-16:LRA=11:TP=-1.5", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", *meta_args, str(final)], "VIDEO_COMPOSITION_FAILED", timeout_seconds=self._composition_timeout(durations or []))
        return final
