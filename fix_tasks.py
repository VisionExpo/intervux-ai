import re

filepath = "backend/background/tasks.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Fix generate_evaluation_task
old_eval = """    from backend.services.decision_support_service import generate_full_report
    from backend.db.database import SessionLocal
    from backend.models.recruiter_dashboard_models import Interview, InterviewQuestion
    
    db = SessionLocal()
    try:
        # Get interview data
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            return {"error": "Interview not found"}
        
        # Get questions and answers
        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview_id
        ).all()"""
new_eval = """    from backend.services.decision_support_service import generate_full_report
    from backend.db.database import AsyncSessionLocal
    from backend.models.recruiter_dashboard_models import Interview, InterviewQuestion
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        # Get interview data
        res = await db.execute(select(Interview).filter(Interview.id == interview_id))
        interview = res.scalar_one_or_none()
        
        if not interview:
            return {"error": "Interview not found"}
        
        # Get questions and answers
        res2 = await db.execute(select(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview_id
        ))
        questions = res2.scalars().all()"""
text = text.replace(old_eval, new_eval)

# remove finally
text = text.replace("""        # Generate report
        report = generate_full_report(answers=answers)
        
        return {"report": report, "interview_id": interview_id}
    
    finally:
        db.close()""", """        # Generate report
        report = generate_full_report(answers=answers)
        
        return {"report": report, "interview_id": interview_id}""")

# Fix generate_report_task
old_rep = """    from backend.services.recruiter_dashboard_store import get_interview_report
    from backend.db.database import SessionLocal
    
    db = SessionLocal()
    try:
        report = get_interview_report(db, interview_id)
        return {"report": report, "report_type": report_type}
    finally:
        db.close()"""
new_rep = """    from backend.services.recruiter_dashboard_store import get_interview_report
    from backend.db.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        report = await get_interview_report(db, interview_id)
        return {"report": report, "report_type": report_type}"""
text = text.replace(old_rep, new_rep)

# Fix aggregate_analytics
old_aggr = """    from backend.services.evaluation_dashboard_store import get_db_metrics_aggregates
    from backend.db.database import SessionLocal
    
    db = SessionLocal()
    try:
        metrics = get_db_metrics_aggregates(db)
        logger.info(f"Analytics aggregated: {metrics}")
    finally:
        db.close()"""
new_aggr = """    from backend.services.evaluation_dashboard_store import get_db_metrics_aggregates
    from backend.db.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        metrics = await get_db_metrics_aggregates(db)
        logger.info(f"Analytics aggregated: {metrics}")"""
text = text.replace(old_aggr, new_aggr)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: tasks.py replaced")
