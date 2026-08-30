#!/usr/bin/env python3
import argparse
import shutil
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--older-than-hours", type=float, required=True)
parser.add_argument("--workspace", type=Path, default=Path("workspaces"))
args = parser.parse_args()
cutoff = time.time() - args.older_than_hours * 3600
for path in args.workspace.iterdir() if args.workspace.exists() else []:
    if path.is_dir() and path.stat().st_mtime < cutoff:
        shutil.rmtree(path)
        print(f"removed {path.name}")

