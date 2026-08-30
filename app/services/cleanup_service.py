from __future__ import annotations

import shutil
import time
from pathlib import Path

from app.services.persistence import Persistence


class CleanupService:
    def __init__(self, workspace: Path, persistence: Persistence):
        self.workspace, self.persistence = workspace.resolve(), persistence

    def storage(self) -> dict:
        totals = {"totalBytes": 0, "temporaryBytes": 0, "trashBytes": 0}
        for p in self.workspace.rglob("*"):
            if p.is_symlink() or not p.is_file(): continue
            try: size=p.stat().st_size
            except OSError: continue
            totals["totalBytes"] += size
            if ".trash" in p.parts: totals["trashBytes"] += size
            elif "jobs" in p.parts: totals["temporaryBytes"] += size
        totals["database"] = str(self.persistence.path.name)
        return totals

    def clean(self) -> dict:
        removed=0; bytes_removed=0
        jobs=self.workspace / "jobs"
        if jobs.is_dir():
            for child in jobs.iterdir():
                if child.is_symlink() or not child.is_dir(): continue
                # Active jobs are only those present in the in-memory registry;
                # callers invoke this after successful jobs. Keep source/output.
                for name in ("extracted","generated-audio","subtitles","rendered-scenes","temp"):
                    target=child/name
                    if not target.is_dir(): continue
                    for p in target.rglob("*"):
                        if p.is_symlink() or not p.is_file(): continue
                        try: bytes_removed += p.stat().st_size; removed += 1
                        except OSError: pass
                    shutil.rmtree(target, ignore_errors=True)
        return {"filesRemoved":removed,"bytesRecovered":bytes_removed,"skippedActive":0}
