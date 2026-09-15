from PIL import Image

# Open the authentic user-provided 9:16 master
src = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/media_1789216368346.jpg")
print("Uploaded image size:", src.size)

# Resize with high-quality Lanczos to native 1080x1920
img_1080x1920 = src.resize((1080, 1920), Image.Resampling.LANCZOS)

# Save as official Scene 01 and Reels cover
img_1080x1920.save("assets/eris_reel/images/scene-01-hook.png", quality=98)
img_1080x1920.save("assets/eris_reel/images/eris-reels-cover-9x16.png", quality=98)

# Also create square 1080x1080 crop (centered at y=420..1500)
# This represents the true Instagram 1:1 feed crop
img_square = img_1080x1920.crop((0, 420, 1080, 1500))
img_square.save("assets/eris_reel/images/eris-cover-square-1x1.png", quality=98)

print("Updated scene-01-hook.png, eris-reels-cover-9x16.png, and eris-cover-square-1x1.png directly from master!")
