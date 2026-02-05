import os
import requests
import json

UNBOUND_URL = "https://api.getunbound.ai/v1/chat/completions"
API_KEY = os.getenv("UNBOUND_API_KEY")

if not API_KEY:
    raise RuntimeError("UNBOUND_API_KEY not set")

def call_unbound(model: str, prompt: str) -> str:
    response = requests.post(
        UNBOUND_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "Connection": "close"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        },
        timeout=(10, 30)
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
