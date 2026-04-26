import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path

def test_gemini_access():
    # Load .env
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / ".env")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in .env")
        return

    model_id = "gemini-1.5-flash"
    client = genai.Client(api_key=api_key)
    
    try:
        print(f"Testing access to model: {model_id}...")
        response = client.models.generate_content(
            model=model_id,
            contents="Hello, are you working?"
        )
        print("SUCCESS: Connection established.")
        print(f"Response: {response.text.strip()}")
    except Exception as e:
        print(f"FAILED: Could not access {model_id}")
        print(f"Error Details: {e}")

if __name__ == "__main__":
    test_gemini_access()
