#!/usr/bin/env python3
"""Compatibility entry point; Antigravity's canonical compositor is shared."""

from pathlib import Path
import runpy


CANONICAL = (
    Path(__file__).resolve().parents[4]
    / ".agents/skills/mamase-reels-cover/scripts/generate_mamase_reels_cover.py"
)

if __name__ == "__main__":
    runpy.run_path(str(CANONICAL), run_name="__main__")
