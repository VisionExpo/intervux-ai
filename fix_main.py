import re

filepath = "backend/main.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Imports
text = text.replace("from sqlalchemy.orm import Session", "from sqlalchemy.ext.asyncio import AsyncSession")

# 2. _run_alembic_migrations
old_alembic = """def _run_alembic_migrations() -> None:
    \"\"\"
    Run 'alembic upgrade head' as a subprocess.

    Falls back to create_all for SQLite/dev environments.
    \"\"\"
    db_url = os.getenv("DATABASE_URL", "")
    if _is_sqlite(db_url):
        logger.info("SQLite detected — using create_all for dev/test environment")
        Base.metadata.create_all(bind=engine)
        return

    logger.info("Running Alembic migrations...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            logger.error(f"Alembic migration failed:\\n{result.stderr}")
            raise RuntimeError(f"Alembic migration failed: {result.stderr}")
        logger.info(f"Alembic migrations complete:\\n{result.stdout}")
    except FileNotFoundError:
        logger.warning("alembic not found — falling back to create_all (run migrations manually)")
        Base.metadata.create_all(bind=engine)"""

new_alembic = """async def _run_alembic_migrations() -> None:
    \"\"\"
    Run 'alembic upgrade head' as a subprocess.

    Falls back to create_all for SQLite/dev environments.
    \"\"\"
    db_url = os.getenv("DATABASE_URL", "")
    if _is_sqlite(db_url):
        logger.info("SQLite detected — using create_all for dev/test environment")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return

    logger.info("Running Alembic migrations...")
    try:
        # Run subprocess concurrently
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "alembic", "upgrade", "head",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logger.error(f"Alembic migration failed:\\n{stderr.decode()}")
            raise RuntimeError(f"Alembic migration failed: {stderr.decode()}")
        logger.info(f"Alembic migrations complete:\\n{stdout.decode()}")
    except FileNotFoundError:
        logger.warning("alembic not found — falling back to create_all (run migrations manually)")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)"""
text = text.replace(old_alembic, new_alembic)

# 3. lifespan
old_lifespan = """    # Wait for Postgres readiness before metadata/table initialization.
    db_ready = False
    for _ in range(20):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_ready = True
            break
        except Exception:
            await asyncio.sleep(1.5)

    if not db_ready:
        logger.warning("Database was not ready during startup warmup window")

    _run_alembic_migrations()"""
new_lifespan = """    # Wait for Postgres readiness before metadata/table initialization.
    db_ready = False
    for _ in range(20):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            db_ready = True
            break
        except Exception:
            await asyncio.sleep(1.5)

    if not db_ready:
        logger.warning("Database was not ready during startup warmup window")

    await _run_alembic_migrations()"""
text = text.replace(old_lifespan, new_lifespan)

# 4. readiness_check
old_ready = """@app.get("/ready")
def readiness_check():
    \"\"\"
    Readiness check endpoint for Kubernetes/load balancers.
    
    Checks:
    - Database connectivity
    - LLM service availability
    \"\"\"
    checks = {
        "status": "ok",
        "database": "unknown",
    }
    
    # Check database connectivity
    try:
        from sqlalchemy import text
        from backend.db.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = "disconnected"
        checks["status"] = "degraded\"\"\""""

# Wait, the `readiness` has more
text = text.replace("@app.get(\"/ready\")\ndef readiness_check():", "@app.get(\"/ready\")\nasync def readiness_check():")
text = text.replace("""    # Check database connectivity
    try:
        from sqlalchemy import text
        from backend.db.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["database"] = "connected"
    except Exception as e:""", """    # Check database connectivity
    try:
        from sqlalchemy import text
        from backend.db.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception as e:""")

# 5. Dashboard routes
text = text.replace("def get_ai_evaluation_dashboard(", "async def get_ai_evaluation_dashboard(")
text = text.replace("    return get_evaluation_dashboard(db)", "    return await get_evaluation_dashboard(db)")

text = text.replace("def get_candidates(", "async def get_candidates(")
text = text.replace("    return list_candidates(db, page=page, limit=limit, role=role, search=search)", "    return await list_candidates(db, page=page, limit=limit, role=role, search=search)")

