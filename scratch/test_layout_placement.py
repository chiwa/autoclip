import numpy as np
from PIL import Image, ImageFont

font_black = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 175)
font_bold = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 80)
font_prompt = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 28)

# Check text dimensions
print("ALPHA bbox:", font_black.getbbox("ALPHA"))
print("CENTAURI bbox:", font_black.getbbox("CENTAURI"))
print("Line 1 bbox:", font_bold.getbbox("ดาวที่ใกล้โลกที่สุด..."))
print("Line 2 bbox:", font_bold.getbbox("ต้องเดินทางกี่หมื่นปี?"))

# What if Title is one line?
font_title_single = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 120)
print("ALPHA CENTAURI (120pt) bbox:", font_title_single.getbbox("ALPHA CENTAURI"))
font_title_single_135 = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 135)
print("ALPHA CENTAURI (135pt) bbox:", font_title_single_135.getbbox("ALPHA CENTAURI"))

