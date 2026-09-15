import glob, os

print("Files in assets/artemis_reel/ and assets/lunar_gateway_reel/:")
for p in glob.glob("assets/artemis_reel/**/*", recursive=True) + glob.glob("assets/lunar_gateway_reel/**/*", recursive=True):
    print(p)
