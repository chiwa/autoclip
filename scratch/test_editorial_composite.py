import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H = 1080, 1920

# 1. Load Raw Artwork
raw_path = "assets/alpha_centauri_reel/raw/scene-01-hook-raw.png"
base = Image.open(raw_path).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)

# 2. Authentic Mamase Podcast Header (Top-Left)
header_path = "assets/branding/mamase/mamase_podcast_header.png"
header = Image.open(header_path).convert("RGBA")
# Scale header to fit width ~390px
hw = 390
hh = int(header.height * (hw / header.width))
header_scaled = header.resize((hw, hh), Image.Resampling.LANCZOS)
base.alpha_composite(header_scaled, (56, 46))

# 3. Top-Right Script Accent: "Different Stars / Same Curiosity"
# We can use Bradley Hand Bold, Noteworthy, or Sriracha
try:
    font_script = ImageFont.truetype("/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf", 34)
except:
    font_script = ImageFont.truetype("assets/fonts/Sriracha-Regular.ttf", 34)

s_draw = ImageDraw.Draw(base)
# Rotated slightly or clean angled script
script_layer = Image.new("RGBA", (340, 120), (0, 0, 0, 0))
sl_draw = ImageDraw.Draw(script_layer)
sl_draw.text((10, 10), "Different Stars\nSame Curiosity", font=font_script, fill="#F5C842", spacing=2, align="right")
# Underline flourish
sl_draw.line([(90, 95), (280, 75)], fill="#F5C842", width=3)
script_rot = script_layer.rotate(4, resample=Image.Resampling.BICUBIC, expand=True)
base.alpha_composite(script_rot, (720, 42))

# 4. Kicker (Tracked Small Caps)
font_kicker = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 20)
kicker_lines = [
    "O U R",
    "N E X T   H O M E",
    "A M O N G",
    "T H E   S T A R S ?"
]
ky = 215
for line in kicker_lines:
    # Subtle drop shadow
    s_draw.text((58 + 2, ky + 2), line, font=font_kicker, fill=(0, 0, 0, 180))
    s_draw.text((58, ky), line, font=font_kicker, fill="#A4C7E8")
    ky += 32

s_draw.line([(58, ky + 6), (150, ky + 6)], fill="#78D7FF", width=2)

# 5. Title: "ALPHA" + "CENTAURI"
# ALPHA: Large bold display font with cyan refraction glow
font_alpha = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 152)
font_centauri = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 46)

# Render ALPHA with subtle glow
alpha_y = 360
# Glow
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
g_draw = ImageDraw.Draw(glow)
g_draw.text((54, alpha_y), "ALPHA", font=font_alpha, fill=(120, 215, 255, 140))
glow = glow.filter(ImageFilter.GaussianBlur(16))
base.alpha_composite(glow)

# Alpha text drop shadow
s_draw.text((54 + 4, alpha_y + 6), "ALPHA", font=font_alpha, fill=(0, 0, 0, 240))
s_draw.text((54, alpha_y), "ALPHA", font=font_alpha, fill="#F6F7F4")

# Shimmer refraction flare on 'A' apex:
flare = Image.new("RGBA", (W, H), (0, 0, 0, 0))
f_draw = ImageDraw.Draw(flare)
# Apex of 'A' is approx at (110, alpha_y + 15)
ax, ay = 110, alpha_y + 15
f_draw.line([(ax - 60, ay), (ax + 60, ay)], fill=(200, 240, 255, 220), width=2)
f_draw.line([(ax, ay - 60), (ax, ay + 60)], fill=(200, 240, 255, 220), width=2)
f_draw.line([(ax - 100, ay + 40), (ax + 100, ay - 40)], fill=(120, 215, 255, 180), width=2)
f_draw.ellipse([(ax - 8, ay - 8), (ax + 8, ay + 8)], fill=(255, 255, 255, 255))
flare = flare.filter(ImageFilter.GaussianBlur(2))
base.alpha_composite(flare)

# CENTAURI in Champagne Gold with letter spacing
centauri_text = "C  E  N  T  A  U  R  I"
centauri_y = alpha_y + 155
s_draw.text((58 + 3, centauri_y + 4), centauri_text, font=font_centauri, fill=(0, 0, 0, 230))
s_draw.text((58, centauri_y), centauri_text, font=font_centauri, fill="#F5E6C8")

# 6. Thai Hook
# Line 1: ดาวที่ใกล้เราที่สุด (Kanit-Bold, 66pt)
# Line 2: แต่ต้องใช้เวลาเดินทางนานถึง (Kanit-Bold, 54pt)
# Line 3: 73,000 ปี! (Kanit-Black, 94pt, warm solar gold)
# Subline: บ้านหลังถัดไปของเรา...อยู่ไกลแค่ไหน? (Prompt-Bold, 26pt, icy cyan-blue)

font_hook_1 = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 68)
font_hook_2 = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 54)
font_hook_3 = ImageFont.truetype("assets/fonts/Kanit-Black.ttf", 96)
font_subline = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 26)

hy1 = centauri_y + 85
s_draw.text((58 + 4, hy1 + 5), "ดาวที่ใกล้เราที่สุด", font=font_hook_1, fill=(0, 0, 0, 230))
s_draw.text((58, hy1), "ดาวที่ใกล้เราที่สุด", font=font_hook_1, fill="#F6F7F4")

