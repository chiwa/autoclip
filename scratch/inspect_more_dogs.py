from PIL import Image
import numpy as np

# Let's inspect where dogs appear in other reels
# Look at voyager1_reel, iss_why_not_fall_reel, jupiter_as_a_star_reel
# In iss_why_not_fall_reel, the dog is seated next to explorer facing forward/away.
# Let's check if there are other images with the dog:
import glob
for p in glob.glob("assets/**/*dog*", recursive=True) + glob.glob("scratch/**/*dog*", recursive=True):
    print(p)
