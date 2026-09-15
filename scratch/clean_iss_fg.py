from PIL import Image
import numpy as np

fg = Image.open("scratch/test_iss_fg_1000.png")
# The crop is 1080x920 (y=1000..1920 of full canvas)
# At y=0..50 of fg:
# There is a small module at x=570..610, y=0..45
# And a tiny yellow solar panel tip at x=830..1080, y=0..20
# Let's inspect them
print("FG size:", fg.size)
