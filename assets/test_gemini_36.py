import os, requests
api_key = None
with open(".env") as f:
    for line in f:
        if "GEMINI_API_KEY" in line:
            api_key = line.split(":", 1)[1].strip().strip("\"").strip("\x27")
            break

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
data = {
    "contents": [{"parts": [{"text": "Can you generate images directly? Answer yes or no."}]}]
}
r = requests.post(url, json=data, headers={"Content-Type": "application/json"})
print("gemini-3.6-flash status:", r.status_code)
if r.status_code == 200:
    print(r.json()["candidates"][0]["content"]["parts"][0]["text"])
else:
    print(r.text[:200])
