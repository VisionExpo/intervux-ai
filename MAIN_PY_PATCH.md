# main.py Resume Router Patch

Add the resume router import:

```python
from backend.api.routes.resume_routes import router as resume_router
```

Then mount it after existing router registrations:

```python
app.include_router(resume_router, prefix="/api/resume", tags=["resume"])
```
