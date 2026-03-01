import os
import time
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.utils.logger import get_logger
from backend.utils.metrics import metrics
from backend.core.agent_ocr import parse_resume
from backend.core.llm_brain import generate_questions, evaluate_answer, generate_final_report
from backend.services.stt_service import transcribe_audio
from backend.services.tts_service import synthesize_speech
from backend.models.interview import InterviewState, ResumeData

logger = get_logger(__name__)

app = FastAPI(
    title="Intervux-AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# -------------------------
# Static Setup
# -------------------------
STATIC_DIR = "/app/static" if os.path.exists("/app") else "backend/static"
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# -------------------------
# Global Session (v1 only)
# -------------------------
SESSION = InterviewState()

# -------------------------
# Middleware: Request Tracing
# -------------------------
@app.middleware("http")
async def add_observability(request: Request, call_next):
    session_id = request.headers.get("X-Session-ID", str(uuid.uuid4()))
    start = time.time()

    metrics.record_request()

    try:
        response = await call_next(request)
        return response
    except Exception as e:
        metrics.record_error()
        logger.exception("Unhandled exception", extra={
            "extra_data": {"session_id": session_id}
        })
        raise e
    finally:
        duration = round(time.time() - start, 3)
        metrics.record_latency("request_total", duration)

        logger.info(
            "Request processed",
            extra={
                "extra_data": {
                    "session_id": session_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration": duration
                }
            }
        )

# -------------------------
# Health Endpoint
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------
# Metrics Endpoint
# -------------------------
@app.get("/metrics")
def get_metrics():
    return metrics.snapshot()

# -------------------------
# Start Interview
# -------------------------
@app.post("/start")
def start_interview():
    SESSION.reset()

    greeting = "Welcome to Intervux AI. Please upload your resume."

    start = time.time()
    audio_url = synthesize_speech(greeting)
    metrics.record_latency("tts", time.time() - start)

    logger.info("Interview started")

    return {"audio_url": audio_url}

# -------------------------
# Upload Resume
# -------------------------
@app.post("/upload-resume")
def upload_resume(file: UploadFile = File(...)):
    start = time.time()

    resume_text, extracted = parse_resume(file)
    SESSION.profile = ResumeData(**extracted)

    metrics.record_latency("resume_parsing", time.time() - start)

    logger.info("Resume parsed", extra={
        "extra_data": {
            "skills_count": len(SESSION.profile.skills)
        }
    })

    return {"status": "resume_parsed"}

# -------------------------
# Generate Questions
# -------------------------
@app.post("/generate-questions")
def generate_interview_questions():
    if not SESSION.profile:
        raise HTTPException(400, "Resume not uploaded")

    start = time.time()

    questions = generate_questions(
        profile=SESSION.profile.model_dump(),
        num_questions=4
    )

    metrics.record_latency("question_generation", time.time() - start)

    SESSION.questions = questions
    SESSION.current_index = 0

    return {"total_questions": len(questions)}

# -------------------------
# Get Current Question
# -------------------------
@app.get("/question")
def get_current_question():
    if not SESSION.questions:
        raise HTTPException(400, "Questions not generated")

    if SESSION.current_index >= len(SESSION.questions):
        raise HTTPException(400, "Interview completed")

    question_text = SESSION.questions[SESSION.current_index]

    start_tts = time.time()
    question_audio_url = synthesize_speech(question_text)
    metrics.record_latency("tts", time.time() - start_tts)

    return {
        "question_index": SESSION.current_index,
        "question_text": question_text,
        "question_audio_url": question_audio_url
    }

# -------------------------
# Submit Answer
# -------------------------
@app.post("/answer")
def submit_answer(audio: UploadFile = File(...)):
    if SESSION.current_index >= len(SESSION.questions):
        raise HTTPException(400, "Interview completed")

    start_stt = time.time()
    transcript = transcribe_audio(audio)
    metrics.record_latency("stt", time.time() - start_stt)

    start_eval = time.time()
    evaluation = evaluate_answer(
        question=SESSION.questions[SESSION.current_index],
        answer=transcript,
        profile=SESSION.profile.model_dump()
    )
    metrics.record_latency("evaluation", time.time() - start_eval)

    SESSION.answers.append({
        "question": SESSION.questions[SESSION.current_index],
        "answer": transcript,
        "evaluation": evaluation
    })

    SESSION.current_index += 1

    logger.info("Answer evaluated", extra={
        "extra_data": {
            "question_index": SESSION.current_index,
            "transcript_length": len(transcript)
        }
    })

    return {
        "transcript": transcript,
        "evaluation": evaluation
    }

# -------------------------
# Final Report
# -------------------------
@app.get("/final-report")
def final_report():
    if SESSION.current_index < len(SESSION.questions):
        raise HTTPException(400, "Interview not completed")

    start = time.time()
    report = generate_final_report(
        profile=SESSION.profile.model_dump(),
        answers=SESSION.answers
    )
    metrics.record_latency("final_report", time.time() - start)

    metrics.record_interview_completed()

    logger.info("Interview completed")

    return {"report": report}
