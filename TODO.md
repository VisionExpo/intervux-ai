# Project Folder Structure

## Recommended Clean Production Structure

```
intervux-ai/
├── .dockerignore
├── .gitignore
├── docker-compose.yaml
├── LICENSE
├── package.json
├── package-lock.json
├── README.md
├── TODO.md
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── candidate_routes.py
│   │       └── resume_routes.py
│   │
│   ├── auth/
│   │   ├── jwt_service.py
│   │   ├── rbac.py
│   │   └── routes.py
│   │
│   ├── config/
│   │   ├── prompt_loader.py
│   │   ├── prompts.yaml
│   │   ├── setting.py
│   │   └── model_registry.py
│   │
│   ├── core/
│   │   ├── adaptive_engine.py
│   │   ├── agent_ocr.py
│   │   ├── audio_stack.py
│   │   ├── celery_app.py
│   │   ├── code_engine.py
│   │   ├── consistency_checker.py
│   │   ├── difficulty_engine.py
│   │   ├── emotion_ai.py
│   │   ├── evaluation_engine.py
│   │   ├── knowledge_graph.py
│   │   ├── llm_brain.py
│   │   ├── memory_engine.py
│   │   ├── multipass_evaluator.py
│   │   ├── reasoning_analyzer.py
│   │   ├── self_consistency.py
│   │   └── skill_coverage.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── alembic/
│   │       ├── env.py
│   │       ├── script.py.mako
│   │       └── versions/
│   │           ├── 001_initial.py
│   │           ├── 002_job_posts_candidates.py
│   │           └── 003_candidate_portal.py
│   │
│   ├── engines/
│   │   └── interview_engine.py
│   │
│   ├── middleware/
│   │   └── rate_limiter.py
│   │
│   ├── models/
│   │   ├── candidate_portal.py
│   │   ├── evaluation_dashboard.py
│   │   ├── interview.py
│   │   ├── recruiter_dashboard.py
│   │   └── recruiter_dashboard_models.py
│   │
│   ├── resume_parser/
│   │   ├── models.py
│   │   └── services.py
│   │
│   ├── services/
│   │   ├── alerting_service.py
│   │   ├── audio_buffer.py
│   │   ├── audit_service.py
│   │   ├── decision_support_service.py
│   │   ├── evaluation_dashboard_store.py
│   │   ├── evaluation_service.py
│   │   ├── recruiter_dashboard_store.py
│   │   ├── stt_service.py
│   │   ├── telemetry_service.py
│   │   ├── tts_service.py
│   │   └── viseme_service.py
│   │
│   ├── sessions/
│   │   ├── interview_session.py
│   │   └── registry.py
│   │
│   ├── sockets/
│   │   ├── interview.py
│   │   ├── interview_gateway.py
│   │   └── metrics.py
│   │
│   ├── workers/
│   │   ├── resume_tasks.py
│   │   ├── evaluation_tasks.py
│   │   └── stt_tasks.py
│   │
│   ├── ai_models/
│   │   ├── skill_taxonomy.json
│   │   ├── embeddings/
│   │   └── prompts/
│   │
│   ├── scripts/
│   │   └── seed_dashboard.py
│   │
│   ├── static/
│   │   └── audio/
│   │       └── ff56422a-3a6b-4bea-990b-7029528c8dad.wav
│   │
│   └── utils/
│       ├── logger.py
│       ├── metrics.py
│       ├── research_logger.py
│       ├── runtime_monitor.py
│       └── structured_logger.py
│
├── docker/
│   └── Dockerfile
│
├── docs/
│   ├── HLD_Intervux_AI.docx
│   ├── LLD_Intervux_AI.docx
│   ├── README.md
│   ├── recruiter_dashboard_schema.sql
│   │
│   ├── rubrics/
│   │   └── evaluation_schema.md
│   │
│   └── sessions/
│       ├── interview_average.json
│       ├── interview_good.json
│       └── interview_poor.json
│
├── frontend/
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.js
│   ├── README.md
│   ├── tailwind.config.js
│   ├── TODO_ENHANCEMENTS.md
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   │
│   ├── public/
│   │   ├── avatar.vrm
│   │   └── vite.svg
│   │
│   └── src/
│       ├── App.css
│       ├── App.tsx
│       ├── index.css
│       ├── main.tsx
│       │
│       ├── assets/
│       │   └── react.svg
│       │
│       ├── avatar/
│       │   ├── AvatarScene.tsx
│       │   ├── BlinkController.ts
│       │   ├── LipSyncController.ts
│       │   ├── visemeMap.ts
│       │   └── VRMAvatar.tsx
│       │
│       ├── components/
│       │   ├── Avatar3D/
│       │   │   └── index.tsx
│       │   │
│       │   └── interview/
│       │       ├── AudioStreamHandler.tsx
│       │       ├── AvatarInterviewer.tsx
│       │       ├── CandidateCamera.tsx
│       │       ├── CodingSandbox.tsx
│       │       ├── InterviewLayout.tsx
│       │       ├── TranscriptPanel.tsx
│       │       └── index.ts
│       │
│       ├── hooks/
│       │   ├── useAuth.tsx
│       │   ├── useAvatarSocket.ts
│       │   ├── useInterview.ts
│       │   └── useInterviewStateMachine.ts
│       │
│       ├── pages/
│       │   ├── AIEvaluationDashboard.tsx
│       │   ├── CandidateComparison.tsx
│       │   ├── CandidateDashboard.tsx
│       │   ├── CandidateInterviewReport.tsx
│       │   ├── CandidateList.tsx
│       │   ├── CandidateNotifications.tsx
│       │   ├── CandidateProfile.tsx
│       │   ├── InterviewHistory.tsx
│       │   ├── InterviewPage.tsx
│       │   ├── InterviewReplay.tsx
│       │   ├── InterviewReport.tsx
│       │   ├── Login.tsx
│       │   ├── MockInterview.tsx
│       │   ├── RecruiterDashboard.tsx
│       │   ├── Signup.tsx
│       │   ├── SkillAnalytics.tsx
│       │   └── types.ts
│       │
│       └── utils/
│           └── audioFeedback.ts
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_decision.py
│   ├── test_experiments.py
│   ├── test_health.py
│   ├── test_metrics.py
│   ├── test.db
│   └── TESTING.md
│
├── logs/
├── uploads/
└── myenv/
```

## Key Restructuring Notes

1. **requirements.txt** → moved to `backend/requirements.txt`
2. **Routes** → moved to `backend/api/routes/`
3. **Celery Tasks** → consolidated in `backend/workers/`
4. **AI Models** → new `backend/ai_models/` folder for skill taxonomy, embeddings, and prompts
5. **Alembic migrations** → moved inside `backend/db/` for better organization

