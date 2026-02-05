from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from backend.core.agent_ocr import parse_resume
from backend.core.llm_brain import (
    generate_questions,
    evaluate_answer,
    generate_final_report
)
from backend.services.stt_service import transcribe_audio
from backend.services.tts_service import synthesize_speech
from backend.models.interview import InterviewState

# -------------------------------------------------
# App Initialization
# -------------------------------------------------
app = FastAPI(
    title="Intervux-AI v1.0",
    description="Voice-first AI interview system (v1.0)",
    version="1.0.0"
)

# -------------------------------------------------
# Global Session (v1.0 = single session only)
# -------------------------------------------------
SESSION = InterviewState()

# -------------------------------------------------
# Response Models
# -------------------------------------------------
class StartResponse(BaseModel):
    greeting_audio_url: str
    message: str


class QuestionResponse(BaseModel):
    question_text: str
    question_audio_url: str
    index: int


class AnswerResponse(BaseModel):
    transcript: str
    evaluation: dict


class FinalReportResponse(BaseModel):
    report: dict


# -------------------------------------------------
# 1️⃣ Start Interview (Voice Greeting)
# -------------------------------------------------
@app.post("/start", response_model=StartResponse)
def start_interview():
    """
    Initializes a new interview session and returns
    a voice-based greeting.
    """
    greeting_text = (
        "Hello, welcome to Intervux AI. "
        "I will be your interviewer today. "
        "This interview will include a short introduction, "
        "technical questions, and feedback at the end. "
        "Please upload your resume to begin."
    )

    audio_url = synthesize_speech(greeting_text)
    SESSION.reset()

    return StartResponse(
        greeting_audio_url=audio_url,
        message="Interview session initialized"
    )


# -------------------------------------------------
# 2️⃣ Resume Upload & Parsing
# -------------------------------------------------
@app.post("/upload-resume")
def upload_resume(file: UploadFile = File(...)):
    """
    Uploads and parses candidate resume.
    """
    resume_text, extracted_profile = parse_resume(file)

    SESSION.resume_text = resume_text
    SESSION.profile = extracted_profile

    return {
        "status": "resume_parsed",
        "profile_summary": extracted_profile
    }


# -------------------------------------------------
# 3️⃣ Generate Interview Questions (Frozen Count)
# -------------------------------------------------
@app.post("/generate-questions")
def generate_interview_questions():
    """
    Generates a fixed number of interview questions
    based on the parsed resume.
    """
    if not SESSION.profile:
        raise HTTPException(
            status_code=400,
            detail="Resume not uploaded"
        )

    questions = generate_questions(
        profile=SESSION.profile,
        num_questions=4  # 🔒 FROZEN FOR v1.0
    )

    SESSION.questions = questions
    SESSION.current_index = 0

    return {
        "total_questions": len(questions)
    }


# -------------------------------------------------
# 4️⃣ Ask Current Question (Voice Output)
# -------------------------------------------------
@app.get("/question", response_model=QuestionResponse)
def get_current_question():
    """
    Returns the current interview question
    along with synthesized speech.
    """
    idx = SESSION.current_index

    if idx >= len(SESSION.questions):
        raise HTTPException(
            status_code=400,
            detail="No more questions"
        )

    question_text = SESSION.questions[idx]
    audio_url = synthesize_speech(question_text)

    return QuestionResponse(
        question_text=question_text,
        question_audio_url=audio_url,
        index=idx
    )


# -------------------------------------------------
# 5️⃣ Submit Answer (Voice → STT → Evaluation)
# -------------------------------------------------
@app.post("/answer", response_model=AnswerResponse)
def submit_answer(audio: UploadFile = File(...)):
    """
    Accepts a spoken answer, transcribes it,
    evaluates the response, and advances the session.
    """
    if SESSION.current_index >= len(SESSION.questions):
        raise HTTPException(
            status_code=400,
            detail="Interview already completed"
        )

    if not audio:
        raise HTTPException(
            status_code=400,
            detail="Audio input required"
        )

    transcript = transcribe_audio(audio)

    evaluation = evaluate_answer(
        question=SESSION.questions[SESSION.current_index],
        answer=transcript,
        profile=SESSION.profile
    )

    SESSION.answers.append({
        "question": SESSION.questions[SESSION.current_index],
        "answer": transcript,
        "evaluation": evaluation
    })

    SESSION.current_index += 1

    return AnswerResponse(
        transcript=transcript,
        evaluation=evaluation
    )


# -------------------------------------------------
# 6️⃣ Final Interview Report
# -------------------------------------------------
@app.get("/final-report", response_model=FinalReportResponse)
def final_report():
    """
    Generates a structured interview report
    after all questions are answered.
    """
    if not SESSION.answers:
        raise HTTPException(
            status_code=400,
            detail="No answers submitted"
        )

    report = generate_final_report(
        profile=SESSION.profile,
        answers=SESSION.answers
    )

    return FinalReportResponse(report=report)
