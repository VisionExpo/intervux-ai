"""
Phase 2 regressions (audit 2026-11-22).

S7  upload hardening: no client filename on disk, magic-byte checks, hard size
    cap, generic errors; the interview WebSocket resume path uses the same rules
    and does not leave the session stuck when a file is rejected.
S11 log redaction: JWTs / bearer tokens / credential query params never reach logs.
S9  JWT_ALGORITHM is restricted to HMAC algorithms.
"""

import base64
import logging
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.core.logging.logger import RedactSecretsFilter, redact_secrets
from backend.core.security.upload_validation import (
    UploadRejected,
    file_extension,
    max_base64_length,
    read_validated_upload,
    safe_stored_filename,
    validate_upload_bytes,
)

PDF = b"%PDF-1.4\n1 0 obj << >> endobj\ntrailer << >>\n%%EOF\n"
DOCX = b"PK\x03\x04" + b"\x00" * 64
EXE = b"MZ\x90\x00" + b"\x00" * 64
REPO_ROOT = Path(__file__).resolve().parents[1]


class _FakeUpload:
    """Minimal async UploadFile stand-in for the validator."""

    def __init__(self, filename, content: bytes):
        self.filename = filename
        self._content = content
        self._pos = 0

    async def read(self, size: int = -1) -> bytes:
        if size is None or size < 0:
            size = len(self._content) - self._pos
        chunk = self._content[self._pos:self._pos + size]
        self._pos += len(chunk)
        return chunk


# =========================================================
# Validator unit tests
# =========================================================


class TestUploadValidator:
    @pytest.mark.asyncio
    async def test_valid_pdf_accepted(self):
        upload = await read_validated_upload(_FakeUpload("cv.PDF", PDF), {".pdf"})
        assert upload.extension == ".pdf"
        assert upload.content == PDF

    @pytest.mark.asyncio
    async def test_renamed_executable_rejected(self):
        with pytest.raises(HTTPException) as err:
            await read_validated_upload(_FakeUpload("resume.pdf", EXE), {".pdf"})
        assert err.value.status_code == 400

    @pytest.mark.asyncio
    async def test_disallowed_extension_rejected(self):
        with pytest.raises(HTTPException) as err:
            await read_validated_upload(_FakeUpload("payload.exe", EXE), {".pdf", ".docx"})
        assert err.value.status_code == 400

    @pytest.mark.asyncio
    async def test_oversize_rejected_without_reading_everything(self):
        upload = _FakeUpload("cv.pdf", PDF + b"x" * 5000)
        with pytest.raises(HTTPException) as err:
            await read_validated_upload(upload, {".pdf"}, max_bytes=1024)
        assert err.value.status_code == 413
        # Stopped at the cap (+ one chunk), not after consuming the whole stream.
        assert upload._pos <= 1024 + 64 * 1024

    @pytest.mark.asyncio
    async def test_empty_file_rejected(self):
        with pytest.raises(HTTPException) as err:
            await read_validated_upload(_FakeUpload("cv.pdf", b""), {".pdf"})
        assert err.value.status_code == 400

    @pytest.mark.asyncio
    async def test_text_with_nul_bytes_rejected(self):
        with pytest.raises(HTTPException):
            await read_validated_upload(_FakeUpload("cv.txt", b"hello\x00world"), {".txt"})
        ok = await read_validated_upload(_FakeUpload("cv.txt", "Résumé text".encode()), {".txt"})
        assert ok.extension == ".txt"

    @pytest.mark.parametrize(
        "name",
        ["..\\..\\..\\Windows\\evil.pdf", "../../etc/evil.pdf", "C:\\temp\\evil.pdf", "/abs/evil.pdf"],
    )
    def test_extension_taken_from_basename_and_stored_name_is_random(self, name):
        assert file_extension(name) == ".pdf"
        stored = safe_stored_filename(file_extension(name))
        assert re.fullmatch(r"[0-9a-f]{32}\.pdf", stored)

    def test_validate_upload_bytes_raises_user_safe_error(self):
        with pytest.raises(UploadRejected) as err:
            validate_upload_bytes("resume.docx", PDF, {".docx"})
        assert "does not match" in str(err.value)
        assert validate_upload_bytes("resume.docx", DOCX, {".docx"}).extension == ".docx"

    def test_max_base64_length_matches_encoding(self):
        assert len(base64.b64encode(b"x" * 300)) == max_base64_length(300)
        assert len(base64.b64encode(b"x" * 301)) > max_base64_length(300)


# =========================================================
# Route tests
# =========================================================


def _signup_candidate(client_sync) -> tuple[str, str]:
    email = f"up-{uuid.uuid4().hex[:8]}@example.com"
    resp = client_sync.post(
        "/api/candidate/signup",
        json={"name": "Upload User", "email": email, "password": "upload-pass-1"},
    )
    assert resp.status_code in (200, 201), resp.text
    token = resp.json()["access_token"]
    me = client_sync.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    return token, me.json()["id"]


