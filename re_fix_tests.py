import os
import re

TESTS_DIR = "tests"

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # The previous script broke indentation:
    #     @pytest.mark.asyncio
    # async def test_...
    # Let's fix it by matching the spaces before @pytest.mark.asyncio and applying them to async def test_.
    
    # There could be lines like:
    #     @pytest.mark.asyncio
    # async def test_...
    
    content = re.sub(r'(?m)^([ \t]*)@pytest\.mark\.asyncio\nasync def test_', r'\1@pytest.mark.asyncio\n\1async def test_', content)

    # Some decorators might be doubled:
    content = content.replace("@pytest.mark.asyncio\n    @pytest.mark.asyncio", "@pytest.mark.asyncio")
    content = content.replace("@pytest.mark.asyncio\n@pytest.mark.asyncio", "@pytest.mark.asyncio")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

for filename in os.listdir(TESTS_DIR):
    if filename.endswith(".py") and filename.startswith("test_"):
        process_file(os.path.join(TESTS_DIR, filename))

print("Fixed indentation in tests.")
