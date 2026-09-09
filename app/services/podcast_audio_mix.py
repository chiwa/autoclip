from __future__ import annotations


def build_podcast_audio_mix_filter(
    narration_input: int,
    bgm_input: int,
    total_duration: float,
    bgm_volume: float,
) -> str:
    """Return the canonical podcast narration/BGM ducking filter graph."""
    fade_out_start = max(0.0, total_duration - 2.0)
    return (
        f"[{narration_input}:a]volume=1.0,asplit=2[n1][n2];"
        f"[{bgm_input}:a]volume={bgm_volume},"
        f"afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_start:.2f}:d=2.0[bg];"
        "[bg][n1]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300[duck];"
        "[n2][duck]amix=inputs=2:duration=first:normalize=0,"
        "loudnorm=I=-16:LRA=11:TP=-1.5[a]"
    )
