import glob

print("WSB files:")
for p in sorted(glob.glob("assets/where_space_begins_reel*/**/*", recursive=True)):
    print(p)
