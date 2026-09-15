from PIL import Image
import numpy as np

iss_crop = Image.open("scratch/iss_header_crop.png")
arr = np.array(iss_crop)
print("ISS header crop shape:", arr.shape)
print("Top-left pixel RGB:", arr[0, 0])
print("Middle background pixel RGB:", arr[10, 10])
