from __future__ import annotations

import re
from pathlib import Path

from app.services.video_service import srt_timestamp

try:
    import pythainlp.tokenize
    HAS_PYTHAINLP = True
except ImportError:
    HAS_PYTHAINLP = False


class PodcastSubtitleService:
    """Generates 16:9 friendly timed Thai subtitles (SRT) from TTS chunks and durations."""

    @classmethod
    def _split_into_cue_texts(cls, chunk_text: str, max_chars_per_cue: int = 60) -> list[str]:
        """Split a chunk text into short, readable subtitle cues (1-2 lines)."""
        # Split by sentence or punctuation first
        if HAS_PYTHAINLP:
            try:
                sentences = pythainlp.tokenize.sent_tokenize(chunk_text)
            except Exception:
                sentences = [s.strip() for s in re.split(r"[.!?\n]+", chunk_text) if s.strip()]
        else:
            sentences = [s.strip() for s in re.split(r"[.!?\n]+", chunk_text) if s.strip()]

        if not sentences:
            sentences = [chunk_text.strip()]

        cues: list[str] = []
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            if len(sent) <= max_chars_per_cue:
                cues.append(sent)
            else:
                # Break long sentence into sub-cues by clauses or spaces/words
                parts = re.split(r"(\s+|[,;])", sent)
                current = ""
                for part in parts:
                    if not part:
                        continue
                    if len(current + part) <= max_chars_per_cue:
                        current += part
                    else:
                        if current.strip():
                            cues.append(current.strip())
                        current = part.lstrip()
                if current.strip():
                    cues.append(current.strip())

        return cues if cues else [chunk_text.strip()]

    def generate_srt(self, chunks: list[str], durations: list[float], output_path: Path) -> Path:
        """Write sequential, timed SRT file matching actual chunk durations."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        srt_lines: list[str] = []
        cue_index = 1
        elapsed_time = 0.0

        for chunk_text, chunk_dur in zip(chunks, durations):
            if chunk_dur <= 0:
                continue

            cues = self._split_into_cue_texts(chunk_text)
            total_chars = max(1, sum(len(c) for c in cues))

            cue_start = elapsed_time
            for i, cue in enumerate(cues):
                # Proportional duration based on length
                prop = len(cue) / total_chars
                dur = max(0.8, chunk_dur * prop)

                # Ensure cue does not exceed the chunk boundary for the last cue
                if i == len(cues) - 1:
                    cue_end = elapsed_time + chunk_dur
                else:
                    cue_end = min(cue_start + dur, elapsed_time + chunk_dur)

                if cue_end > cue_start + 0.1:
                    srt_lines.append(f"{cue_index}")
                    srt_lines.append(f"{srt_timestamp(cue_start)} --> {srt_timestamp(cue_end)}")
                    # If cue is somewhat long, split into 2 lines for 16:9
                    if len(cue) > 40 and " " in cue:
                        mid = len(cue) // 2
                        space_idx = cue.find(" ", mid)
                        if space_idx == -1:
                            space_idx = cue.rfind(" ", 0, mid)
                        if space_idx != -1:
                            line1 = cue[:space_idx].strip()
                            line2 = cue[space_idx:].strip()
                            cue_text = f"{line1}\n{line2}"
                        else:
                            cue_text = cue
                    else:
                        cue_text = cue

                    srt_lines.append(cue_text)
                    srt_lines.append("")
                    cue_index += 1

                cue_start = cue_end

            elapsed_time += chunk_dur

        output_path.write_text("\n".join(srt_lines), encoding="utf-8")
        return output_path
