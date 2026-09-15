#!/usr/bin/env python3
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path
from app.services.package_service import PackageService

def validate(zip_path_str: str):
    zip_path = Path(zip_path_str).resolve()
    if not zip_path.exists():
        print(f"ERROR: File not found: {zip_path}")
        sys.exit(1)
        
    print(f"=== 1. Validating Archive Integrity ({zip_path.name}) ===")
    res = subprocess.run(["unzip", "-t", str(zip_path)], capture_output=True, text=True)
    if res.returncode != 0:
        print("ERROR: unzip -t failed:")
        print(res.stderr or res.stdout)
        sys.exit(1)
    print("Archive integrity verified (unzip -t: OK)")
    
    print("\n=== 2. Validating AutoClip Contract (PackageService) ===")
    extract_dir = Path("/tmp/autoclip_skill_val")
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        service = PackageService(50_000_000)
        script, bgm = service.extract_and_validate(zip_path, extract_dir)
        print("PackageService validation PASSED!")
        print(f"Project ID:    {script.project.id}")
        print(f"Project Title: {script.project.title}")
        print(f"Language:      {script.project.language}")
        print(f"Resolution:    {script.project.resolution}")
        print(f"Total Scenes:  {len(script.scenes)}")
        print(f"Voice:         {script.voice.provider} ({script.voice.voice}, speed={script.voice.speed})")
        print(f"BGM Found:     {bgm.name if bgm else 'None'}")
        
        # Check metadata
        meta_file = extract_dir / "video-metadata.json"
        if meta_file.exists():
            print("video-metadata.json: OK")
        else:
            print("WARNING: video-metadata.json missing at root")
            
        print("\n=== ALL VALIDATIONS PASSED 100% ===")
    finally:
        if extract_dir.exists():
            shutil.rmtree(extract_dir)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_package.py <path-to-zip>")
        sys.exit(1)
    validate(sys.argv[1])
