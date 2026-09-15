from PIL import Image

# The true 1:1 master is media_1789215531601.jpg
src_sq = Image.open("/Users/zengcode/.gemini/antigravity/brain/be4e5334-0b2c-43a2-b1e0-78f58d22bc55/.user_uploaded/media_1789215531601.jpg")
sq_1080 = src_sq.resize((1080, 1080), Image.Resampling.LANCZOS)
sq_1080.save("assets/eris_reel/images/eris-cover-square-1x1.png", quality=98)
print("Saved authentic square master to assets/eris_reel/images/eris-cover-square-1x1.png")
