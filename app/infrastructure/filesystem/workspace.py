from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Workspace:
    root: Path
    source: Path
    extracted: Path
    generated_audio: Path
    rendered_scenes: Path
    subtitles: Path
    output: Path


class WorkspaceManager:
    def __init__(self, root: Path):
        self.root = root

    def create(self, job_id: str) -> Workspace:
        base = (self.root / job_id).resolve()
        if base.parent != self.root.resolve():
            raise ValueError("invalid job id")
        workspace = Workspace(base, base / "source", base / "extracted", base / "generated-audio", base / "rendered-scenes", base / "subtitles", base / "output")
        for path in workspace.__dict__.values():
            Path(path).mkdir(parents=True, exist_ok=False if path == base else True)
        return workspace

    def get(self, job_id: str) -> Workspace:
        base = (self.root / job_id).resolve()
        if base.parent != self.root.resolve():
            raise ValueError("invalid job id")
        workspace = Workspace(base, base / "source", base / "extracted", base / "generated-audio", base / "rendered-scenes", base / "subtitles", base / "output")
        for path in workspace.__dict__.values():
            Path(path).mkdir(parents=True, exist_ok=True)
        return workspace

