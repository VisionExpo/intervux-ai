import os

from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import sqlalchemy

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/intervux"
)

if DATABASE_URL.startswith("sqlite"):
    async_db_url = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    connect_args = {"check_same_thread": False}
    
    engine = create_async_engine(
        async_db_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )

    # Enable WAL mode for better concurrency in SQLite
    @sqlalchemy.event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()
else:
    # Convert sync postgres URL to asyncpg natively
    async_db_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        async_db_url,
        pool_pre_ping=True,
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE_S", "1800")),
        pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT_S", "30")),
    )

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# =========================================================
# User Model
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="recruiter")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


# =========================================================
# Revoked Token Model
# =========================================================

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(255), unique=True, nullable=False, index=True)
    token_type = Column(String(20), nullable=False, default="access")  # "access" or "refresh"
    revoked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    expires_at = Column(DateTime, nullable=False)  # When the original token expires


# =========================================================
# API Key Model
# =========================================================

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    expires_at = Column(DateTime, nullable=False)


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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)


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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
