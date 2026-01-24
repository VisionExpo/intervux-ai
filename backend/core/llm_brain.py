import os
import yaml
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class InterviewerAI:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.chat_session = None

    def _load_prompts(self):
        """Helper to load the YAML config"""
        # Build path relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))  # backend/core
        yaml_path = os.path.join(base_dir, "..", "config", "prompts.yaml")

        try:
            with open(yaml_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"prompts.yaml not found at {yaml_path}")
        
    def start_session(self, resume_data, job_role="AI Engineer"):
         # 1. Get the templete from YAML
         raw_prompt = self.prompts["system_prompts"]["interviewer"]

         # 2. Fill in the placeholders (Dynamic Injection)
         system_prompt = raw_prompt.format(
              job_role=job_role,
              name=resume_data.get('name','Candidate'),
              skills = ', '.join(resume_data.get('skills', [])),
              projects = str(resume_data.get('projects', []))
         )

         # 3. Start Chat

         self.chat_session = self.model.start_chat(
             history=[
                 {"role": "user", "parts": [system_prompt]},
                 {"role": "model", "parts": ["Understood. I am ready."]}
             ]
         )

         response = self.chat_session.send_message("Start the interview.")
         return response.text
    
    def get_response(self, user_answer):
        if not self.chat_session:
            return "Error: Session not started."
        response = self.chat_session.send_message(user_answer)
        return response.text    