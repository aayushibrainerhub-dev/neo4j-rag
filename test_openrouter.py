import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

print(f"Testing OpenRouter integration...")
print(f"API Key: {api_key[:20]}...")
print(f"Model: {model}")
print()

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:8000",
    "X-Title": "Neo4j RAG System"
}

payload = {
    "model": model,
    "messages": [
        {
            "role": "user",
            "content": "Say 'Hello from OpenRouter!' if you can read this."
        }
    ],
    "max_tokens": 50
}

try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Success!")
        print(f"Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"✗ Error: {response.text}")
        
except Exception as e:
    print(f"✗ Exception: {e}")
