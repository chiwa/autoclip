import numpy as np
from PIL import Image, ImageDraw, ImageFilter

end_img = Image.open("assets/branding/mamase/reels-end-scene.png").convert("RGB")
arr = np.array(end_img) # shape (1672, 941, 3)

# In end_img:
# Let us inspect row by row from bottom to top:
# Where do the characters and mountain lie?
# Boy head: around row 960..1050, col 50..300
# Dog head: around row 1000..1100, col 300..500
# Horizon clouds: around row 1100..1250, col 500..941
# Above that (rows 0 to 950) is the starry sky with text!

# Let us verify if rows < 950 can be completely replaced by the cosmic sky + Jupiter!
# If rows < 960 are sky, then the entire text ("MAMASE PODCAST", "Explore the world...", "เพราะในจักรวาลนี้...", "THANK YOU FOR WATCHING")
# is above row 1100, EXCEPT "เพราะในจักรวาลนี้" which is around row 950..1100 on the right side!
print("End img shape:", arr.shape)
