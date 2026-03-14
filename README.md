# Intervux AI 🚀

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue?style=flat-square)
![Status](https://img.shields.io/badge/status-active-success?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square) <br />
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square&logo=react&logoColor=black)
![Three.js](https://img.shields.io/badge/3D-Three.js-black?style=flat-square&logo=three.js&logoColor=white)
![Gemini](https://img.shields.io/badge/AI-Gemini-4285F4?style=flat-square&logo=google&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)
![CI](https://github.com/YourUsername/intervux-ai/actions/workflows/tests.yml/badge.svg)

</div>

<div align="center">
  <h3>The AI Interview Runtime and Recruiter Intelligence Platform</h3>
  <p>
    <strong>Intervux AI</strong> runs resume-aware interviews, evaluates answers, tracks model experiments, and provides recruiter decision support.
  </p>
</div>

---

# The Problem 💼

Hiring and interview preparation workflows today are still:

* ⚡️ **Static & unrealistic** - weak simulation of real interview pressure
* 📝 **Text-only** - missing multimodal signals
* 📊 **Hard to compare** - inconsistent evaluation across candidates

Modern hiring requires **structured evaluation, adaptive questioning, and reliable analytics**.

---

# The Solution: Intervux AI 💡

Intervux introduces a **real-time AI interview runtime combined with recruiter intelligence tools**.

1. 🧠 **Context Awareness**

Resume parsing builds interview context and skill profiles.

2. 🎯 **Adaptive Interview Engine**

Dynamic questioning adjusts based on candidate responses.

3. 📈 **Evaluation Pipeline**

Answers are scored using structured evaluation signals.

4. 📋 **Recruiter Intelligence**

Dashboards provide experiment tracking, analytics, and decision support.

---

# Core Features ✨

| Feature                     | Description                                                               |
| :-------------------------- | :------------------------------------------------------------------------ |
| 🔐 **Auth + RBAC**          | JWT authentication with role protection (`admin`, `recruiter`, `viewer`). |
| 🎤 **Interview Runtime**    | Real-time WebSocket interview sessions with adaptive questioning.         |
| 🤖 **Decision Support**     | `/api/interview/{id}/decision` generates recruiter recommendations.       |
| 📊 **Evaluation Dashboard** | Aggregated performance, cost, quality, and health metrics.                |
| 🧪 **Experiment Tracking**  | Compare prompt templates, models, and evaluation outcomes.                |
| 👁️ **Observability**        | Latency, throughput, token usage, and cost tracking.                      |
| ✅ **Testing + CI**         | Pytest suite with GitHub Actions automation.                              |

---

# System Architecture 🏗️

## High-Level System Flow

```mermaid
flowchart TD
    User[Candidate User] -->|UI + Audio| Frontend[React Frontend]
    Frontend -->|HTTP / WebSocket| Backend[FastAPI Backend]
    Backend -->|LLM Tasks| Provider[LLM Provider]
    Backend -->|ORM Queries| PostgreSQL[(PostgreSQL)]
    Backend -->|Metrics + Reports| Dashboard[Recruiter Dashboard]
```

---

## Core Platform Architecture

```mermaid
flowchart LR
    Candidate[Candidate Browser] --> UI[React + Avatar UI]

    UI -->|WebSocket| InterviewRuntime[Interview Runtime]
    UI -->|REST API| API[FastAPI Gateway]

    API --> Auth[Auth Layer<br/>JWT + RBAC]
    API --> Experiments[Experiment Service]
    API --> Metrics[Telemetry Service]

    InterviewRuntime --> LLM[LLM Provider]
    InterviewRuntime --> STT[Speech-to-Text]
    InterviewRuntime --> TTS[Text-to-Speech]

    API --> DB[(PostgreSQL Database)]

    Metrics --> Dashboard[Recruiter Dashboard]
    Experiments --> Dashboard
```

---

# Production Architecture 🌍

The production architecture introduces asynchronous workers, telemetry, and scalable inference.

```mermaid
flowchart LR

subgraph Client
    Candidate[Candidate Browser]
    Recruiter[Recruiter Dashboard]
end

subgraph Edge
    CDN[CDN / Static Hosting]
    Gateway[API Gateway]
end

subgraph Backend
    API[FastAPI Services]
    Auth[Auth Service<br/>JWT + RBAC]
end

subgraph Workers
    Queue[(Redis Task Queue)]
    EvalWorker[Evaluation Worker]
    ReportWorker[Report Generator]
end

subgraph AI
    STT[Speech-to-Text]
    LLM[LLM Provider]
    TTS[Text-to-Speech]
end

subgraph Data
    DB[(PostgreSQL)]
    Cache[(Redis Cache)]
end

subgraph Observability
    Metrics[Telemetry + Metrics]
    Alerts[Alerting System]
end

Candidate --> CDN
Recruiter --> CDN

CDN --> API
API --> Auth
API --> DB
API --> Cache

API --> Queue
Queue --> EvalWorker
Queue --> ReportWorker

EvalWorker --> STT
EvalWorker --> LLM
EvalWorker --> TTS

EvalWorker --> DB
ReportWorker --> DB

API --> Metrics
Metrics --> Alerts
```

---

# API Interaction Loop 🔄

```mermaid
sequenceDiagram
    participant U as Candidate
    participant FE as React Frontend
    participant BE as FastAPI Backend
    participant DB as PostgreSQL
    participant LLM as LLM Provider

    U->>FE: Resume upload + interview interaction
    FE->>BE: REST / WebSocket request
    BE->>LLM: Evaluation / summary tasks
    BE->>DB: Persist interview results
    BE-->>FE: Scores, reports, analytics
```

---

# Interview Evaluation Pipeline 📥

```mermaid
flowchart LR
    Resume --> Parser[Resume Parser]
    Parser --> Context[Candidate Context Builder]

    Context --> QuestionEngine[Adaptive Question Engine]

    QuestionEngine --> InterviewRuntime

    InterviewRuntime --> STT
    STT --> Transcript

    Transcript --> Evaluation[Evaluation Engine]

    Evaluation --> TechnicalScore
    Evaluation --> BehavioralScore
    Evaluation --> ReasoningScore

    TechnicalScore --> FinalScore
    BehavioralScore --> FinalScore
    ReasoningScore --> FinalScore

    FinalScore --> Report[Recruiter Report]
```

---

# Tech Stack 🛠️

## Frontend

| Technology         | Purpose                  |
| ------------------ | ------------------------ |
| React + TypeScript | Interview UI             |
| Three.js / R3F     | Avatar rendering         |
| WebSockets         | Real-time interview flow |

---

## Backend

| Technology  | Purpose       |
| ----------- | ------------- |
| FastAPI     | API server    |
| SQLAlchemy  | ORM           |
| Pydantic v2 | Validation    |
| Alembic     | DB migrations |

---

## AI & Speech

| Component     | Role                 |
| ------------- | -------------------- |
| Gemini        | LLM reasoning        |
| Whisper / STT | Speech transcription |
| Azure TTS     | Avatar speech        |

---

# Getting Started 🏁

## Prerequisites

* 🐍 Python 3.10+
* 📦 Node.js 18+
* 🗄️ PostgreSQL
* 🔑 LLM API key

---

## Clone the Repository

```bash
git clone https://github.com/YourUsername/intervux-ai.git
cd intervux-ai
```

---

## Backend Setup

```powershell
python -m venv myenv
.\myenv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`

```env
GOOGLE_API_KEY=your_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/intervux
LLM_PROVIDER=gemini
```

Run backend

```powershell
uvicorn backend.main:app --reload
```

---

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

---

## Docker 🐳

```bash
docker-compose up --build
```

---

# Authentication 🔒

Login endpoint

```
POST /api/auth/login/json
```

Demo users

```
admin@intervux.ai / admin123
recruiter@intervux.ai / recruiter123
viewer@intervux.ai / viewer123
```

Header

```
Authorization: Bearer <access_token>
```

---

# Example API Usage 💻

Create experiment

```bash
curl -X POST http://localhost:8000/api/experiments \
-H "Authorization: Bearer <token>" \
-H "Content-Type: application/json" \
-d '{
  "experiment_name": "prompt_experiment",
  "model_version": "gemini",
  "prompt_template": "Explain {topic}"
}'
```

---

# Project Structure 📁

```text
intervux-ai/                    # Repository root
|- backend/                     # FastAPI backend runtime
|  |- main.py                   # App entrypoint + route wiring
|  |- auth/                     # JWT, RBAC, auth routes
|  |- background/               # Async/background task orchestration
|  |- core/                     # Interview engine + LLM logic
|  |- db/                       # SQLAlchemy engine/session/base
|  |- middleware/               # Rate limiter and HTTP middleware
|  |- models/                   # Pydantic and domain models
|  |- scripts/                  # Seed/utility scripts
|  |- services/                 # Decision, telemetry, dashboard services
|  |- sockets/                  # WebSocket interview/metrics handlers
|  |- static/                   # Static/audio artifacts
|  `- utils/                    # Logging and runtime helpers
|- frontend/                    # React client app
|- tests/                       # Pytest suite and fixtures
|- alembic/                     # Database migrations
|- docs/                        # Project docs
|- evaluation/                  # Evaluation assets/reports
|- logs/                        # Runtime/research logs
|- .github/workflows/           # CI workflows
|- docker-compose.yaml          # Local orchestration
|- Dockerfile                   # Container build file
|- requirements.txt             # Python dependencies
`- README.md                    # Project overview
```

---

# Testing 🧪

Run the full suite

```powershell
pytest -q
```

Useful commands

```powershell
pytest -x
pytest -vv
pytest --cov=backend
```

CI runs automatically on push via:

```
.github/workflows/tests.yml
```

---

# Observability 📊

Intervux tracks system metrics including:

* ⏱️ request latency
* 🪙 token usage
* 💰 cost estimation
* 🚀 throughput
* ❌ error rate

These metrics power the **evaluation dashboard and alerting system**.

---

# Advanced System Diagrams 📐

## 1) LLM Evaluation Pipeline (Detailed)

```mermaid
flowchart TD
    A[Question + Candidate Answer] --> B[Preprocessing Layer]
    B --> C[Prompt Builder]
    C --> D[Primary Evaluator LLM]
    D --> E[Structured Scores JSON]
    E --> F[Consistency / Sanity Checks]
    F --> G[Critique Pass LLM]
    G --> H[Final Evaluation]
    H --> I[Normalization + Session Calibration]
    I --> J[Decision Support Report]
    J --> K[Recruiter Dashboard + APIs]
```

---

## 2) Telemetry + Metrics Architecture

```mermaid
flowchart LR
    API[FastAPI Routes] --> M1[In-Memory Metrics]
    WS[WebSocket Runtime] --> M1
    Eval[Evaluation Service] --> T1[Telemetry Service]

    T1 --> J1[JSONL Logs]
    T1 --> DB1[(llm_metrics Table)]

    M1 --> SNAP[Metrics Snapshot]
    SNAP --> WSM["WS metrics stream (/ws/metrics)"]
    SNAP --> DASH[Evaluation Dashboard API]

    DB1 --> AGG[Aggregates + Trends]
    J1 --> AGG
    AGG --> DASH
```

---

## 3) Experiment Tracking Architecture

```mermaid
flowchart TD
    UI[Recruiter / Admin UI] --> E1[POST /api/experiments]
    UI --> E2[POST /api/experiments/compare]
    UI --> E3[GET /api/experiments]

    E1 --> V1[Pydantic Validation]
    E2 --> V2[Pydantic Validation]

    V1 --> S1[Experiment Service]
    V2 --> S1
    E3 --> S1

    S1 --> DB[(experiments Table)]
    DB --> C1[Comparison Builder]
    C1 --> RESP[Structured Comparison Response]
```

---

# Roadmap 🗺️

* [x] ✅ Core interview + dashboard APIs
* [x] ✅ JWT auth + RBAC
* [x] ✅ Experiment tracking
* [x] ✅ Decision endpoint
* [x] ✅ Automated testing + CI
* [ ] ⏳ WebSocket integration tests
* [ ] ⏳ Load testing for interview runtime
* [ ] ⏳ Multi-model routing


# Contributing 🤝

Pull requests are welcome.

For major changes, please open an issue to discuss what you would like to improve.

---

# License 📄

Distributed under the MIT License.

---

<div align="center">
<sub>Built with ❤️ by Vishal Gorule</sub>
</div>


## Maintainer Quick Start

1. Copy .env.example to .env and fill secrets (GOOGLE_API_KEY, JWT_SECRET_KEY, DB credentials).
2. Start stack with docker compose up --build -d.
3. Verify GET /health, GET /ready, and Flower (http://localhost:5555).
4. Frontend dev server: 
pm --prefix frontend install && npm --prefix frontend run dev.
5. Run backend checks: py -3 -m compileall backend and pytest -q.

See also: SYSTEM_FLOW.md and ARCHITECTURE.md.
