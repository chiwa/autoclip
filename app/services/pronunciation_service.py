from __future__ import annotations
import json
from pathlib import Path
from app.domain.models import Scene

class PronunciationService:
    def __init__(self, dictionary_path: Path | None = None):
        path = dictionary_path or Path(__file__).parents[2] / "config" / "pronunciation-th.json"
        try: self.dictionary = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        except (OSError, json.JSONDecodeError): self.dictionary = {}
        self._terms = sorted(((str(k), str(v)) for k,v in self.dictionary.items()), key=lambda x: len(x[0]), reverse=True)
    def normalize(self, text: str) -> str:
        for source, target in self._terms: text = text.replace(source, target)
        return text
    def resolve_scene(self, scene: Scene) -> str:
        override = (scene.tts_text or "").strip()
        return self.normalize(override or scene.narration)
