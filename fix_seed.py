import re

filepath = "backend/scripts/seed_dashboard.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Make seed_dashboard async
text = text.replace("def seed_dashboard() -> None:", "async def seed_dashboard() -> None:")
text = text.replace("from backend.db.database import Base, SessionLocal, engine", "from backend.db.database import Base, AsyncSessionLocal, engine\nfrom sqlalchemy import select")

old_db_start = """    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Candidate).count() > 0:
            print("Dashboard seed skipped: candidates already exist.")
            return"""
            
new_db_start = """    # Using run_sync to create tables in async environment
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Candidate))
        if len(res.all()) > 0:
            print("Dashboard seed skipped: candidates already exist.")
            return"""
text = text.replace(old_db_start, new_db_start)

text = text.replace("        db.flush()", "        await db.flush()")
text = text.replace("        db.commit()", "        await db.commit()")

old_finally = """        print("Dashboard seed completed.")
    finally:
        db.close()"""
new_finally = """        print("Dashboard seed completed.")"""
text = text.replace(old_finally, new_finally)

old_main = """if __name__ == "__main__":
    seed_dashboard()"""
new_main = """if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_dashboard())"""
text = text.replace(old_main, new_main)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: seed_dashboard.py replaced")
