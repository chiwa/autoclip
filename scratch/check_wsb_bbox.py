from PIL import Image

im = Image.open("assets/where_space_begins_reel/images/scene-01-hook.png")
print("Size:", im.size)
# In this image, the presenter is on the right side:
# Head is around x=300..800, y=100..700!
# Wait! In that image, his head is at y=100! That would occupy the top area where typography needs to be!
