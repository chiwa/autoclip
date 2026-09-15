import subprocess

# Let's search git history for iss_why_not_fall_reel scene-01-hook-base.png
out = subprocess.run(["git", "log", "--follow", "-p", "-n", "1", "assets/iss_why_not_fall_reel/images/scene-01-hook-base.png"], capture_output=True, text=True)
print("Git log header:", out.stdout[:500])

out2 = subprocess.run(["git", "log", "--follow", "-p", "-n", "1", "assets/voyager1_reel/images/scene-01-hook.png"], capture_output=True, text=True)
print("Git log voyager:", out2.stdout[:500])
