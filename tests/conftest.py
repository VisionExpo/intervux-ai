import os
import json
import sys
import time
import socket
import urllib.request
import urllib.error
import subprocess
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

# Ensure repo root is importable when pytest runs from different working dirs.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Configure deterministic test env before importing backend modules.
TEST_DB_PATH = ROOT_DIR / "tests" / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ.setdefault("TELEMETRY_DB_ENABLED", "false")
os.environ.setdefault("TELEMETRY_JSONL_ENABLED", "false")

from backend.db.database import SessionLocal
from backend.models.recruiter_dashboard_models import Interview
from backend.scripts.seed_dashboard import seed_dashboard


@pytest.fixture(scope="session")
def client():
    def _find_free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    class Response:
        def __init__(self, status_code: int, body_text: str):
            self.status_code = status_code
            self.text = body_text

        def json(self):
            return json.loads(self.text) if self.text else {}

    class HttpClient:
        def __init__(self, base_url: str):
            self.base_url = base_url.rstrip("/")

        def _request(self, method: str, path: str, json_payload=None, headers=None):
            data = None
            req_headers = {}
            if headers:
                req_headers.update(headers)
            if json_payload is not None:
                data = json.dumps(json_payload).encode("utf-8")
                req_headers.setdefault("Content-Type", "application/json")
            url = f"{self.base_url}{path}"
            request = urllib.request.Request(
                url=url,
                data=data,
                headers=req_headers,
                method=method,
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as resp:
                    body = resp.read().decode("utf-8")
                    return Response(resp.status, body)
            except urllib.error.HTTPError as err:
                body = err.read().decode("utf-8")
                return Response(err.code, body)

        def get(self, path: str, headers=None):
            return self._request("GET", path, headers=headers)

        def post(self, path: str, json=None, headers=None):
            return self._request("POST", path, json_payload=json, headers=headers)

    port = _find_free_port()
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=str(ROOT_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    base_url = f"http://127.0.0.1:{port}"
    ready = False
    for _ in range(180):
        if proc.poll() is not None:
            break
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=2) as resp:
                if resp.status == 200:
                    ready = True
                    break
        except Exception:
            time.sleep(0.5)

    if not ready:
        proc.terminate()
        stdout = ""
        stderr = ""
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except Exception:
            pass
        raise RuntimeError(
            "Test server did not start in time.\n"
            f"stdout:\n{stdout}\n"
            f"stderr:\n{stderr}"
        )

    try:
        yield HttpClient(base_url=base_url)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()


@pytest.fixture(scope="session")
def admin_token(client):
    response = client.post(
        "/api/auth/login/json",
        json={"email": "admin@intervux.ai", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def recruiter_token(client):
    response = client.post(
        "/api/auth/login/json",
        json={"email": "recruiter@intervux.ai", "password": "recruiter123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def recruiter_headers(recruiter_token):
    return {"Authorization": f"Bearer {recruiter_token}"}


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def sample_interview_id() -> str:
    db: Session = SessionLocal()
    try:
        row = db.query(Interview.id).first()
        if row:
            return row[0]
    finally:
        db.close()

    seed_dashboard()

    db = SessionLocal()
    try:
        row = db.query(Interview.id).first()
        assert row is not None
        return row[0]
    finally:
        db.close()
