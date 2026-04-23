# Developer Workflow & Setup

Getting Intervux AI up and running locally for development.

## 📦 Prerequisites
- **Docker & Docker Compose** (Highly recommended).
- **Python 3.10+** (For local backend work).
- **Node.js 18+** (For frontend work).
- **API Keys**: Google Gemini (Google AI Studio), ElevenLabs.

## 🚀 Local Setup (Docker)

1. **Clone the Repo**.
2. **Setup Env**: Create a `.env` in the root (use `.env.example` as a template).
3. **Start Services**:
   ```bash
   docker-compose up --build
   ```
   This will start:
   - `intervux-db`: PostgreSQL.
   - `intervux-redis`: Redis.
   - `intervux-backend`: FastAPI App.
   - `intervux-frontend`: Vite (exposed on :5173).
   - `intervux-celery`: Worker.
   - `intervux-beat`: Task Scheduler.

## 🛠 Manual Development (No Docker)

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. `python main.py`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## 🧪 Running Tests
- **Backend Tests**: `pytest backend/tests`
- **Verification Scripts**: `python scripts/verify_system_health.py`

## 📡 Port Mapping
- Frontend: `5173`
- Backend API: `8000`
- WebSocket: `ws://localhost:8000/ws/interview`
- PostgreSQL: `5432`
- Redis: `6379`

## 🔄 Deployment Logic
The system is built for containerization. For production:
1. Build images via Docker.
2. Deploy to a cloud provider (AWS/GCP/Azure) using an orchestrator like Kubernetes or ECS.
3. Use a persistent block storage (e.g., S3) for large audio files.
