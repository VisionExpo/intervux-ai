import re

filepath = "tests/conftest.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Replace synchronous SQLAlchemy imports
text = text.replace("from sqlalchemy import create_engine", "from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker")
text = text.replace("from sqlalchemy.orm import Session, sessionmaker", "")

# Fix database URL
text = text.replace("sqlite:///./tests/data/test_intervux.db", "sqlite+aiosqlite:///./tests/data/test_intervux.db")
text = text.replace("test_engine = create_engine(", "test_engine = create_async_engine(")
text = text.replace("TestSessionLocal = sessionmaker(", "TestSessionLocal = async_sessionmaker(class_=AsyncSession,")

# Replace TestClient with AsyncClient
text = text.replace("from fastapi.testclient import TestClient", "from httpx import AsyncClient, ASGITransport\nimport pytest_asyncio")

# Rewrite db_session
old_db_session = """@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    \"\"\"
    Create a fresh database session for each test.
    
    Yields:
        SQLAlchemy session for database operations
    \"\"\"
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)"""
        
new_db_session = """@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)"""
text = text.replace(old_db_session, new_db_session)

# Rewrite client fixture
old_client = """@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    \"\"\"
    Create a FastAPI TestClient with test database.
    
    Yields:
        TestClient for making HTTP requests
    \"\"\"
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()"""
new_client = """@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncClient:
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()"""
text = text.replace(old_client, new_client)

# Transform test_job_post async
text = text.replace("def test_job_post(db_session: Session) -> JobPost:", "async def test_job_post(db_session: AsyncSession) -> JobPost:")
text = text.replace("@pytest.fixture\nasync def test_job_post", "@pytest_asyncio.fixture\nasync def test_job_post")
text = text.replace("    db_session.commit()\n    db_session.refresh(job)", "    await db_session.commit()\n    await db_session.refresh(job)")
text = text.replace("@pytest.fixture\ndef test_job_post", "@pytest_asyncio.fixture\nasync def test_job_post")

# test_candidate
text = text.replace("def test_candidate(db_session: Session, test_job_post: JobPost) -> Candidate:", "async def test_candidate(db_session: AsyncSession, test_job_post: JobPost) -> Candidate:")
text = text.replace("@pytest.fixture\nasync def test_candidate", "@pytest_asyncio.fixture\nasync def test_candidate")
text = text.replace("    db_session.commit()\n    db_session.refresh(candidate)", "    await db_session.commit()\n    await db_session.refresh(candidate)")
text = text.replace("@pytest.fixture\ndef test_candidate", "@pytest_asyncio.fixture\nasync def test_candidate")

# test_interview
text = text.replace("def test_interview(", "async def test_interview(")
text = text.replace("    db_session: Session, ", "    db_session: AsyncSession, ")
text = text.replace("@pytest.fixture\nasync def test_interview", "@pytest_asyncio.fixture\nasync def test_interview")
text = text.replace("    db_session.commit()\n    db_session.refresh(interview)", "    await db_session.commit()\n    await db_session.refresh(interview)")
text = text.replace("@pytest.fixture\ndef test_interview", "@pytest_asyncio.fixture\nasync def test_interview")

# create_test_... helpers
text = text.replace("def create_test_job_post(", "async def create_test_job_post(")
text = text.replace("db: Session,", "db: AsyncSession,")
text = text.replace("    db.commit()\n    db.refresh(job)", "    await db.commit()\n    await db.refresh(job)")

text = text.replace("def create_test_candidate(", "async def create_test_candidate(")
text = text.replace("    db.commit()\n    db.refresh(candidate)", "    await db.commit()\n    await db.refresh(candidate)")

text = text.replace("def create_test_interview(", "async def create_test_interview(")
text = text.replace("    db.commit()\n    db.refresh(interview)", "    await db.commit()\n    await db.refresh(interview)")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: conftest.py updated.")