class TestCandidateResumeRoute:
    def test_traversal_filename_is_not_used_on_disk(self, test_client: TestClient, monkeypatch):
        from backend.modules.candidate.routes import candidate_routes
        from backend.services.resume_parser_service import ParsedResume

        seen = {}

        def fake_parse(name, content):
            seen["name"], seen["content"] = name, content
            return ParsedResume()

        monkeypatch.setattr(candidate_routes, "parse_resume_from_bytes", fake_parse)
        token, user_id = _signup_candidate(test_client)
        upload_root = REPO_ROOT / "backend" / "modules" / "uploads"
        escaped = REPO_ROOT / "backend" / "pwned.pdf"

        resp = test_client.post(
            "/api/candidate/resume",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("..\\..\\..\\pwned.pdf", PDF, "application/pdf")},
        )
        try:
            assert resp.status_code == 200, resp.text
            stored = resp.json()["resume_url"].rsplit("/", 1)[-1]
            assert re.fullmatch(r"[0-9a-f]{32}\.pdf", stored)
            assert seen["name"] == stored and seen["content"] == PDF
            assert (upload_root / "resumes" / user_id / stored).is_file()
            assert not escaped.exists()
        finally:
            target = upload_root / "resumes" / user_id
            if target.is_dir():
                for f in target.iterdir():
                    f.unlink()
                target.rmdir()

    def test_wrong_magic_bytes_rejected(self, test_client: TestClient):
        token, _ = _signup_candidate(test_client)
        resp = test_client.post(
            "/api/candidate/resume",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("resume.pdf", EXE, "application/pdf")},
        )
        assert resp.status_code == 400


class TestLegacyResumeRoute:
    def test_parser_error_text_not_leaked(self, test_client: TestClient, candidate_headers, monkeypatch):
        from backend.modules.candidate.routes import resume_routes

        def boom(name, content):
            raise RuntimeError("internal detail C:\\secret\\path")

        monkeypatch.setattr(resume_routes, "parse_resume_from_bytes", boom)
        resp = test_client.post(
            "/api/resume/upload",
            headers=candidate_headers,
            files={"file": ("cv.pdf", PDF, "application/pdf")},
        )
        assert resp.status_code == 500
        assert resp.json()["detail"] == "Resume parsing failed."

    def test_legacy_route_checks_content(self, test_client: TestClient, candidate_headers):
        resp = test_client.post(
            "/api/resume/upload",
            headers=candidate_headers,
            files={"file": ("cv.pdf", EXE, "application/pdf")},
        )
        assert resp.status_code == 400


# =========================================================
# WebSocket resume path
# =========================================================


class TestWebSocketResumeValidation:
    def _session(self):
        from backend.modules.interview.sessions.interview_session import InterviewSession

        return InterviewSession(
            session_id=str(uuid.uuid4()),
            user_id="ws-upload-user",
            session_policy={"question_count": 2, "question_temperature": 0.7},
        )

    def test_validate_payload(self):
        from backend.modules.interview.sessions.interview_session import InterviewSession

        check = InterviewSession._validate_resume_payload
        assert check("cv.pdf", base64.b64encode(PDF).decode()) is None
        assert check("cv.exe", base64.b64encode(EXE).decode()) is not None
        assert check("cv.pdf", base64.b64encode(EXE).decode()) is not None
        assert check("cv.pdf", "not base64 !!!") is not None
        assert "too large" in check("cv.pdf", "A" * (max_base64_length() + 4))

    @pytest.mark.asyncio
    async def test_rejected_resume_keeps_session_waiting(self):
        from backend.modules.interview.models import InterviewPhase

        session = self._session()
        session.state.transition_to(InterviewPhase.WAITING_RESUME)

        async def must_not_be_called(*args, **kwargs):
            raise AssertionError("engine must not run for a rejected file")

        session.engine.start_interview = must_not_be_called
        result = await session._handle_resume_upload(
            {"type": "resume_upload",
             "data": {"file_name": "evil.pdf", "file_bytes": base64.b64encode(EXE).decode()}}
        )
        assert result["code"] == "INVALID_RESUME"
        assert result["recoverable"] is True
        assert session.state.phase == InterviewPhase.WAITING_RESUME
        assert not session.state.resume_processing


# =========================================================
# Log redaction
# =========================================================

JWT = "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoieCJ9.c2lnbmF0dXJlLXZhbHVl"


class TestLogRedaction:
    @pytest.mark.parametrize(
        "raw, secret",
        [
            (f"WebSocket /ws/interview?token={JWT}&mock_session_id=mock-1", JWT),
            ("GET /ws/interview?token=opaque-value-123 HTTP/1.1", "opaque-value-123"),
            ("Authorization: Bearer abc.def.ghi", "abc.def.ghi"),
            ("login password=hunter2&x=1", "hunter2"),
            (f"payload {JWT} trailing", JWT),
        ],
    )
    def test_secrets_removed(self, raw, secret):
        assert secret not in redact_secrets(raw)

    def test_innocent_text_untouched(self):
        line = "tokens_used=120 token_count=5 max_tokens=100 session=mock-1"
        assert redact_secrets(line) == line

    def test_filter_handles_uvicorn_style_args(self):
        record = logging.LogRecord(
            name="uvicorn.access", level=logging.INFO, pathname=__file__, lineno=1,
            msg='%s - "WebSocket %s" [accepted]',
            args=("127.0.0.1:5000", f"/ws/interview?token={JWT}"),
            exc_info=None,
        )
        assert RedactSecretsFilter().filter(record) is True
        assert JWT not in record.getMessage()
        assert "127.0.0.1:5000" in record.getMessage()

    def test_filter_installed_on_uvicorn_loggers(self):
        for name in ("uvicorn.access", "uvicorn.error"):
            assert any(isinstance(f, RedactSecretsFilter) for f in logging.getLogger(name).filters)


# =========================================================
# JWT algorithm restriction
# =========================================================


@pytest.mark.parametrize("algorithm", ["none", "RS256"])
def test_non_hmac_jwt_algorithm_refused_at_import(algorithm):
    env = dict(os.environ, JWT_SECRET_KEY="x" * 32, JWT_ALGORITHM=algorithm, ENV="test")
    result = subprocess.run(
        [sys.executable, "-c", "import backend.core.security.jwt_service"],
        cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode != 0
    assert "Unsupported JWT_ALGORITHM" in result.stderr
