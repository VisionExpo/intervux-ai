from pydantic import BaseModel

class Test(BaseModel):
    name: str

t = Test(name="foo")
try:
    t.meta = {"source": "llm"}
    print(f"Meta added: {t.meta}")
except Exception as e:
    print(f"Error: {e}")
