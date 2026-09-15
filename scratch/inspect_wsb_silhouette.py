from PIL import Image
import numpy as np

wsb = Image.open("assets/where_space_begins_reel/images/scene-01-hook.png")
# Let's inspect the bounding box of the explorer in WSB:
# He is on the left from x=0 to roughly x=900, y=50 to 1920
# In the background:
# At y=0..600, x>600 is dark starry sky (R<40, G<50, B<90).
# At y=600..1200, x>650 is sunset clouds (warm orange/beige).
# Below y=1200, x>800 is dark mountains.

# Let's see how cleanly we can separate him:
# We can create a mask using edge detection / threshold / interactive polygon
print("WSB dimensions:", wsb.size)
