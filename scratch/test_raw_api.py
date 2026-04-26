import os
import urllib.request
import json
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the correct location
load_dotenv('backend/.env')
api_key = os.getenv('GOOGLE_API_KEY')
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'
data = json.dumps({'contents': [{'parts': [{'text': 'test'}]}]}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

print(f"Testing Gemini API with key: {api_key[:5]}...")

try:
    res = urllib.request.urlopen(req)
    response_body = res.read().decode()
    print(f"SUCCESS: {response_body[:200]}")
except urllib.error.HTTPError as e:
    print(f"FAILED (HTTPError): {e.code} {e.reason}")
    print(f"Details: {e.read().decode()}")
except Exception as e:
    print(f"FAILED (Exception): {e}")
