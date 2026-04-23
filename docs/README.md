# Intervux AI: Professional AI Interview Platform

Intervux AI is a production-grade, AI-driven SaaS platform designed to automate and scale the first-round technical interview process. It provides candidates with an immersive, real-time interview experience featuring a responsive 3D avatar, while providing recruiters with deep, structured evaluation insights.

## 🎯 The Problem
Traditional technical interviewing is slow, expensive, and prone to human bias. Companies often struggle to filter high volumes of candidates consistently. Intervux AI solves this by providing a "24/7 technical screener" that conducts high-fidelity interviews, evaluates reasoning, and generates structured reports.

## 🚀 Key Features
- **Real-time Voice Interaction**: Low-latency WebSocket-based audio stream with 3D avatar lip-sync.
- **Dynamic Questioning**: Adaptive LLM-driven interviews based on candidate resumes and real-time responses.
- **Multi-Pass Evaluation**: Deep reasoning analysis that goes beyond simple keyword matching to evaluate technical depth and consistency.
- **Enterprise Dashboard**: Comprehensive recruiter views for managing candidates, reviewing transcripts, and analyzing competency scores.
- **Hardened Infrastructure**: Built with an App Factory pattern, structured observability, and non-blocking startup orchestration.

## 🛠 Tech Stack
- **Backend**: FastAPI, Celery, Redis, PostgreSQL, Pydantic v2.
- **Frontend**: React, Vite, Framer Motion (for animations), CSS Modules (Glassmorphism).
- **AI/ML**: Google Gemini (LLM), ElevenLabs (TTS), Azure Speech (STT), Custom Viseme Engine.
- **Infrastructure**: Docker Compose, GitHub Actions (CI/CD).

## 🏗 High-Level Architecture
Intervux AI follows a service-oriented architecture designed for scalability and maintainability:

1.  **WebSocket Gateway**: Orchestrates real-time audio and metadata flow.
2.  **Interview Engine**: Manages the stateful conversation and adaptive questioning logic.
3.  **Evaluation Pipeline**: An asynchronous multi-pass system for candidate scoring.
4.  **LLM Layer**: A robust wrapper around LLMs featuring safe JSON parsing and provider fallbacks.
5.  **Persistence Layer**: Dual-storage approach using Redis for real-time session state and PostgreSQL for permanent records.

---

*See [architecture.md](architecture.md) for a deep dive into the system components.*
