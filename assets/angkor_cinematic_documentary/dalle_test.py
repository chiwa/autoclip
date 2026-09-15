import os
import requests
from openai import OpenAI

api_key = None
with open("/Users/zengcode/projects/autoclip/.env", "r") as f:
    for line in f:
        if "OPENAI_API_KEY:" in line:
            api_key = line.split("OPENAI_API_KEY:")[1].strip()

client = OpenAI(api_key=api_key)
try:
    response = client.images.generate(
        model="dall-e-2",
        prompt="A highly detailed cinematic shot of an ancient Southeast Asian temple at sunrise.",
        size="1024x1024",
        n=1,
    )
    url = response.data[0].url
    print(f"SUCCESS: {url[:50]}...")
except Exception as e:
    print(f"ERROR: {e}")
