from PIL import Image

im = Image.open("assets/alpha_centauri_reel/raw/alpha_centauri_ab.png")
# Save 600px wide preview
thumb = im.resize((600, int(im.height * 600 / im.width)), Image.Resampling.LANCZOS)
thumb.save("scratch/alpha_ab_thumb.jpg", quality=90)
print("Saved scratch/alpha_ab_thumb.jpg")
