import os, glob

# Search for any image files containing 'dog' or in assets/reference or scratch
matches = glob.glob("assets/**/*dog*", recursive=True) + glob.glob("scratch/**/*dog*", recursive=True) + glob.glob("assets/**/scene-01*.png", recursive=True)
for m in set(matches):
    print(m)

