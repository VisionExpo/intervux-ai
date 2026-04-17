# Deployment Verification Checklist

Last verified: 2026-04-17

## 1. Tooling & Compose Syntax
- `docker --version`
- `docker compose version`
- `docker compose -f docker-compose.yaml config -q`

Pass criteria:
- Docker and Compose commands return exit code 0.
- Compose config validation returns exit code 0.

## 2. Security & Runtime Hardening
- `docker/entrypoint.sh`:
  - migrations are fail-fast (`alembic upgrade head` must succeed)
  - migration execution controlled by `RUN_DB_MIGRATIONS`
- `docker-compose.yaml`:
  - no host port publishing for `postgres`/`redis`
  - `backend` healthcheck uses `/ready`
  - `worker`, `beat`, `flower` set `RUN_DB_MIGRATIONS=false`
  - Flower requires basic auth via `FLOWER_BASIC_AUTH`

Required env:
- `.env.docker` must include `FLOWER_BASIC_AUTH=<user>:<strong_password>`

## 3. Bring Up Stack
- `docker compose -f docker-compose.yaml up -d --build` (first run)
- `docker compose -f docker-compose.yaml up -d` (subsequent runs)
- `docker compose -f docker-compose.yaml ps`

Pass criteria:
- `backend`, `worker`, `postgres`, `redis`, `flower` are `Up`
- `backend`, `worker`, `postgres`, `redis`, `flower` report healthy status
- `beat` is `Up` (healthcheck intentionally disabled)

## 4. Endpoint Smoke Tests
- `GET http://localhost:8000/health` -> `200`
- `GET http://localhost:8000/ready` -> `200`
- `GET http://localhost:8000/docs` -> `200`
- `GET http://localhost:5555/` (without auth) -> `401`

## 5. Worker Smoke Tests
- `docker compose -f docker-compose.yaml exec -T worker celery -A backend.core.celery_app:celery_app inspect ping`
- Trigger task:
  - `docker compose -f docker-compose.yaml exec -T backend python -c "from backend.core.celery_tasks import health_check; r=health_check.delay(); print(r.id)"`
- Verify worker logs:
  - `docker compose -f docker-compose.yaml logs worker --tail 120`

Pass criteria:
- `inspect ping` returns `pong`
- worker logs show `health_check` task received and succeeded

## Rollback
If deployment fails:
- `docker compose -f docker-compose.yaml down`
- `git restore docker-compose.yaml docker/entrypoint.sh`
- restore known-good env values in `.env.docker`
- redeploy with `docker compose -f docker-compose.yaml up -d --build`

