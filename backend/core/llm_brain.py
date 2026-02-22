import os
import json
import time
from typing import Dict, List

from google import genai
from dotenv import load_dotenv

from backend.utils.logger import get_logger
from backend.utils.metrics import metrics

load_dotenv()

logger = get_logger(__name__)

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not set")

MODEL_NAME = "gemini-2.5-flash"
client = genai.Client(api_key=API_KEY)


# ---------------------------------------------------------
# Question Generation
# ---------------------------------------------------------

def generate_questions(profile: dict, num_questions: int) -> List[str]:
    start = time.time()

    prompt = f"""
    You are an expert AI interviewer. Based on the following candidate profile, 
    generate exactly {num_questions} technical interview questions.
    Return the questions as a JSON list of strings.

    Candidate Profile:
    {json.dumps(profile, indent=2)}
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.7
            }
        )

        questions = json.loads(response.text)

        duration = round(time.time() - start, 3)
        metrics.record_latency("llm_question_generation", duration)

        logger.info(
            "Questions generated",
            extra={
                "extra_data": {
                    "num_questions": len(questions),
                    "duration": duration
                }
            }
        )

        return questions

    except Exception:
        metrics.record_error()
        logger.exception("Question generation failed")
        return [
            "Tell me about a challenging project you worked on.",
            "What are your strongest technical skills?",
            "How do you stay up-to-date with new technologies?",
            "Where do you see yourself in 5 years?",
        ]


# ---------------------------------------------------------
# Answer Evaluation
# ---------------------------------------------------------

def evaluate_answer(question: str, answer: str, profile: dict) -> dict:
    start = time.time()

    prompt = f"""
    You are an expert AI interviewer evaluating a candidate's answer.
    Score 0-10 on four dimensions:
    - Technical Accuracy
    - Clarity of Explanation
    - Depth of Understanding
    - Confidence & Communication

    Return JSON:
    {{
      "scores": {{ ... }},
      "feedback": [...],
      "summary": "..."
    }}

    Candidate Profile:
    {json.dumps(profile, indent=2)}

    Question:
    "{question}"

    Answer:
    "{answer}"
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.3
            }
        )

        evaluation = json.loads(response.text)

        # Clamp scores 0–10
        if "scores" in evaluation:
            for k, v in evaluation["scores"].items():
                evaluation["scores"][k] = max(0, min(10, int(v)))

        duration = round(time.time() - start, 3)
        metrics.record_latency("llm_evaluation", duration)

        logger.info(
            "Answer evaluated",
            extra={
                "extra_data": {
                    "duration": duration,
                    "scores": evaluation.get("scores", {}),
                    "answer_length": len(answer)
                }
            }
        )

        return evaluation

    except Exception:
        metrics.record_error()
        logger.exception("Evaluation failed")
        return {
            "scores": {
                "Technical Accuracy": 5,
                "Clarity of Explanation": 5,
                "Depth of Understanding": 5,
                "Confidence & Communication": 5,
            },
            "feedback": ["Evaluation fallback triggered."],
            "summary": "AI evaluation failed."
        }


# ---------------------------------------------------------
# Final Report
# ---------------------------------------------------------

def generate_final_report(profile: dict, answers: List[dict]) -> dict:
    start = time.time()

    prompt = f"""
    You are a hiring manager writing a final report.
    Provide:
    - Overall Recommendation
    - Strengths
    - Weaknesses
    - Final Summary

    Return JSON.

    Candidate Profile:
    {json.dumps(profile, indent=2)}

    Q&A:
    {json.dumps(answers, indent=2)}
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.4
            }
        )

        report = json.loads(response.text)

        duration = round(time.time() - start, 3)
        metrics.record_latency("llm_final_report", duration)

        logger.info(
            "Final report generated",
            extra={
                "extra_data": {
                    "duration": duration,
                    "num_answers": len(answers)
                }
            }
        )

        return report

    except Exception:
        metrics.record_error()
        logger.exception("Final report generation failed")
        return {"error": "Failed to generate report."}