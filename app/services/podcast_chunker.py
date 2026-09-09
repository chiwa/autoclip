from __future__ import annotations

import re

try:
    import pythainlp.tokenize
    HAS_PYTHAINLP = True
except ImportError:
    HAS_PYTHAINLP = False


class PodcastChunker:
    """Chunks long podcast scripts for TTS using UTF-8 byte limits and Thai word boundaries."""

    @staticmethod
    def byte_len(text: str) -> int:
        return len(text.encode("utf-8"))

    @classmethod
    def _split_sentence(cls, text: str) -> list[str]:
        """Split text into sentences or clause units."""
        if HAS_PYTHAINLP:
            try:
                sentences = pythainlp.tokenize.sent_tokenize(text)
                if sentences:
                    return [s.strip() for s in sentences if s.strip()]
            except Exception:
                pass

        # Fallback sentence boundary regex (newlines, question marks, exclamation marks, periods, Thai pauses)
        parts = re.split(r"([.!?\n]+|\s{2,})", text)
        sentences = []
        current = ""
        for part in parts:
            if not part:
                continue
            current += part
            if re.match(r"[.!?\n]+|\s{2,}", part):
                if current.strip():
                    sentences.append(current.strip())
                current = ""
        if current.strip():
            sentences.append(current.strip())
        return sentences if sentences else [text.strip()]

    @classmethod
    def _split_words(cls, text: str) -> list[str]:
        """Tokenize text into words so word boundaries are never cut."""
        if HAS_PYTHAINLP:
            try:
                tokens = pythainlp.tokenize.word_tokenize(text, keep_whitespace=True)
                if tokens:
                    return tokens
            except Exception:
                pass
        # Fallback: whitespace tokenization preserving spaces
        return re.findall(r"\S+|\s+", text)

    @classmethod
    def _split_long_sentence(cls, sentence: str, max_bytes: int) -> list[str]:
        """Split a single sentence exceeding max_bytes into sub-units by word boundaries."""
        words = cls._split_words(sentence)
        sub_chunks: list[str] = []
        current = ""

        for word in words:
            # Pathological case: a single word larger than max_bytes
            word_bytes = cls.byte_len(word)
            if word_bytes > max_bytes:
                if current.strip():
                    sub_chunks.append(current.strip())
                    current = ""
                # Slice safely by unicode characters without breaking UTF-8 byte boundaries
                cur_slice = ""
                for char in word:
                    if cls.byte_len(cur_slice + char) > max_bytes:
                        if cur_slice:
                            sub_chunks.append(cur_slice)
                        cur_slice = char
                    else:
                        cur_slice += char
                if cur_slice:
                    current = cur_slice
                continue

            test_str = current + word if current else word
            if cls.byte_len(test_str) <= max_bytes:
                current = test_str
            else:
                if current.strip():
                    sub_chunks.append(current.strip())
                current = word.lstrip()

        if current.strip():
            sub_chunks.append(current.strip())

        return sub_chunks

    @classmethod
    def chunk(cls, script: str, max_bytes: int = 2800) -> list[str]:
        """Chunk script deterministically into parts each <= max_bytes UTF-8."""
        cleaned = script.strip()
        if not cleaned:
            return []

        if cls.byte_len(cleaned) <= max_bytes:
            return [cleaned]

        # Step 1: Split into paragraphs first
        raw_paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", cleaned) if p.strip()]
        if not raw_paragraphs:
            raw_paragraphs = [cleaned]

        # Step 2: Break paragraphs that exceed max_bytes into sentences or words
        atomic_units: list[str] = []
        for paragraph in raw_paragraphs:
            if cls.byte_len(paragraph) <= max_bytes:
                atomic_units.append(paragraph)
            else:
                sentences = cls._split_sentence(paragraph)
                for sentence in sentences:
                    if cls.byte_len(sentence) <= max_bytes:
                        atomic_units.append(sentence)
                    else:
                        sub_units = cls._split_long_sentence(sentence, max_bytes)
                        atomic_units.extend(sub_units)

        # Step 3: Greedy aggregation into chunks <= max_bytes
        chunks: list[str] = []
        current_chunk = ""

        for unit in atomic_units:
            unit = unit.strip()
            if not unit:
                continue

            if not current_chunk:
                current_chunk = unit
                continue

            # Join with newline if units were paragraphs or with space
            separator = "\n\n" if ("\n" in unit or "\n" in current_chunk) else " "
            combined = f"{current_chunk}{separator}{unit}"

            if cls.byte_len(combined) <= max_bytes:
                current_chunk = combined
            else:
                chunks.append(current_chunk.strip())
                current_chunk = unit

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks
