# Intervux AI 🚀

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue?style=flat-square)
![Status](https://img.shields.io/badge/status-active-success?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square) <br />
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square&logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)

</div>

<div align="center">
  <h3>The AI Interview Runtime and Recruiter Intelligence Platform</h3>
  <p>
    <strong>Intervux AI</strong> runs resume-aware interviews, evaluates answers, tracks model experiments, and provides recruiter decision support.
  </p>
</div>

---

# 📖 Overview

## The Problem 💼
Hiring and interview preparation workflows today are still:
* ⚡️ **Static & unrealistic** - weak simulation of real interview pressure and rigid Q&A scripts.
* 📝 **Text-only** - missing multimodal signals, speech cadence, and real-time stress testing.
* 📊 **Hard to compare** - inconsistent human evaluation across candidates due to inherent bias.

Modern hiring requires **structured evaluation, adaptive questioning, and reliable analytics**.

## The Solution: Intervux AI 💡
Intervux introduces a **real-time AI interview runtime combined with recruiter intelligence tools**.

1. 🧠 **Context Awareness:** Resume parsing builds deep interview context and skill profiles automatically.
2. 🎯 **Adaptive Interview Engine:** Dynamic questioning adjusts live based on candidate responses.
3. 📈 **Evaluation Pipeline:** Answers are scored using structured, unbiased evaluation signals.
4. 📋 **Recruiter Intelligence:** Dashboards provide experiment tracking, telemetry, and decision support algorithms.

---

