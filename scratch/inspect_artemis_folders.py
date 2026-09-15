import glob

print("Checking assets/artemis_reel/raw/:")
for p in glob.glob("assets/artemis_reel/raw/*"):
    print(p)

print("Checking scratch for any lunar or gateway files:")
for p in glob.glob("scratch/*lunar*") + glob.glob("scratch/*gateway*") + glob.glob("scratch/*artemis*"):
    print(p)
