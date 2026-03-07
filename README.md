# 🎙️ Intervux AI

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue?style=flat-square)
![Status](https://img.shields.io/badge/status-active-success?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
<br />
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square&logo=react&logoColor=black)
![Three.js](https://img.shields.io/badge/3D-Three.js-black?style=flat-square&logo=three.js&logoColor=white)
![Gemini](https://img.shields.io/badge/AI-Gemini-4285F4?style=flat-square&logo=google&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)

</div>

<div align="center">
  <h3>The AI Interview and Evaluation Platform</h3>
  <p>
    <strong>Intervux AI</strong> runs resume-aware interviews, evaluates answers, tracks model experiments, and provides recruiter decision support.
  </p>
</div>

---

## 🧠 The Problem
Hiring and interview prep workflows are still:
* **Static & unrealistic:** weak simulation of real interview pressure.
* **Text-only:** limited signal beyond plain Q&A.
* **Hard to compare:** poor experiment tracking and reporting consistency.

**Real interview evaluation is multimodal, iterative, and data-driven.**

## 💡 The Solution: Intervux AI
Intervux is a practical **interview runtime + recruiter intelligence** stack:

1. 👁️ **It Sees Context:** Parses resume data and builds interview context.
2. 🎧 **It Runs Interviews:** Real-time WebSocket interview flow with adaptive questioning.
3. 💻 **It Evaluates:** Structured answer scoring and report generation.
4. 📊 **It Supports Recruiters:** Dashboard metrics, experiment tracking, and decision reports.

---

> **Note on current version:** The project includes REST + WebSocket runtime, auth/RBAC, dashboard APIs, experiment APIs, and a dedicated pytest suite with CI.

## ✨ Core Features

| Feature | Description |
| :--- | :--- |
| **🔐 Auth + RBAC** | JWT auth with role-protected routes (`admin`, `recruiter`, `viewer`). |
| **🗣️ Interview Runtime** | Resume-aware question flow and answer evaluation over WebSockets. |
| **🧾 Decision Endpoint** | `POST /api/interview/{interview_id}/decision` for recruiter-facing summaries/recommendations. |
| **📈 Evaluation Dashboard** | Aggregated performance, quality, cost, and system health APIs. |
| **🧪 Experiment Tracking** | Validated create/compare experiment endpoints. |
| **✅ Testing + CI** | `tests/` suite + GitHub Actions workflow. |

---

## 🧩 System Architecture

### High-Level Flow
```mermaid
flowchart TD
    User -->|UI + Audio| Frontend
    Frontend -->|HTTP/WebSocket| Backend
    Backend -->|LLM Tasks| Provider
    Backend -->|ORM| PostgreSQL
    Backend -->|Metrics + Reports| Recruiter Dashboard
```

### API Interaction Loop
```mermaid
sequenceDiagram
    participant U as User
    participant FE as React Frontend
    participant BE as FastAPI Backend
    participant DB as PostgreSQL
    participant LLM as LLM Provider

    U->>FE: Resume + Interview interaction
    FE->>BE: REST / WebSocket requests
    BE->>LLM: Evaluation / summary tasks
    BE->>DB: Persist interview + experiment data
    BE-->>FE: Scores, reports, metrics
```

---

## 🛠️ Tech Stack

### Frontend (Client)
* **Framework:** React + TypeScript (Vite)
* **3D:** Three.js / React Three Fiber
* **Comms:** WebSockets

### Backend (Server)
* **Framework:** FastAPI (Python 3.10+)
* **DB Layer:** SQLAlchemy
* **Validation:** Pydantic v2
* **Lifecycle:** FastAPI lifespan handlers

### AI & Logic
* **Provider:** Gemini / local fallback (env configurable)
* **Pipelines:** STT / evaluation / reporting

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* Node.js 18+
* PostgreSQL
* API key for configured LLM provider

### 1. Clone the Repository
```bash
git clone https://github.com/YourUsername/intervux-ai.git
cd intervux-ai
```

### 2. Backend Setup
```powershell
python -m venv myenv
.\myenv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:
```env
GOOGLE_API_KEY=your_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/intervux
LLM_PROVIDER=gemini
```

Run backend:
```powershell
uvicorn backend.main:app --reload
```

### 3. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```

### 4. Docker (Optional)
```bash
docker-compose up --build
```

---

## 🔐 Authentication

Use:
* `POST /api/auth/login/json`

Demo users:
* `admin@intervux.ai` / `admin123`
* `recruiter@intervux.ai` / `recruiter123`
* `viewer@intervux.ai` / `viewer123`

Header format:
```http
Authorization: Bearer <access_token>
```

---

## 📁 Project Structure

```text
intervux-ai/
├── backend/                # FastAPI backend
│   ├── main.py             # App entrypoint + routes
│   ├── auth/               # JWT, RBAC, auth routes
│   ├── services/           # Decision, telemetry, dashboard services
│   ├── sockets/            # Interview + metrics WebSocket handlers
│   ├── models/             # Pydantic + ORM-related models
│   ├── middleware/         # Rate limiter and HTTP middleware
│   └── db/                 # SQLAlchemy setup
├── frontend/               # React app
├── tests/                  # Pytest suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_experiments.py
│   ├── test_decision.py
│   ├── test_metrics.py
│   └── test_health.py
├── .github/workflows/
│   └── tests.yml           # CI test workflow
├── docker-compose.yaml
└── README.md
```

---

## ✅ Testing

Run full suite:
```powershell
pytest -q
```

Useful commands:
```powershell
pytest -x
pytest -vv
pytest --cov=backend
```

CI runs on push/PR via:
* `.github/workflows/tests.yml`

---

## 🛣️ Roadmap

* [x] Core interview + dashboard APIs
* [x] Auth + RBAC route protection
* [x] Validated experiment create/compare payloads
* [x] Decision endpoint schema normalization
* [x] Dedicated pytest suite + CI
* [ ] Broader WebSocket integration tests
* [ ] Extended rate-limit and revocation test coverage

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

<div align="center">
<sub>Built with ❤️ by Vishal Gorule</sub>
</div>
