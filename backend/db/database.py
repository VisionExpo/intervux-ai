import os

from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/intervux"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# LLM Metrics Table for Dashboard Telemetry
# =========================================================

class LLMMetrics(Base):
    __tablename__ = "llm_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(String, nullable=False)
    latency_ms = Column(Integer, nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    cost_usd = Column(Float, nullable=False)
    accuracy_score = Column(Float, nullable=True)
    hallucination_score = Column(Float, nullable=True)
    reasoning_score = Column(Float, nullable=True)
    consistency_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# =========================================================
# Experiment Tracking Table
# =========================================================

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_name = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    prompt_template = Column(String, nullable=True)
    accuracy = Column(Float, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