text = text.replace("def get_interview(", "async def get_interview(")
text = text.replace("    return get_interview_report(db, interview_id)", "    return await get_interview_report(db, interview_id)")

text = text.replace("def get_interview_analytics(", "async def get_interview_analytics(")
text = text.replace("    return get_skill_analytics(db, interview_id)", "    return await get_skill_analytics(db, interview_id)")

text = text.replace("def get_candidate_comparison(", "async def get_candidate_comparison(")
text = text.replace("    return compare_candidates(db)", "    return await compare_candidates(db)")

text = text.replace("def get_metrics_aggregates(", "async def get_metrics_aggregates(")
text = text.replace("    return get_db_metrics_aggregates(db)", "    return await get_db_metrics_aggregates(db)")

text = text.replace("def get_metrics_trends(", "async def get_metrics_trends(")
text = text.replace("    return get_historical_trends(db, days=days)", "    return await get_historical_trends(db, days=days)")

text = text.replace("def get_experiment_list(", "async def get_experiment_list(")
text = text.replace("    return get_experiments(db, limit=limit)", "    return await get_experiments(db, limit=limit)")

text = text.replace("def create_experiment(", "async def create_experiment(")
text = text.replace("""    return log_experiment(
        db,
        experiment_name=payload.experiment_name,
        model_version=payload.model_version,
        prompt_template=payload.prompt_template,
        accuracy=payload.accuracy,
        latency_ms=payload.latency_ms,
    )""", """    return await log_experiment(
        db,
        experiment_name=payload.experiment_name,
        model_version=payload.model_version,
        prompt_template=payload.prompt_template,
        accuracy=payload.accuracy,
        latency_ms=payload.latency_ms,
    )""")

text = text.replace("def compare_experiment_results(", "async def compare_experiment_results(")
text = text.replace("    return compare_experiments(db, payload.experiment_names)", "    return await compare_experiments(db, payload.experiment_names)")

text = text.replace("def get_interview_decision(", "async def get_interview_decision(")
text = text.replace("    interview = get_interview_report(db, interview_id)", "    interview = await get_interview_report(db, interview_id)")

text = text.replace("def get_job_posts(", "async def get_job_posts(")
text = text.replace("    return list_job_posts(db, page=page, limit=limit, status=status)", "    return await list_job_posts(db, page=page, limit=limit, status=status)")

text = text.replace("def create_new_job_post(", "async def create_new_job_post(")
text = text.replace("    return create_job_post(db, job_data, created_by=user.user_id)", "    return await create_job_post(db, job_data, created_by=user.user_id)")

text = text.replace("def get_job(", "async def get_job(")
text = text.replace("    job = get_job_post(db, job_post_id)", "    job = await get_job_post(db, job_post_id)")

text = text.replace("def update_job(", "async def update_job(")
text = text.replace("    job = update_job_post(db, job_post_id, job_data)", "    job = await update_job_post(db, job_post_id, job_data)")

text = text.replace("def delete_job(", "async def delete_job(")
text = text.replace("    success = delete_job_post(db, job_post_id)", "    success = await delete_job_post(db, job_post_id)")

text = text.replace("def invite_new_candidate(", "async def invite_new_candidate(")
text = text.replace("    candidate = invite_candidate(db, candidate_data)", "    candidate = await invite_candidate(db, candidate_data)")

text = text.replace("def create_interview_link(", "async def create_interview_link(")
text = text.replace("    interview_link, expires_at = generate_interview_link(db, candidate_id, expires_days)", "    interview_link, expires_at = await generate_interview_link(db, candidate_id, expires_days)")

text = text.replace("def change_candidate_status(", "async def change_candidate_status(")
text = text.replace("    candidate = update_candidate_status(db, candidate_id, status)", "    candidate = await update_candidate_status(db, candidate_id, status)")

# Replace db: Session to db: AsyncSession for all routes
text = text.replace("db: Session ", "db: AsyncSession ")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: main.py updated.")
