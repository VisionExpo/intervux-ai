# Project Structure

```text
intervux-ai/
├── backend/
│   ├── ai_models/
│   ├── api/
│   │   └── routes/
│   ├── auth/
│   ├── background/
│   ├── config/
│   ├── core/
│   ├── db/
│   │   └── alembic/
│   │       └── versions/
│   ├── engines/
│   ├── middleware/
│   ├── models/
│   ├── resume_parser/
│   ├── routes/
│   ├── scripts/
│   ├── services/
│   ├── sessions/
│   ├── sockets/
│   ├── static/
│   │   └── audio/
│   ├── utils/
│   ├── workers/
│   ├── __init__.py
│   ├── main.py
│   └── requirements.txt
├── docker/
│   └── Dockerfile
├── docs/
├── evaluation/
│   ├── rubrics/
│   └── sessions/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── avatar/
│   │   ├── components/
│   │   │   ├── Avatar3D/
│   │   │   └── interview/
│   │   ├── hooks/
│   │   ├── pages/
│   │   └── utils/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── logs/
├── tests/
├── uploads/
├── .dockerignore
├── .env
├── .env.docker
├── .gitignore
├── alembic.ini
├── conftest_backup.py
├── docker-compose.yaml
├── Dockerfile
├── LICENSE
├── pytest.ini
├── README.md
├── requirements-test.txt
├── requirements.txt
└── TODO.md
```

## Notes

- Omitted from tree for readability: `.git/`, `.pytest_cache/`, `myenv/`, `node_modules/`, `__pycache__/`.
- Two Dockerfile locations exist: root `Dockerfile` and `docker/Dockerfile`.
- Python dependency files exist at both root (`requirements.txt`) and backend (`backend/requirements.txt`).
