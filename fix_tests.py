import os
import re

TESTS_DIR = "tests"

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Add pytest mark if not present
    if "pytest.mark.asyncio" not in content and "test_" in os.path.basename(filepath):
        if "pytest" not in content:
            content = "import pytest\n" + content
        # we can just use @pytest.mark.asyncio on each function, or pytest_asyncio. 
        # Actually anyio or pytest.mark.asyncio works.
        # It's cleaner to just replace `def test_` with `@pytest.mark.asyncio\nasync def test_`
    
    # 1. replace def test_ to async def test_
    content = re.sub(r'(?<!async )def test_', r'@pytest.mark.asyncio\nasync def test_', content)
    
    # replace multiple decorators if we just added it to an already decorated one?
    content = content.replace("@pytest.mark.asyncio\n@pytest.mark.asyncio", "@pytest.mark.asyncio")

    # 2. replace client.get, client.post, client.put, client.delete, client.patch with await client...
    content = re.sub(r'(?<!await )client\.(get|post|put|delete|patch)\(', r'await client.\1(', content)
    
    # 3. replace create_test_... with await create_test_... for helpers
    content = re.sub(r'(?<!await )create_test_job_post\(', r'await create_test_job_post(', content)
    content = re.sub(r'(?<!await )create_test_candidate\(', r'await create_test_candidate(', content)
    content = re.sub(r'(?<!await )create_test_interview\(', r'await create_test_interview(', content)

    # 4. db interactions
    content = re.sub(r'(?<!await )db_session\.commit\(\)', r'await db_session.commit()', content)
    content = re.sub(r'(?<!await )db_session\.refresh\(', r'await db_session.refresh(', content)
    content = re.sub(r'(?<!await )db_session\.execute\(', r'await db_session.execute(', content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

for filename in os.listdir(TESTS_DIR):
    if filename.endswith(".py") and filename.startswith("test_"):
        process_file(os.path.join(TESTS_DIR, filename))

print("SUCCESS: Tests updated.")
