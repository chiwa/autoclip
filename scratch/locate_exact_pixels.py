from PIL import Image

im = Image.open("assets/artemis_reel/images/scene-01-hook.png")

# Explorer's arm: Let's crop x=600..750, y=950..1250
im.crop((600, 950, 750, 1250)).save("scratch/crop_arm_exact.png")

# Explorer's backpack: Let's crop x=800..980, y=950..1250
im.crop((800, 950, 980, 1250)).save("scratch/crop_bp_exact.png")

# Text "Same Sky": crop x=750..1020, y=1450..1650
im.crop((750, 1450, 1020, 1650)).save("scratch/crop_txt_exact.png")

print("Saved exact pixel crops.")
