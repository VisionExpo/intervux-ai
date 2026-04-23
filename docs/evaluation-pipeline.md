# Evaluation Pipeline

The Evaluation Pipeline is the "Intellectual Layer" of Intervux AI. It transforms a raw interview transcript into a structured competency report.

## 🧠 Multi-Pass Evaluation Strategy
Simple keyword matching is insufficient for technical interviews. Intervux AI uses a **Multi-Pass Reasoning** approach:

### Pass 1: Reasoning Analysis
- **Goal**: Extract the "Signal from Noise."
- **Logic**: Filters out filler words and identifies the core technical claims made by the candidate.

### Pass 2: Competency Scoring
- **Goal**: Measure depth against a rubric.
- **Scoring**: Evaluates specific dimensions (e.g., System Design, Coding Logic, Communication) on a scale of 1-10.

### Pass 3: Consistency Check
- **Goal**: Detect contradictions.
- **Logic**: Compares answers across different questions. If a candidate claims expertise in "Redis" but fails a basic caching question later, the consistency score drops.

### Pass 4: Score Reconciliation
- **Goal**: Final mathematical normalization.
- **Formula**: `Final Score = (Avg(Competency) * 0.7) + (Consistency * 0.3)`.

## 🔗 Code Mapping

### Component: Evaluation Orchestrator
- **Files**: `backend/services/evaluation_service.py`.
- **What it does**: Triggers the evaluation after the session ends.
- **Why it exists**: To ensure evaluation runs asynchronously and doesn't block the WebSocket.
- **Connects to**: `LLMService` and `PostgreSQL`.

### Component: Evaluation Engine
- **Files**: `backend/core/evaluation_engine.py`.
- **What it does**: Contains the actual multi-pass LLM prompts and logic.
- **Why it exists**: The core "brain" that knows how to score technical depth.
- **Connects to**: `LLMService`.

## 🛡 Failure Handling & Robustness

### 1. LLM Fallback
If the primary LLM (Gemini) fails during evaluation, the system automatically falls back to a secondary provider (e.g., Qwen/Local LLM) to ensure the recruiter always gets a report.

### 2. Validation Failures
LLM outputs are validated against Pydantic schemas. If the LLM returns "Garbage JSON," the system uses a **Repair Pass** where it sends the error back to the LLM for correction before falling back to a "Safe Default" score.

## 📊 Observability Metrics
Recruiters can see not just the score, but the system's confidence:
- `evaluation_latency`: Time taken to generate the report.
- `validation_error_rate`: Tracks how often the LLM output needed repair.
- `consistency_alert`: Flagged if Pass 3 detects high variance in candidate expertise.
