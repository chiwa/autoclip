from PIL import Image

im = Image.open("assets/lunar_gateway_reel/images/scene-01-hook.png").convert("RGBA")
# explorer's arm is more to the right:
# Let's crop x=680..760, y=1050..1250
crop_arm = im.crop((680, 1050, 760, 1250))
crop_arm.save("scratch/crop_arm_actual.png")
print("Saved scratch/crop_arm_actual.png")
