import os
import json
from typing import Dict, List

import google.generativeai as genai
from dotenv import load_dotenv

# from backend.config.prompt_loader import PromptManager # NOTE: Using inline prompts for v1.0 simplicity

load_dotenv()


# --- v1.0 Simple Functions (as required by main.py) ---

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not set")
genai.configure(api_key=API_KEY)
# NOTE: Using the Gemini 1.5 Pro model.
MODEL = genai.GenerativeModel("gemini-1.5-pro-latest")


def generate_questions(profile: dict, num_questions: int) -> List[str]:
    """Generates interview questions based on a resume profile."""
    prompt = f"""
    You are an expert AI interviewer. Based on the following candidate profile, generate exactly {num_questions} technical interview questions.
    The questions should be relevant to the candidate's skills and project experience.
    Return the questions as a JSON list of strings.

    Candidate Profile:
    {json.dumps(profile, indent=2)}

    Example Output:
    ["Question 1", "Question 2", "Question 3", "Question 4"]
    """
    try:
        response = MODEL.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        questions = json.loads(response.text)
        return questions
    except (json.JSONDecodeError, Exception) as e:
        print(f"[ERROR] Failed to generate questions: {e}")
        # Fallback questions
        return [
            "Tell me about a challenging project you worked on.",
            "What are your strongest technical skills?",
            "How do you stay up-to-date with new technologies?",
            "Where do you see yourself in 5 years?",
        ]


def evaluate_answer(question: str, answer: str, profile: dict) -> dict:
    """Evaluates a candidate's answer to a question."""
    prompt = f"""
    You are an expert AI interviewer evaluating a candidate's answer.
    Use the provided rubric to score the answer from 0 to 10 on four dimensions.
    Provide a brief summary and bullet-point feedback.
    Return a JSON object with keys: "scores", "feedback", "summary".
    "scores" should be a dictionary mapping dimension to an integer score.
    "feedback" should be a list of strings.

    Rubric:
    - Technical Accuracy (0-10): Correctness of technical information.
    - Clarity of Explanation (0-10): How clearly the candidate explains concepts.
    - Depth of Understanding (0-10): How well the candidate demonstrates deep knowledge vs. surface-level.
    - Confidence & Communication (0-10): Overall communication style and confidence.

    Candidate Profile:
    {json.dumps(profile, indent=2)}

    Interview Question:
    "{question}"

    Candidate's Answer:
    "{answer}"
    """
    try:
        response = MODEL.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        evaluation = json.loads(response.text)
        return evaluation
    except (json.JSONDecodeError, Exception) as e:
        print(f"[ERROR] Failed to evaluate answer: {e}")
        # Fallback evaluation
        return {
            "scores": {"clarity": 5, "depth": 5},
            "feedback": ["Evaluation failed, providing default feedback."],
            "summary": "Could not process the evaluation via the AI model."
        }


def generate_final_report(profile: dict, answers: List[dict]) -> dict:
    """Generates a final interview report."""
    prompt = f"""
    You are an expert hiring manager. You have conducted an interview and now need to write a final report.
    Summarize the candidate's performance based on their profile and their answers/evaluations.
    Provide an overall recommendation (e.g., "Strong Hire", "Hire", "No Hire") and a summary of strengths and weaknesses.
    Return a JSON object.

    Candidate Profile:
    {json.dumps(profile, indent=2)}

    Interview Q&A and Evaluations:
    {json.dumps(answers, indent=2)}
    """
    try:
        response = MODEL.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        report = json.loads(response.text)
        return report
    except (json.JSONDecodeError, Exception) as e:
        print(f"[ERROR] Failed to generate final report: {e}")
        return {"error": "Failed to generate report."}


"""
# --- v2.0+ Class (Commented out for v1.0 as it's not used) ---
# The InterviewerAI class is designed for a more complex, multi-session architecture
# with features like chat history, which is beyond the scope of the stateless v1.0 API.
class InterviewerAI:
    ... (Code commented out for brevity)
"""
