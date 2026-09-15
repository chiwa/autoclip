import glob, os

print("Files in assets/artemis_ii_far_side_reel/:")
for p in sorted(glob.glob("assets/artemis_ii_far_side_reel/**/*", recursive=True)):
    print(p)
