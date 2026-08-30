#!/usr/bin/env python3
"""Download and validate every bundled local Thai voice during image build."""

from pathlib import Path

from vachanatts import TTS


def main() -> None:
    output = Path("/tmp/autoclip-tts-warmup.wav")
    for voice in ("th_f_1", "th_m_1", "th_f_2", "th_m_2"):
        TTS(text="ทดสอบเสียง", voice=voice, output=str(output), speed=1.0)
        if not output.is_file() or output.stat().st_size <= 44:
            raise RuntimeError(f"Thai TTS voice failed to initialize: {voice}")
        output.unlink()


if __name__ == "__main__":
    main()
