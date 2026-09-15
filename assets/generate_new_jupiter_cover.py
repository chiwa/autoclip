import os, sys, shutil

sys.path.append(".agents/skills/mamase-reels-cover/scripts")
from generate_mamase_reels_cover import create_reels_cover

base_path = "assets/jupiter_as_a_star_reel/raw/jupiter_summit_master_base.png"
out_9x16 = "assets/jupiter_as_a_star_reel/images/scene-01-hook.png"
out_1x1 = "assets/jupiter_as_a_star_reel/images/jupiter-cover-square-1x1.png"

callouts = [
    {
        "from": (320, 280),
        "mid": (200, 230),
        "to": (70, 230),
        "text_pos": (70, 185),
        "title": "Brown Dwarf Limit",
        "sub": "NEEDS 13x MASS FOR DEUTERIUM FUSION"
    },
    {
        "from": (820, 260),
        "mid": (880, 210),
        "to": (980, 210),
        "text_pos": (680, 165),
        "title": "True Star Limit",
        "sub": "75-80x MASS TO IGNITE HYDROGEN"
    },
    {
        "from": (230, 680),
        "mid": (150, 720),
        "to": (60, 720),
        "text_pos": (60, 675),
        "title": "Failed Star Myth",
        "sub": "JUPITER HAS ONLY 0.1% OF SOLAR MASS"
    }
]

create_reels_cover(
    base_image_path=base_path,
    output_9x16_path=out_9x16,
    output_1x1_path=out_1x1,
    title="JUPITER",
    headline_th="ถ้าดาวพฤหัส กลายเป็นดาวฤกษ์?",
    sub_th="โลกเราจะมีดวงอาทิตย์ 2 ดวง... จริงหรือแค่เรื่องเล่า?",
    sub_en="Failed Star Myth Debunked: The Science of Brown Dwarfs",
    callouts=callouts,
    slogan_pos=(680, 1500),
    title_y=1590,
    clean_bottom_height=220
)

# Also duplicate as jupiter-reels-cover-9x16.png
shutil.copyfile(out_9x16, "assets/jupiter_as_a_star_reel/images/jupiter-reels-cover-9x16.png")
# Also copy to artifacts directory for display
shutil.copyfile(out_9x16, "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/jupiter-reels-cover-9x16.png")
shutil.copyfile(out_1x1, "/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/jupiter-cover-square-1x1.png")

print("Generated new Master Cover 9:16 and 1:1 square successfully!")
