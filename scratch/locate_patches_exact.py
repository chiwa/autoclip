from PIL import Image

im = Image.open("assets/lunar_gateway_reel/images/scene-01-hook.png").convert("RGBA")
# Let's crop x=700..950, y=950..1300
crop_upper = im.crop((700, 950, 950, 1300))
crop_upper.save("scratch/crop_upper_body.png")
print("Saved scratch/crop_upper_body.png")
