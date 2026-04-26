import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_db():
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://intervux:intervux@localhost:5432/intervux")
    print(f"Connecting to {db_url}...")
    engine = create_async_engine(db_url)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print("Database is UP!")
    except Exception as e:
        print(f"Database is DOWN: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_db())
