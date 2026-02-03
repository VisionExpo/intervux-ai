import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from backend.config.prompt_loader import PromptManager

load_dotenv()


class ResumeParser:
    """
    Vision-based resume parser using Gemini VLM.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash"):
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
