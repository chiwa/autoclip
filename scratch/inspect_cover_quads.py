from PIL import Image

im = Image.open("assets/alpha_centauri_reel/images/scene-01-hook.png")
w, h = im.size

# Save 3 vertical sections: Top, Mid, Bot
im.crop((0, 0, w, 700)).save("scratch/cover_section_top.jpg", quality=92)
im.crop((0, 650, w, 1250)).save("scratch/cover_section_mid.jpg", quality=92)
im.crop((0, 1200, w, h)).save("scratch/cover_section_bot.jpg", quality=92)
print("Sections saved.")
