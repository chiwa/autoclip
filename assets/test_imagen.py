import requests

api_key = None
with open("/Users/zengcode/projects/autoclip/.env", "r") as f:
    for line in f:
        if "GEMINI_API_KEY:" in line:
            api_key = line.split("GEMINI_API_KEY:")[1].strip()

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image:generateImages?key={api_key}"
data = {
    "prompt": "A cinematic shot"
}
r = requests.post(url, headers={"Content-Type": "application/json"}, json=data)
print(r.status_code)
print(r.text[:200])
