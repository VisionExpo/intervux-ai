import os
import json
import tempfile
from typing import Tuple

import google.generativeai as genai
from dotenv import load_dotenv
from backend.config.prompt_loader import PromptManager
from fastapi import UploadFile

load_dotenv()


class ResumeParser:
    """
    Vision-based resume parser using Gemini VLM.
    """

    def __init__(self, model_name: str = "gemini-1.5-pro-latest"):
        # NOTE: Using the Gemini 1.5 Pro model.
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not set")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            model_name,
            generation_config={
                "response_mime_type": "application/json"
            }
        )

        self.prompt_manager = PromptManager()

    def parse(self, file_path: str) -> dict:
        """
        Parses a resume PDF/image into structured JSON.
        """
        print(f"[INFO] Uploading resume to Gemini: {file_path}")

        uploaded_file = genai.upload_file(file_path)

        try:
            prompt = self.prompt_manager.get("resume_parser")

            print("[INFO] Analyzing resume...")
            response = self.model.generate_content(
                [prompt, uploaded_file]
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
                genai.delete_file(uploaded_file.name)
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
