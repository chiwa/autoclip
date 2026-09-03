"""Small isolated worker for the Wayu Kokoro Thai ONNX bundle."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf


def split_text(text: str, max_chars: int = 140) -> list[str]:
    """Split long Thai narration into model-safe, sentence-aware chunks."""
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return [text]
    sentences = [part.strip() for part in re.split(r"(?<=[.!?…。！？;:])\s*", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        while len(sentence) > max_chars:
            cut = sentence.rfind(" ", 0, max_chars + 1)
            cut = cut if cut >= max_chars // 2 else max_chars
            piece, sentence = sentence[:cut].strip(), sentence[cut:].strip()
            if piece:
                if current:
                    chunks.append(current)
                    current = ""
                chunks.append(piece)
        if not sentence:
            continue
        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks or [text]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--voice", default="m_young_clear")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.model_dir).resolve()
    sys.path.insert(0, str(root))
    from kokoro_thai.g2p import ThaiG2P
    from kokoro_thai.onnx_infer import load_onnx, load_styles, synth
    roster = json.loads((root / "data" / "seeds" / "roster.json").read_text(encoding="utf-8"))
    by_name = {str(item["name"]): item for item in roster}
    selected = by_name.get(args.voice) or by_name.get("m_young_clear") or roster[9]
    style = load_styles(root / "onnx")[int(selected["id"])]
    student = load_onnx(root / "onnx", g2p=ThaiG2P(), precision="fp32", intra_threads=2)
    parts = [synth(student, chunk, style, speed=args.speed) for chunk in split_text(args.text)]
    parts = [part for part in parts if part.size]
    if not parts:
        return 2
    # A short join pause prevents words at chunk boundaries from being clipped
    # while keeping the narration natural.
    pause = np.zeros(round(0.08 * 24000), dtype=np.float32)
    audio = np.concatenate([part if index == len(parts) - 1 else np.concatenate([part, pause]) for index, part in enumerate(parts)])
    sf.write(args.output, np.asarray(audio, dtype=np.float32), 24000)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