# 📸 Demos & Live Action
* *(Placeholder)* **[Watch the Recruiter Dashboard Demo Video (YouTube) 🎥](#)**
* *(Placeholder)* **[Watch the Live Candidate Interview Runtime (YouTube) 🎥](#)**
* *(Placeholder)* **[Live Demo Application Link 🔗](#)**

---

# 📚 Detailed Documentation
If you are looking to understand the underlying system design, navigate to our `docs/` folder:
* 🏗️ **[System Architecture (ARCHITECTURE.md)](docs/ARCHITECTURE.md):** Deep dive into the backend services and React configurations.
* 🔄 **[System Flow (SYSTEM_FLOW.md)](docs/SYSTEM_FLOW.md):** The data flow pipelines (LLM interactions, Telemetry cycles).
* 📐 **[High-Level Design (HLD_Intervux_AI.docx)](docs/HLD_Intervux_AI.docx):** Broad platform layouts for enterprise evaluation.
* 🔧 **[Low-Level Design (LLD_Intervux_AI.docx)](docs/LLD_Intervux_AI.docx):** Component-level class diagrams and state logic.

---

# Requirements for Beginners 🏁

If you don't know much about building web applications natively—**Docker is the easiest and recommended way to run this application!** By using Docker, you bypass the need to install Python, Node, Postgres, or Redis manually on your computer.

All you need installed on your machine are:
1. **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**
2. **[Git](https://git-scm.com/)**

---

# ⚡ Quickstart (The Best Method)

### Step 1: Clone the Repository
```bash
git clone https://github.com/YourUsername/intervux-ai.git
cd intervux-ai
```

### Step 2: Configure Environment Variables
Inside the root folder, copy the example Docker variables into a new `.env.docker` file.
```bash
# Windows (PowerShell)
Copy-Item .env.docker.example .env.docker

# Mac / Linux
cp .env.docker.example .env.docker
```
Open `.env.docker` in your text editor and add your AI credentials (e.g., set `GOOGLE_API_KEY=your_gemini_api_key_here`). The rest of the settings are already perfectly configured for Docker!

### Step 3: Run the Application!
Open Docker Desktop, then run the build command in your terminal:
```bash
docker-compose up --build
```
*Note: The first time you run this, it may take 3-5 minutes to download Linux packages and build the databases.*

### Step 4: Access the Dashboard
Once the terminal logs calm down, the servers are running!
- **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
- **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Celery Task Monitor (Flower):** [http://localhost:5555](http://localhost:5555)

**Use these default credentials to log in to the Frontend Dashboard:**
| Role      | Email                    | Password      |
|-----------|--------------------------|---------------|
| Admin     | admin@intervux.ai        | admin123      |
| Recruiter | recruiter@intervux.ai    | recruiter123  |

---

# 💻 Manual Local Setup (Advanced)
*If you are actively developing code and want terminal-level debug control without running containers, follow these hybrid steps.*

### Prerequisites
* 🐍 Python 3.10+
* 📦 Node.js 18+
* 🗄️ PostgreSQL Database (Running locally)
* 🛑 Redis Server (Running locally)

### 1. Backend Setup
```powershell
python -m venv myenv
.\myenv\Scripts\activate
pip install -r backend/requirements.txt
```

*(Windows developers only: `pip install -r requirements/windows.txt`)*

Create a local `.env` copy and connect it to your local Postgres/Redis instances:
```env
GOOGLE_API_KEY=your_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/intervux
REDIS_URL=redis://localhost:6379/0
LLM_PROVIDER=gemini
```

Start the FastAPI backend:
```powershell
uvicorn backend.main:app --reload
```

### 2. Frontend Setup
In a new terminal:
```powershell
cd frontend
npm install
npm run dev
```

---

# 📁 Project Structure

Our application uses a strict Domain-Driven modular architecture divided natively between React interfaces and Python services.

```text
intervux-ai/                        
|- backend/                         # FastAPI Python runtime
|  |- main.py                       # App entrypoint + ASGI hook
|  |- ai/                           # AI Namespaces (Models, STT, Engines)
|  |- api/routes/                   # Granular REST API Endpoints
|  |- auth/                         # JWT, RBAC security
|  |- background/                   # Background Task orchestration
|  |- core/                         # LLM Brains and configurations
|  |- db/                           # SQLAlchemy engine + models
|  |- services/                     # Evaluation telemetry routers
|  `- sockets/                      # Real-time WebSockets logic
|- frontend/                        # React / Vite SPA
|  |- src/components/dashboard/     # Shared React widgets
|  |- src/pages/                    # Top-level routable views
|  `- src/types/                    # Global Typescript interfaces
|- tests/                           # Pytest suites
|- requirements/                    # Python PIP registries
|- docs/                            # Project Documentation & Architecture
|- docker-compose.yaml              # Local Docker orchestration
|- Dockerfile                       # Container manifest
`- .env.docker.example              # Container secrets template
```

---

# 🏗️ System Architecture 

Intervux connects modern browser UX to powerful multi-agent AI pipelines processing on background Celery workers. 

```mermaid
flowchart TD
    User[Candidate User] -->|UI + Audio| Frontend[React Frontend]
    Frontend -->|HTTP / WebSocket| Backend[FastAPI Backend]
    Backend -->|Async Tasking| Redis[(Redis Broker)]
    Redis -->|Evaluation Jobs| Worker[Celery Worker]
    Worker -->|LLM Prompts| Provider[LLM Provider]
    Worker -->|Persist Evaluates| PostgreSQL[(PostgreSQL)]
    Backend -->|Stream Results| Dashboard[Recruiter Dashboard]
```

### Core Features
*   **Context Awareness:** Natural Language Processing (NLP) parses resumes to build interview context parameters.
*   **Adaptive Interview Engine:** Next-question logic is determined probabilistically by evaluating immediate prior answers from candidates.
*   **Recruiter Intelligence:** Endpoints like `/api/interview/{id}/decision` yield explicit, data-backed recruiter recommendations.
*   **Experiment Tracking:** Allows administrators to trace and compare LLM latency (`p99`), response quality, and throughput per model deployed.

---

# Testing 🧪

To validate system reliability before a deployment, run the unified tracking suite.

```powershell
pip install -r requirements/test.txt
pytest -v
```

CI (Continuous Integration) also runs these assertions automatically on push via `.github/workflows/tests.yml`.

---

# License 📄

Distributed under the MIT License. Built with ❤️ by Vishal Gorule.
