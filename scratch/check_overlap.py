from PIL import ImageFont

font_sub = ImageFont.truetype("assets/fonts/Prompt-Bold.ttf", 26)
sub_bbox = font_sub.getbbox("THE 4.24 LIGHT-YEAR VOYAGE TO OUR NEXT-DOOR NEIGHBOR")
print("Subline bbox:", (58 + sub_bbox[0], 725 + sub_bbox[1], 58 + sub_bbox[2], 725 + sub_bbox[3]))

font_c_title = ImageFont.truetype("assets/fonts/Kanit-Bold.ttf", 20)
c1_bbox = font_c_title.getbbox("Alpha Centauri A & B")
print("Callout 1 bbox:", (220 + c1_bbox[0], 742 + c1_bbox[1], 220 + c1_bbox[2], 742 + c1_bbox[3]))
