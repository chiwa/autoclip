import os, requests
api_key = None
with open(".env") as f:
    for line in f:
        if "GEMINI_API_KEY" in line:
            api_key = line.split(":", 1)[1].strip().strip("\"").strip("\x27")
            break

# In Gemini API v1beta, image generation is typically Imagen 3:
# endpoint: https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict
# or https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002
# Let's list all models in the API:
r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
models = r.json().get("models", [])
for m in models:
    if "image" in m["name"].lower() or "imagen" in m["name"].lower() or "draw" in m["name"].lower():
        print(m["name"], m.get("supportedGenerationMethods"))
