import glob

eso_files = glob.glob("scratch/**/*eso*", recursive=True) + glob.glob("assets/**/*eso*", recursive=True) + glob.glob("scratch/**/*vlt*", recursive=True)
for f in eso_files:
    print(f)
