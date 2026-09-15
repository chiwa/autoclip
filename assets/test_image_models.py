import os, requests
api_key = None
with open(".env") as f:
    for line in f:
        if "GEMINI_API_KEY" in line:
            api_key = line.split(":", 1)[1].strip().strip("\"").strip("\x27")
            break

models = [
    "gemini-3.1-flash-lite-image",
    "gemini-3-pro-image-preview",
    "gemini-3-pro-image",
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image"
]

data = {
    "contents": [{"parts": [{"text": "Generate an image of a galaxy"}]}]
}

for m in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
    r = requests.post(url, json=data, headers={"Content-Type": "application/json"})
    print(m, "=>", r.status_code)
    if r.status_code == 200:
        print("SUCCESS on", m)
        break
    else:
        print("   ", r.text[:120])
