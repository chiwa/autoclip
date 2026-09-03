from __future__ import annotations
import math, wave
from pathlib import Path

def ensure_default_bgm(workspace: Path) -> Path:
    """Create a tiny, royalty-free ambient fallback once for packages without BGM."""
    # Version the generated fallback so installations that already have the
    # original ultra-quiet file automatically receive the audible mix.
    target = workspace / "shared" / "music" / "default-ambient-v2.wav"
    if target.is_file(): return target
    target.parent.mkdir(parents=True, exist_ok=True); rate=48000; seconds=30
    chords=((220.0,277.18,329.63),(196.0,246.94,293.66),(174.61,220.0,261.63))
    with wave.open(str(target), "wb") as out:
        out.setparams((2,2,rate,0,"NONE","not compressed"))
        for i in range(rate*seconds):
            t=i/rate; chord=chords[int(t/10)%len(chords)]; sample=sum(math.sin(2*math.pi*f*t) for f in chord)/3*0.18
            value=int(32767*sample); out.writeframesraw(value.to_bytes(2,"little",signed=True)*2)
    return target
