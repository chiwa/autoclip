from PIL import Image

# Let's crop x=500..900, y=700..1100 from assets/artemis_reel/images/scene-01-hook.png
art = Image.open("assets/artemis_reel/images/scene-01-hook.png")
crop = art.crop((500, 700, 900, 1100))
# In this crop:
# Head is at x=130..280, y=10..180
# Flag is at x=100..160, y=260..310
# Triangle is at x=85..150, y=340..420
# ART is at x=170..230, y=225..275
# NASA logo is at x=260..340, y=240..340
crop.save("scratch/crop_500_700_900_1100.png")
print("Saved scratch/crop_500_700_900_1100.png")
