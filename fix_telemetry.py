import re

filepath = "backend/services/telemetry_service.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Fix EvaluationDBLogger.write
old_write = """    def write(self, payload: Dict[str, Any]):
        \"\"\"Write evaluation metrics to PostgreSQL.\"\"\"
        if not self.enabled:
            return
        
        try:
            db = SessionLocal()
            try:
                metric = LLMMetrics(
                    model=payload.get("model", "unknown"),
                    latency_ms=int(payload.get("latency_ms", 0)),
                    prompt_tokens=int(payload.get("prompt_tokens", 0)),
                    completion_tokens=int(payload.get("completion_tokens", 0)),
                    cost_usd=float(payload.get("cost_usd", 0.0)),
                    accuracy_score=float(payload.get("accuracy_score", 0.0)),
                    hallucination_score=float(payload.get("hallucination_score", 0.0)),
                    reasoning_score=float(payload.get("reasoning_score", 0.0)),
                    consistency_score=float(payload.get("consistency_score", 0.0)),
                    created_at=datetime.utcnow()
                )
                db.add(metric)
                db.commit()
            except Exception:
                db.rollback()
                logger.exception("Telemetry DB transaction failed; rolled back")
            finally:
                db.close()
        except Exception:
            logger.exception("Telemetry DB logging failed")"""

new_write = """    async def write(self, payload: Dict[str, Any]):
        \"\"\"Write evaluation metrics to PostgreSQL.\"\"\"
        if not self.enabled:
            return
        
        try:
            from backend.db.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                try:
                    metric = LLMMetrics(
                        model=payload.get("model", "unknown"),
                        latency_ms=int(payload.get("latency_ms", 0)),
                        prompt_tokens=int(payload.get("prompt_tokens", 0)),
                        completion_tokens=int(payload.get("completion_tokens", 0)),
                        cost_usd=float(payload.get("cost_usd", 0.0)),
                        accuracy_score=float(payload.get("accuracy_score", 0.0)),
                        hallucination_score=float(payload.get("hallucination_score", 0.0)),
                        reasoning_score=float(payload.get("reasoning_score", 0.0)),
                        consistency_score=float(payload.get("consistency_score", 0.0)),
                        created_at=datetime.utcnow()
                    )
                    db.add(metric)
                    await db.commit()
                except Exception:
                    await db.rollback()
                    logger.exception("Telemetry DB transaction failed; rolled back")
        except Exception:
            logger.exception("Telemetry DB logging failed")"""

text = text.replace(old_write, new_write)

old_db_log = """        # Write to JSONL
        self.jsonl_logger.write(payload)
        
        # Write to PostgreSQL
        self.db_logger.write(payload)"""

new_db_log = """        # Write to JSONL
        self.jsonl_logger.write(payload)
        
        # Write to PostgreSQL
        import asyncio
        asyncio.create_task(self.db_logger.write(payload))"""

text = text.replace(old_db_log, new_db_log)

old_log_metrics_call = """    # Log via telemetry service
    telemetry_service.log_evaluation_from_evaluation_result(
        model=model,
        latency_ms=latency_seconds * 1000,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        evaluation_result=evaluation_result,
        cost_per_1k=cost_per_1k
    )"""

new_log_metrics_call = """    # Log via telemetry service
    await telemetry_service.log_evaluation_from_evaluation_result(
        model=model,
        latency_ms=latency_seconds * 1000,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        evaluation_result=evaluation_result,
        cost_per_1k=cost_per_1k
    )"""

text = text.replace(old_log_metrics_call, new_log_metrics_call)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: telemetry_service.py replaced")