hy2 = hy1 + 82
s_draw.text((58 + 4, hy2 + 5), "แต่ต้องใช้เวลาเดินทางนานถึง", font=font_hook_2, fill=(0, 0, 0, 230))
s_draw.text((58, hy2), "แต่ต้องใช้เวลาเดินทางนานถึง", font=font_hook_2, fill="#F6F7F4")

hy3 = hy2 + 75
# Solar Gold Glow for 73,000 ปี!
gold_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gg_draw = ImageDraw.Draw(gold_glow)
gg_draw.text((58, hy3), "73,000 ปี!", font=font_hook_3, fill=(255, 180, 40, 160))
gold_glow = gold_glow.filter(ImageFilter.GaussianBlur(14))
base.alpha_composite(gold_glow)

s_draw.text((58 + 5, hy3 + 6), "73,000 ปี!", font=font_hook_3, fill=(0, 0, 0, 250))
s_draw.text((58, hy3), "73,000 ปี!", font=font_hook_3, fill="#FFC83B")

# Subline & divider
hy4 = hy3 + 120
s_draw.text((58 + 2, hy4 + 3), "บ้านหลังถัดไปของเรา...อยู่ไกลแค่ไหน?", font=font_subline, fill=(0, 0, 0, 210))
s_draw.text((58, hy4), "บ้านหลังถัดไปของเรา...อยู่ไกลแค่ไหน?", font=font_subline, fill="#BCD5EB")
s_draw.line([(58, hy4 + 42), (210, hy4 + 42)], fill="#78D7FF", width=3)

# 7. Factually Accurate Celestial Callouts
# Alpha Centauri A: center at (770, 245)
# Alpha Centauri B: center at (680, 410)
# Proxima b (planet): center at (570, 480)
font_callout_title = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 22)
font_callout_sub = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 16)

# Callout A: above star A
s_draw.line([(770, 160), (770, 130), (620, 130)], fill=(255, 215, 120, 200), width=2)
s_draw.ellipse([(770 - 4, 160 - 4), (770 + 4, 160 + 4)], fill=(255, 235, 180, 255))
s_draw.text((620, 78), "Alpha Centauri A", font=font_callout_title, fill="#FFFFFF")
s_draw.text((620, 104), "(Rigil Kentaurus)", font=font_callout_sub, fill="#F5C842")

# Callout B: to the right of star B
s_draw.line([(740, 410), (840, 410)], fill=(255, 180, 100, 200), width=2)
s_draw.ellipse([(740 - 4, 410 - 4), (740 + 4, 410 + 4)], fill=(255, 210, 150, 255))
s_draw.text((850, 390), "Alpha Centauri B", font=font_callout_title, fill="#FFFFFF")
s_draw.text((850, 416), "(Toliman)", font=font_callout_sub, fill="#FFAC70")

# Callout Proxima b:
s_draw.line([(540, 500), (460, 500), (460, 540)], fill=(120, 215, 255, 200), width=2)
s_draw.ellipse([(540 - 3, 500 - 3), (540 + 3, 500 + 3)], fill=(200, 240, 255, 255))
s_draw.text((420, 546), "Proxima b", font=font_callout_sub, fill="#BCD5EB")

# 8. Right Margin Editorial Quote (at x=760..1020, y=940..1030)
font_quote = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 17)
quote_lines = [
    "“A SMALL STEP",
    "IN CURIOSITY",
    "A BIGGER TOMORROW",
    "FOR HUMANITY.”"
]
qy = 930
for line in quote_lines:
    s_draw.text((750 + 2, qy + 2), line, font=font_quote, fill=(0, 0, 0, 180))
    s_draw.text((750, qy), line, font=font_quote, fill="#8EA8C4")
    qy += 26

# 9. Bottom Editorial Audio / Brand Bar (at y=1830..1875)
# Sits cleanly on the bottom deck, out of subtitle-safe zone
font_bar_main = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 21)
font_bar_sub = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 15)
font_bar_cat = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 18)

# Headphones icon circle at (75, 1845)
s_draw.ellipse([(58, 1828), (106, 1876)], outline="#F5C842", width=2)
# Draw mini headphones inside
s_draw.arc([(68, 1838), (96, 1866)], start=180, end=0, fill="#F5C842", width=3)
s_draw.rectangle([(66, 1850), (72, 1864)], fill="#F5C842")
s_draw.rectangle([(92, 1850), (98, 1864)], fill="#F5C842")

# Podcast badge text
s_draw.text((120, 1826), "MAMASE PODCAST", font=font_bar_main, fill="#F6F7F4")
s_draw.text((120, 1852), "STORIES FROM THE UNIVERSE", font=font_bar_sub, fill="#F5C842")

# Divider line
s_draw.line([(520, 1832), (520, 1872)], fill="#5A728A", width=2)

# Category tags
s_draw.text((550, 1840), "SCIENCE   •   SPACE   •   HUMANITY", font=font_bar_cat, fill="#F6F7F4")

# Outer frame border around podcast info
s_draw.line([(50, 1818), (480, 1818)], fill=(245, 200, 66, 140), width=1)
s_draw.line([(50, 1884), (480, 1884)], fill=(245, 200, 66, 140), width=1)

# Save result
out_path = "scratch/test_editorial_scene01.png"
base.convert("RGB").save(out_path, quality=98)
print("Rendered:", out_path)
