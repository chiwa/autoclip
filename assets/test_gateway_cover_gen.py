from PIL import Image
import os, sys

# Import our new skill module
sys.path.append(".agents/skills/mamase-reels-cover/scripts")
from generate_mamase_reels_cover import create_reels_cover

base_path = "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/lunar_gateway_cover_base_1789258793878.jpg"
out_9x16 = "assets/lunar_gateway_reel/images/scene-01-hook.png"
out_1x1 = "assets/lunar_gateway_reel/images/gateway-cover-square-1x1.png"

# Coordinates in 1080x1920:
# Station is roughly centered at y ~ 500..800
# Ion engine / PPE is at x ~ 300, y ~ 700
# HALO module is at x ~ 620, y ~ 640
# Moon limb is at x ~ 750, y ~ 450
callouts = [
    {
        "from": (280, 710),
        "mid": (180, 750),
        "to": (50, 750),
        "text_pos": (50, 705),
        "title": "PPE Module",
        "sub": "ION ELECTRIC PROPULSION"
    },
    {
        "from": (640, 630),
        "mid": (720, 580),
        "to": (920, 580),
        "text_pos": (720, 535),
        "title": "HALO Module",
        "sub": "HABITATION & DOCKING HUB"
    },
    {
        "from": (650, 930),
        "mid": (580, 980),
        "to": (280, 980),
        "text_pos": (280, 935),
        "title": "NRHO Orbit",
        "sub": "STAGING & SOUTH POLE ACCESS"
    }
]

create_reels_cover(
    base_image_path=base_path,
    output_9x16_path=out_9x16,
    output_1x1_path=out_1x1,
    title="LUNAR GATEWAY",
    headline_th="จำเป็นจริงไหม?",
    sub_th="หรือแค่ทำให้ภารกิจซับซ้อนและแพงขึ้น?",
    sub_en="Essential Infrastructure or Costly Detour?",
    callouts=callouts,
    slogan_pos=(710, 1490),
    title_y=1580,
    clean_bottom_height=260
)

# Also copy 9:16 as gateway-reels-cover-9x16.png
import shutil
shutil.copyfile(out_9x16, "assets/lunar_gateway_reel/images/gateway-reels-cover-9x16.png")
shutil.copyfile(out_9x16, "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/gateway_cover_9x16.png")
shutil.copyfile(out_1x1, "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/gateway_cover_1x1.png")

print("Gateway master cover generated via skill!")
