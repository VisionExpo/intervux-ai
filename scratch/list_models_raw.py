import os
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('GOOGLE_API_KEY')

# Try to list models
url = f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}'
req = urllib.request.Request(url)

print(f"Listing models with key: {api_key[:5]}...")

try:
    res = urllib.request.urlopen(req)
    models = json.loads(res.read().decode())
    print("Available Models:")
    for m in models.get('models', []):
        print(f"- {m['name']}")
except Exception as e:
    print(f"FAILED to list models: {e}")
    if hasattr(e, 'read'):
        print(f"Details: {e.read().decode()}")
