import os
import re

def migrate_to_async_sqlalchemy(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add select import if needed
    if "from sqlalchemy import" not in content and "db.query" in content:
        content = "from sqlalchemy import select\n" + content
    elif "from sqlalchemy import" in content and "select" not in content and "db.query" in content:
        content = re.sub(r'(from sqlalchemy import )', r'\1select, ', content, count=1)

    # 2. Replace db = SessionLocal() ... try: ... finally: db.close() 
    # This is tricky with regex because of indentation and try/finally blocks.
    # An easier path for async migration is to replace `db = SessionLocal()` with `async with AsyncSessionLocal() as db:`
    # and indent the body, removing try/finally.
    
    # 3. Replace db.query(Model).filter(...) -> await db.execute(select(Model).filter(...)).scalars()
    # Simple regex for db.query(X) -> (await db.execute(select(X)
    content = re.sub(
        r'db\.query\(([^)]+)\)',
        r'(await db.execute(select(\1)))',
        content
    )
    
    # Replace .first() with .scalars().first()
    content = re.sub(
        r'\)\.filter\(([^)]+)\)\.first\(\)',
        r'.filter(\1)).scalars().first()',
        content
    )
    
    # Replace .all() with .scalars().all()
    content = re.sub(
        r'\)\.filter\(([^)]+)\)\.all\(\)',
        r'.filter(\1)).scalars().all()',
        content
    )
    content = re.sub(
        r'\)\.all\(\)',
        r'.scalars().all()',
        content
    )
    
    # Replace db.commit() -> await db.commit()
    content = re.sub(r'db\.commit\(\)', r'await db.commit()', content)
    # Replace db.refresh(x) -> await db.refresh(x)
    content = re.sub(r'db\.refresh\(([^)]+)\)', r'await db.refresh(\1)', content)
    # db.add(x) remains db.add(x) in async sqlalchemy!

    # Replace SessionLocal with AsyncSessionLocal
    content = content.replace("SessionLocal", "AsyncSessionLocal")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
print("Migration functions loaded.")
