# Intervux AI – Docker Production Setup TODO

## 🎯 Goal

Containerize the **Intervux AI backend** using Docker so the system runs with:

* FastAPI API server
* Celery background workers
* Redis task broker
* PostgreSQL database
* Flower monitoring dashboard

This setup enables **production-grade async resume processing and scalable AI interview pipelines**.

---

# Phase 1 — Project Structure

Create the following directory structure:

```
intervux-ai
│
├── backend
│   ├── app
│   │   ├── main.py
│   │   ├── core
│   │   │   └── celery_app.py
│   │   ├── workers
│   │   │   └── resume_tasks.py
│   │   └── resume_parser
│   │       └── pipeline.py
│   │
│   └── requirements.txt
│
├── docker
│   ├── Dockerfile
│   └── entrypoint.sh
│
├── docker-compose.yml
├── .env
└── .dockerignore
```

Tasks:

* [x] Create `docker/` directory
* [x] Create `Dockerfile`
* [x] Create `docker-compose.yml`
* [x] Create `.env` file
* [x] Create `.dockerignore`

---

# Phase 2 — Dockerfile Implementation

Create:

```
docker/Dockerfile
```

Tasks:

* [x] Use lightweight base image `python:3.11-slim`
* [x] Set Python environment variables
* [x] Install required system dependencies
* [x] Create non-root user `appuser`
* [x] Set working directory `/app`
* [x] Copy `requirements.txt`
* [x] Install Python dependencies
* [x] Copy backend application code
* [x] Set correct file permissions
* [x] Switch to non-root user
* [x] Expose port `8000`
* [x] Run FastAPI using `uvicorn`

Goals:

* secure container
* smaller image
* optimized build layers

---

# Phase 3 — Docker Ignore

Create `.dockerignore`.

Tasks:

* [x] Ignore Python cache files
* [x] Ignore `.env`
* [x] Ignore `.git`
* [x] Ignore virtual environments
* [x] Ignore logs

---

# Phase 4 — Environment Configuration

Create `.env`.

Tasks:

* [x] Define PostgreSQL credentials
* [x] Define Redis connection
* [x] Define Celery broker configuration

---

# Phase 5 — Docker Compose Services

Create `docker-compose.yml`.

Services to configure:

### API Service

Tasks:

* [x] Build image from Dockerfile
* [x] Run FastAPI server
* [x] Map port `8000`
* [x] Load `.env`
* [x] Add dependency on Redis and Postgres
* [x] Enable automatic restart

### Celery Worker

Tasks:

* [x] Use same Docker image
* [x] Start Celery worker
* [x] Set concurrency level
* [x] Load environment variables
* [x] Enable restart policy

### Redis Service

Tasks:

* [x] Use `redis:7-alpine`
* [x] Expose port `6379`
* [x] Enable restart policy

### PostgreSQL Service

Tasks:

* [x] Use `postgres:15`
* [x] Load `.env`
* [x] Persist database using Docker volume
* [x] Expose port `5432`

### Flower Monitoring

Tasks:

* [x] Run Flower dashboard
* [x] Connect to Celery workers
* [x] Expose port `5555`

---

# Phase 6 — Celery Configuration

Create files:

```
backend/core/celery_app.py
backend/core/celery_tasks.py
```

Tasks:

* [x] Initialize Celery instance
* [x] Load broker URL from environment variables
* [x] Load result backend
* [x] Configure serializers
* [x] Enable UTC timezone
* [x] Create background tasks for resume parsing
* [x] Create background tasks for evaluation generation
* [x] Create background tasks for report generation

---

# Phase 7 — System Startup

Run containers.

Tasks:

* [ ] Build Docker images
* [ ] Start containers
* [ ] Verify service health

Command:

```
docker compose up --build
```

Verify containers:

```
docker ps
```

Expected services:

```
intervux_api
intervux_worker
intervux_redis
intervux_postgres
intervux_flower
```

---

# Phase 8 — Service Verification

Test API server.

Tasks:

* [ ] Open API docs
* [ ] Test upload endpoints
* [ ] Confirm Celery tasks run
* [ ] Verify Redis queues
* [ ] Confirm Postgres writes

URLs:

```
API docs:
http://localhost:8000/docs

Celery dashboard:
http://localhost:5555
```

---

# Phase 9 — Scaling Workers

Increase background processing capacity.

Tasks:

* [ ] Increase Celery concurrency
* [ ] Scale worker containers
* [ ] Monitor CPU and memory

Examples:

Increase worker threads:

```
celery worker --concurrency=8
```

Scale containers:

```
docker compose up --scale worker=3
```

---

# Phase 10 — Production Hardening

Future improvements:

* [ ] Add Nginx reverse proxy
* [ ] Enable HTTPS
* [ ] Add centralized logging
* [ ] Implement health checks
* [ ] Add container resource limits
* [ ] Implement auto-scaling

---

# Final System Architecture

```
User Request
      │
      ▼
FastAPI API Server
      │
      ▼
Redis Task Broker
      │
      ▼
Celery Workers
      │
      ▼
Resume Processing Pipeline
      │
      ▼
PostgreSQL Database
```

This architecture enables **asynchronous resume parsing, scalable AI interview processing, and production-ready container deployment for Intervux AI**.

