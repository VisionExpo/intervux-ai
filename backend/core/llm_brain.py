import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict
from backend.config.prompt_loader import PromptManager

load_dotenv()


class InterviewerAI:
    """
    Handles all LLM-driven interviewer logic.
    Session-safe and prompts-configurable.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

        self.prompt_manager = PromptManager()

        # session_id -> chat_session
        self.sessions: Dict[str, any] = {}


    # -------------------
    # Interview Flow
    # -------------------

    def start_session(
            self,
            session_id: str,
            resume_data: dict,
            job_role: str = "AI Engineer",
    ) -> str:
        """
        Starts a new interview session.
        """

        system_prompt = self.prompt_manager(
            "interviewer",
            job_role=job_role,
            name=resume_data.get("name", "Candidate"),
            skills=", ".join(resume_data.get("skills", [])),
            projects=", ".join(
                [p.get("title", "") for p in resume_data.get("projects", [])]
            ),    
        )

        chat = self.model.start_chat(
            history = [
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["Understood. I am ready."]},
            ]
        )

        self.sessions[session_id] = chat

        response = chat.send_message("Start the interview.")
        return response.text
    
    def get_respose(self, session_id: str, user_answer: str) -> str:
        """
        Comtinues an interview session.
        """

        chat = self.sessions.get(session_id)
        if not chat:
            return "Error: Interview session not found."
        
        response = chat.send_message(user_answer)
        return response.text
    
    # -----------------
    # Code Review
    # -----------------

    def review_code(
            self,
            problem_desc: str,
            code_snippet: str,
            execution_output: str,
    ) -> str:
        prompt = self.prompt_manager.get(
            "code_review",
            problem_description=problem_desc,
            code_snippet=code_snippet,
            execution_output=execution_output,
        )

        response = self.model.generate_content(prompt)
        return response.text 
    
    # -------------------
    # Problem Generator
    # -------------------

    def generate_problem(
        self,
        skills: str,
        difficulty: str = "Medium",
        topic: str = "Data Structures & Algorithms",
    ) -> str:
        prompt = self.prompt_manager.get(
            "problem_generator",
            skills=skills,
            topic=topic,
            difficulty=difficulty,
        )

        response = self.model.generate_content(prompt)

        # Clean Gemini formatting
        return (
            response.text.replace("```python", "")
            .replace("```", "")
            .strip()
        )