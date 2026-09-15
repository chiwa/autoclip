from PIL import Image, ImageDraw, ImageFont

img = Image.new("RGBA", (1080, 800), (5, 10, 25, 255))
draw = ImageDraw.Draw(img)

fonts = [
    ("Didot", "/System/Library/Fonts/Supplemental/Didot.ttc", 0, 160),
    ("Bodoni 72", "/System/Library/Fonts/Supplemental/Bodoni 72.ttc", 0, 160),
    ("Optima", "/System/Library/Fonts/Optima.ttc", 0, 160),
    ("Futura Medium", "/System/Library/Fonts/Supplemental/Futura.ttc", 0, 150),
    ("Avenir Next Medium", "/System/Library/Fonts/Avenir Next.ttc", 0, 150),
]

y = 20
for name, path, idx, sz in fonts:
    f = ImageFont.truetype(path, sz, index=idx)
    draw.text((40, y), f"ALPHA ({name})", font=f, fill="#FFFFFF")
    y += sz + 10

img.save("scratch/test_fonts_alpha.png")
print("Saved scratch/test_fonts_alpha.png")
