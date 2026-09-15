from PIL import Image

im = Image.open("assets/characters/mamase-presenter-v1.png")
# Save 600px preview
thumb = im.resize((600, int(im.height * 600 / im.width)), Image.Resampling.LANCZOS)
thumb.save("scratch/presenter_v1_thumb.jpg", quality=90)
print("Saved presenter_v1_thumb.jpg")
