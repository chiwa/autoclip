import zipfile
import os

zip_path = "dist/mamase-eris-reel-v1.zip"
src_dir = "assets/eris_reel"

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    # 1. script.json at archive root
    script_json = os.path.join(src_dir, "script.json")
    zf.write(script_json, "script.json")
    
    # 2. video-metadata.json at archive root
    metadata_json = os.path.join(src_dir, "video-metadata.json")
    zf.write(metadata_json, "video-metadata.json")
    
    # 3. images/ directory
    img_dir = os.path.join(src_dir, "images")
    for fname in sorted(os.listdir(img_dir)):
        if fname.endswith(".png") or fname.endswith(".jpg"):
            fpath = os.path.join(img_dir, fname)
            zf.write(fpath, f"images/{fname}")

print(f"Updated {zip_path}, size: {os.path.getsize(zip_path) / (1024*1024):.2f} MB")
