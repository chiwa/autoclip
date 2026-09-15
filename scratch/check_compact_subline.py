from PIL import ImageFont

font_sub = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 26)
bbox = font_sub.getbbox("4.24 LIGHT-YEARS & THE 73,000-YEAR VOYAGE")
print("Compact subline width:", bbox[2] - bbox[0])
print("Ending X:", 58 + bbox[2])
