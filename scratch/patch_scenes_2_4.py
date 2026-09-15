from PIL import Image, ImageEnhance
from pathlib import Path
import numpy as np

TARGET_W = 1080
TARGET_H = 1920
RAW_DIR = Path("scratch/pale_blue_dot_raw")
PREVIEW_DIR = Path("scratch/pale_blue_dot_preview")

def apply_safe_area_vignette(img, bot_height=420, top_height=140):
    w, h = img.size
    arr = np.zeros((h, w, 4), dtype=np.float32)
    y_bot = np.linspace(0.0, 1.0, bot_height) ** 1.8 * 210
    arr[-bot_height:, :, 3] = y_bot[:, None]
    y_top = np.linspace(1.0, 0.0, top_height) ** 1.5 * 140
    arr[:top_height, :, 3] = np.maximum(arr[:top_height, :, 3], y_top[:, None])
    vignette = Image.fromarray(arr.astype(np.uint8))
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(vignette)
    return img_rgba.convert("RGB")

def patch_scene_02():
    print("Re-rendering Scene 02 with crop_x=320...")
    src = Image.open(RAW_DIR / "voyager_view_solar_system.jpg").convert("RGB")
    crop_h = src.height # 1935
    crop_w = int(crop_h * 9 / 16) # 1088
    crop_x = 320 # Pushes spacecraft completely out of right border
    cropped = src.crop((crop_x, 0, crop_x + crop_w, crop_h))
    res = cropped.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    enh = ImageEnhance.Contrast(res).enhance(1.18)
    enh = ImageEnhance.Color(enh).enhance(1.12)
    res_final = apply_safe_area_vignette(enh, bot_height=420, top_height=140)
    out_file = PREVIEW_DIR / "scene-02-solar-system-zoom.png"
    res_final.save(out_file, format="PNG", optimize=True)
    print("Saved:", out_file)

def patch_scene_04():
    print("Re-rendering Scene 04 with clean scan platform optics...")
    src = Image.open(RAW_DIR / "voyager_spacecraft.jpg").convert("RGB")
    crop_w = 850
    crop_h = int(crop_w * 16 / 9) # 1511
    crop_x = 280
    crop_y = 120
    cropped = src.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
    res = cropped.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    enh = ImageEnhance.Contrast(res).enhance(1.18)
    enh = ImageEnhance.Color(enh).enhance(1.12)
    res_final = apply_safe_area_vignette(enh, bot_height=420, top_height=140)
    out_file = PREVIEW_DIR / "scene-04-cagan-turn-camera.png"
    res_final.save(out_file, format="PNG", optimize=True)
    print("Saved:", out_file)

if __name__ == "__main__":
    patch_scene_02()
    patch_scene_04()
