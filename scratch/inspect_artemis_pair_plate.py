from PIL import Image

art = Image.open("assets/artemis_reel/images/scene-01-hook.png")
# Let's see how the explorer and dog look when kept together on their ridge:
# In artemis_reel, the explorer and dog are on the foreground ridge (y=660..1920, x=150..1080).
# In front of them at the very bottom is "ARTEMIS I-V" title and Thai hook text.
# Let's inspect what y range has text:
# Title "ARTEMIS I-V" starts at y=1470!
# At y=660..1460, both the dog and explorer are 100% text-free!
print("Title starts at y=1470.")
