from PIL import Image, ImageFilter
import numpy as np

ref = Image.open('assets/branding/mamase/reference/mamase-reels-editorial-poster-master.png').convert('RGB')
ref_scaled = ref.resize((1080, 1920), Image.Resampling.LANCZOS)
ref_np = np.array(ref_scaled).astype(np.float32)

raw = Image.open('assets/alpha_centauri_reel/raw/scene-01-hook-raw.png').convert('RGB')
raw_np = np.array(raw).astype(np.float32)

# Composite mask: We only want the typography, header, quote, bottom bar, and script
# Let's define the bounding regions for typography:
# 1. Header: [30:150, 40:480]
# 2. Script top-right: [30:140, 720:1040]
# 3. Kicker + Title + Hook: [210:1080, 40:680]
# 4. Quote: [980:1140, 730:1030]
# 5. Bottom bar: [1750:1910, 20:1060]

composite_np = raw_np.copy()

# Function to extract text via luminance threshold / background subtraction
def blend_text_region(y1, y2, x1, x2, threshold=20, gamma=1.2, boost=1.1):
    sub_ref = ref_np[y1:y2, x1:x2]
    sub_raw = composite_np[y1:y2, x1:x2]
    
    # Estimate local dark background
    lum = 0.299 * sub_ref[:, :, 0] + 0.587 * sub_ref[:, :, 1] + 0.114 * sub_ref[:, :, 2]
    
    # Calculate mask based on brightness above background
    mask = np.clip((lum - threshold) / (220.0 - threshold), 0, 1) ** gamma
    mask_3d = mask[:, :, np.newaxis]
    
    # Screen blend or max blend or alpha blend
    # Alpha blend:
    blended = sub_raw * (1.0 - mask_3d) + np.clip(sub_ref * boost, 0, 255) * mask_3d
    composite_np[y1:y2, x1:x2] = blended

# Apply to text regions
blend_text_region(30, 150, 40, 480, threshold=15, gamma=1.0)
blend_text_region(30, 140, 720, 1040, threshold=18, gamma=1.0)
blend_text_region(210, 1080, 40, 680, threshold=18, gamma=1.1, boost=1.05)
blend_text_region(980, 1140, 730, 1030, threshold=22, gamma=1.0)
blend_text_region(1750, 1910, 20, 1060, threshold=25, gamma=1.0)

res = Image.fromarray(np.clip(composite_np, 0, 255).astype(np.uint8))
res.save('scratch/test_blended_master.png')
print("Saved scratch/test_blended_master.png")
