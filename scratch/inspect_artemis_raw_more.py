import glob, os

print("Files in assets/artemis_reel/:")
for p in sorted(glob.glob("assets/artemis_reel/**/*", recursive=True)):
    print(p)
