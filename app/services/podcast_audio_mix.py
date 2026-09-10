from __future__ import annotations


def build_podcast_audio_mix_filter(
    narration_input: int,
    bgm_input: int,
    total_duration: float,
    bgm_volume: float,
    output_label: str = "a",
) -> str:
    """Return the canonical podcast narration/BGM ducking filter graph."""
    fade_out_start = max(0.0, total_duration - 2.0)
    return (
        f"[{narration_input}:a]volume=1.0,asplit=2[n1][n2];"
        f"[{bgm_input}:a]volume={bgm_volume},"
        f"afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_start:.2f}:d=2.0[bg];"
        "[bg][n1]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300[duck];"
        "[n2][duck]amix=inputs=2:duration=first:normalize=0,"
        f"loudnorm=I=-16:LRA=11:TP=-1.5[{output_label}]"
    )


def build_podcast_ending_filter(
    main_label: str,
    ending_input: int,
    ending_duration: float,
    *,
    output_label: str = "a",
    fade_in_seconds: float = 0.25,
    fade_out_seconds: float = 0.75,
) -> str:
    """Append the complete ending theme after the narration program audio."""
    fade_out = min(fade_out_seconds, ending_duration)
    fade_out_start = max(0.0, ending_duration - fade_out)
    return (
        f"[{main_label}]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[program];"
        f"[{ending_input}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
        f"afade=t=in:st=0:d={min(fade_in_seconds, ending_duration):.3f},"
        f"afade=t=out:st={fade_out_start:.3f}:d={fade_out:.3f},asetpts=PTS-STARTPTS[theme];"
        f"[program][theme]concat=n=2:v=0:a=1[{output_label}]"
    )
