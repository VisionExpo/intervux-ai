import re

filepath = "backend/services/evaluation_dashboard_store.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Replace Session with AsyncSession
text = text.replace("from sqlalchemy.orm import Session", "from sqlalchemy.ext.asyncio import AsyncSession\nfrom sqlalchemy import select")
text = text.replace("db: Session", "db: AsyncSession")

# get_evaluation_dashboard
text = text.replace("def get_evaluation_dashboard(", "async def get_evaluation_dashboard(")
text = text.replace(
    """    interviews = db.query(Interview).all()""",
    """    res = await db.execute(select(Interview))
    interviews = res.scalars().all()"""
)

# get_llm_metrics_from_db
text = text.replace("def get_llm_metrics_from_db(", "async def get_llm_metrics_from_db(")
old_llm_metrics = """    query = db.query(LLMMetrics)
    
    if days is not None:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(LLMMetrics.created_at >= cutoff)
    
    if model:
        query = query.filter(LLMMetrics.model == model)
    
    return query.order_by(LLMMetrics.created_at.desc()).all()"""
new_llm_metrics = """    query = select(LLMMetrics)
    
    if days is not None:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(LLMMetrics.created_at >= cutoff)
    
    if model:
        query = query.filter(LLMMetrics.model == model)
    
    res = await db.execute(query.order_by(LLMMetrics.created_at.desc()))
    return res.scalars().all()"""
text = text.replace(old_llm_metrics, new_llm_metrics)

# get_db_metrics_aggregates
text = text.replace("def get_db_metrics_aggregates(", "async def get_db_metrics_aggregates(")
old_aggr = """    metrics_24h = db.query(LLMMetrics).filter(
        LLMMetrics.created_at >= cutoff_24h
    ).all()
    
    metrics_7d = db.query(LLMMetrics).filter(
        LLMMetrics.created_at >= cutoff_7d
    ).all()
    
    metrics_30d = db.query(LLMMetrics).filter(
        LLMMetrics.created_at >= cutoff_30d
    ).all()"""
new_aggr = """    res_24h = await db.execute(select(LLMMetrics).filter(LLMMetrics.created_at >= cutoff_24h))
    metrics_24h = res_24h.scalars().all()
    
    res_7d = await db.execute(select(LLMMetrics).filter(LLMMetrics.created_at >= cutoff_7d))
    metrics_7d = res_7d.scalars().all()
    
    res_30d = await db.execute(select(LLMMetrics).filter(LLMMetrics.created_at >= cutoff_30d))
    metrics_30d = res_30d.scalars().all()"""
text = text.replace(old_aggr, new_aggr)

# get_historical_trends
text = text.replace("def get_historical_trends(", "async def get_historical_trends(")
old_trends = """    daily_metrics = db.query(
        func.date(LLMMetrics.created_at).label("date"),
        func.avg(LLMMetrics.latency_ms).label("avg_latency"),
        func.avg(LLMMetrics.accuracy_score).label("avg_accuracy"),
        func.avg(LLMMetrics.hallucination_score).label("avg_hallucination"),
        func.sum(LLMMetrics.cost_usd).label("total_cost"),
        func.count(LLMMetrics.id).label("request_count"),
    ).filter(
        LLMMetrics.created_at >= cutoff
    ).group_by(
        func.date(LLMMetrics.created_at)
    ).order_by(
        func.date(LLMMetrics.created_at)
    ).all()"""
new_trends = """    query = select(
        func.date(LLMMetrics.created_at).label("date"),
        func.avg(LLMMetrics.latency_ms).label("avg_latency"),
        func.avg(LLMMetrics.accuracy_score).label("avg_accuracy"),
        func.avg(LLMMetrics.hallucination_score).label("avg_hallucination"),
        func.sum(LLMMetrics.cost_usd).label("total_cost"),
        func.count(LLMMetrics.id).label("request_count"),
    ).filter(
        LLMMetrics.created_at >= cutoff
    ).group_by(
        func.date(LLMMetrics.created_at)
    ).order_by(
        func.date(LLMMetrics.created_at)
    )
    res = await db.execute(query)
    daily_metrics = res.all()"""
text = text.replace(old_trends, new_trends)

# log_experiment
text = text.replace("def log_experiment(", "async def log_experiment(")
text = text.replace(
    """    db.add(experiment)
    db.commit()""",
    """    db.add(experiment)
    await db.commit()"""
)

# get_experiments
text = text.replace("def get_experiments(", "async def get_experiments(")
old_get_exp = """    return db.query(Experiment).order_by(
        Experiment.created_at.desc()
    ).limit(limit).all()"""
new_get_exp = """    res = await db.execute(select(Experiment).order_by(
        Experiment.created_at.desc()
    ).limit(limit))
    return res.scalars().all()"""
text = text.replace(old_get_exp, new_get_exp)

# compare_experiments
text = text.replace("def compare_experiments(", "async def compare_experiments(")
old_cmp_exp = """    experiments = db.query(Experiment).filter(
        Experiment.experiment_name.in_(experiment_names)
    ).all()"""
new_cmp_exp = """    res = await db.execute(select(Experiment).filter(
        Experiment.experiment_name.in_(experiment_names)
    ))
    experiments = res.scalars().all()"""
text = text.replace(old_cmp_exp, new_cmp_exp)


with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: evaluation_dashboard_store.py replaced")
