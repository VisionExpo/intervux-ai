import os
import json
import base64
import tempfile
from typing import Tuple
from pathlib import Path

from google import genai
from dotenv import load_dotenv
from backend.config.prompt_loader import PromptManager
from fastapi import UploadFile

# Load .env from project root
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")


# --- Gemini Client Setup ---
# Lazy initialization - only create client when needed
MODEL_NAME = "gemini-2.5-flash"
_client = None


def get_gemini_client():
    """Lazy initialization of Gemini client."""
    global _client
    if _client is None:
        API_KEY = os.getenv("GOOGLE_API_KEY")
        if not API_KEY:
            raise RuntimeError("GOOGLE_API_KEY not set. Please add GOOGLE_API_KEY to your .env file.")
        _client = genai.Client(api_key=API_KEY)
    return _client


class ResumeParser:
    """
    Vision-based resume parser using Gemini VLM.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.prompt_manager = PromptManager()

    def parse(self, file_path: str) -> dict:
        """
        Parses a resume PDF/image into structured JSON.
        """
        client = get_gemini_client()
        
        print(f"[INFO] Uploading resume to Gemini: {file_path}")

        uploaded_file = client.files.upload(file=file_path)

        try:
            prompt = self.prompt_manager.get("resume_parser")

            print("[INFO] Analyzing resume...")
            response = client.models.generate_content(
                model=self.model_name,
                contents=[prompt, uploaded_file],
                config={"response_mime_type": "application/json"}
            )

            return json.loads(response.text)

        except json.JSONDecodeError:
            print("[WARN] Gemini returned invalid JSON")
            return {}

        except Exception as e:
            print(f"[ERROR] Resume parsing failed: {e}")
            return {}

        finally:
            # Cleanup uploaded artifact
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception:
                pass


def parse_resume(file: UploadFile) -> Tuple[str, dict]:
    """
    Wrapper function to handle UploadFile, parse it, and return data
    in the format expected by main.py.
    """
    parser = ResumeParser()

    # Save UploadFile to a temporary file to get a path
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(file.file.read())
        file_path = tmp.name

    try:
        profile_data = parser.parse(file_path)
        # main.py expects a tuple (resume_text, profile_dict).
        # The raw text isn't used in v1.0, so we return an empty string.
        return "", profile_data
    finally:
        # Clean up the local temporary file
        if os.path.exists(file_path):
            os.remove(file_path)


def parse_resume_bytes(file_name: str, file_bytes_b64: str) -> Tuple[str, dict]:
    """
    Parse a base64-encoded resume payload from WebSocket transport.
    """
    parser = ResumeParser()
    decoded = base64.b64decode(file_bytes_b64)

    suffix = os.path.splitext(file_name)[1] if file_name else ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(decoded)
        file_path = tmp.name

    try:
        profile_data = parser.parse(file_path)
        return "", profile_data
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
