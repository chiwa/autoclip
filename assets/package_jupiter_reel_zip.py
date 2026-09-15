import os
import zipfile
import shutil
from pathlib import Path

source_dir = Path("assets/jupiter_as_a_star_reel")
dist_dir = Path("dist")
dist_dir.mkdir(exist_ok=True)
zip_path = dist_dir / "mamase-jupiter-as-a-star-reel-v1.zip"

print(f"Packaging {zip_path}...")
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    # Add script.json at root
    zf.write(source_dir / "script.json", arcname="script.json")
    print("Added script.json")
    
    # Add video-metadata.json at root
    zf.write(source_dir / "video-metadata.json", arcname="video-metadata.json")
    print("Added video-metadata.json")
    
    # Add images
    images_dir = source_dir / "images"
    for img_path in sorted(images_dir.glob("*.png")):
        arcname = f"images/{img_path.name}"
        zf.write(img_path, arcname=arcname)
        print(f"Added {arcname}")

print(f"Successfully packaged {zip_path} (Size: {zip_path.stat().st_size / (1024*1024):.2f} MB)")
