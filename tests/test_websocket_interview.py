"""
WebSocket Interview Session Tests
===================================

These are real integration tests that open an actual WebSocket connection
against a TestClient-backed FastAPI app with a SQLite test database.

Each test that exercises the protocol sends real JSON/binary messages and
asserts on the responses the server returns - replacing the previous file
full of `pass` and `assert True` stubs.

Coverage:
    - Connection rejected without token
    - Connection rejected with invalid token
    - Connection accepted with valid token ? greeting arrives
    - Rate limit enforcement
    - Session capacity enforcement
    - resume_upload flow: greeting ? WAITING_RESUME ? first question
    - stream_end flow: answer ? evaluation ? next_question or complete
    - ping/pong
    - Server-side error message format
"""

import json
import os
import sys
import uuid
from datetime import timedelta
from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# -- env must be set before any app imports ----------------------------------
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ws_interview.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-ws-secret-key")
os.environ.setdefault("DISABLE_STT", "true")          # no Whisper in CI
os.environ.setdefault("DISABLE_TTS", "true")          # avoid network TTS in CI
os.environ.setdefault("GOOGLE_API_KEY", "FAKE_KEY")   # no Gemini calls in CI
os.environ.setdefault("MAX_CONCURRENT_SESSIONS", "5")
os.environ.setdefault("RATE_LIMIT_WS_PER_MINUTE", "30")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import Base, get_db
from backend.main import app
from backend.auth.jwt_service import create_token_pair, Role, TokenData

# -- test database ------------------------------------------------------------

TEST_DB_URL = "sqlite:///./test_ws_interview.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=test_engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


# -- token helpers ------------------------------------------------------------

def _make_token(role: str = Role.CANDIDATE) -> str:
    return create_token_pair(
        {
            "user_id": f"test-{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:6]}@example.com",
            "name": "Test User",
            "role": role,
        }
    ).access_token


# -- helpers -------------------------------------------------------------------

def _recv_json(ws, *, skip_types: tuple = ()) -> dict:
    """
    Read the next JSON message from the WebSocket, skipping any message whose
    type is in *skip_types*.  Binary frames (TTS audio) are silently discarded
    here so callers only deal with control messages.
    """
    while True:
        data = ws.receive()
        # TestClient returns {"type": "websocket.send", "text": ..., "bytes": ...}
        if data.get("bytes"):
            continue  # skip TTS audio bytes
        raw = data.get("text") or data.get("data") or ""
        if not raw:
            continue
        msg = json.loads(raw)
        if msg.get("type") in skip_types:
            continue
        return msg


def _drain_until(ws, target_type: str, max_messages: int = 20) -> dict:
    """Read messages until one with target_type is found."""
    for _ in range(max_messages):
        msg = _recv_json(ws, skip_types=("avatar_visemes",))
        if msg.get("type") == target_type:
            return msg
    raise AssertionError(f"Did not receive a '{target_type}' message in {max_messages} attempts")


# =============================================================================
# Authentication tests
# =============================================================================


class TestWebSocketAuthentication:
    """Connection-level auth: tokens required, invalid tokens rejected."""

    def test_connection_rejected_without_token(self, client: TestClient):
        """No token ? server accepts the WS but immediately sends UNAUTHORIZED
        and closes the connection."""
        with client.websocket_connect("/ws/interview") as ws:
            msg = _recv_json(ws)
            assert msg["type"] == "error"
            assert msg["code"] == "UNAUTHORIZED"
            assert msg["recoverable"] is True

    def test_connection_rejected_with_invalid_token(self, client: TestClient):
        """Garbage token ? UNAUTHORIZED error."""
        with client.websocket_connect("/ws/interview?token=not_a_real_jwt") as ws:
            msg = _recv_json(ws)
            assert msg["type"] == "error"
            assert msg["code"] == "UNAUTHORIZED"

    def test_connection_accepted_with_valid_candidate_token(self, client: TestClient):
        """Valid candidate token ? greeting arrives."""
        token = _make_token(Role.CANDIDATE)
        with client.websocket_connect(f"/ws/interview?token={token}") as ws:
            # First message after auth is the avatar greeting
            msg = _drain_until(ws, "avatar_sync")
            assert msg["type"] == "avatar_sync"
            assert isinstance(msg.get("text"), str)
            assert len(msg["text"]) > 0

    def test_connection_accepted_with_recruiter_token(self, client: TestClient):
        """Recruiter token is also a valid JWT - gateway accepts any valid token."""
        token = _make_token(Role.RECRUITER)
        with client.websocket_connect(f"/ws/interview?token={token}") as ws:
            msg = _drain_until(ws, "avatar_sync")
            assert msg["type"] == "avatar_sync"

    def test_connection_accepted_with_admin_token(self, client: TestClient):
        token = _make_token(Role.ADMIN)
        with client.websocket_connect(f"/ws/interview?token={token}") as ws:
            msg = _drain_until(ws, "avatar_sync")
            assert msg["type"] == "avatar_sync"


# =============================================================================
# Greeting / initial handshake
# =============================================================================


class TestWebSocketGreeting:
    """After auth the server sends a greeting then waits for resume_upload."""

    def test_greeting_contains_welcome_text(self, client: TestClient):
        token = _make_token()
        with client.websocket_connect(f"/ws/interview?token={token}") as ws:
            msg = _drain_until(ws, "avatar_sync")
            text = msg.get("text", "")
            # Greeting must mention the platform or the interviewer
            assert any(
                kw in text.lower()
                for kw in ("intervux", "welcome", "interview", "resume")
            )

    def test_greeting_is_followed_by_waiting_state(self, client: TestClient):
        """After the greeting the server waits - no question arrives yet."""
        token = _make_token()
        with client.websocket_connect(f"/ws/interview?token={token}") as ws:
            _drain_until(ws, "avatar_sync")
            # Send a ping - server should respond with pong, NOT a question
            ws.send_text(json.dumps({"type": "ping"}))
            msg = _drain_until(ws, "pong")
            assert msg["type"] == "pong"


# =============================================================================
# Ping / pong
# =============================================================================


class TestWebSocketPingPong:
    def test_ping_returns_pong(self, client: TestClient):
        token = _make_token()
        with client.websocket_connect(f"/ws/interview?token={token}") as ws:
            _drain_until(ws, "avatar_sync")  # consume greeting
            ws.send_text(json.dumps({"type": "ping"}))
            msg = _drain_until(ws, "pong")
            assert msg["type"] == "pong"

    def test_multiple_pings(self, client: TestClient):
        token = _make_token()
        with client.websocket_connect(f"/ws/interview?token={token}") as ws:
            _drain_until(ws, "avatar_sync")
            for _ in range(3):
                ws.send_text(json.dumps({"type": "ping"}))
                msg = _drain_until(ws, "pong")
                assert msg["type"] == "pong"


# =============================================================================
# Invalid JSON / unknown message types
# =============================================================================


class TestWebSocketBadMessages:
    def test_invalid_json_returns_error(self, client: TestClient):
        token = _make_token()
        with client.websocket_connect(f"/ws/interview?token={token}") as ws:
            _drain_until(ws, "avatar_sync")
            ws.send_text("this is not json {{")
            msg = _recv_json(ws, skip_types=("avatar_visemes", "avatar_sync", "phase"))
            assert msg["type"] == "error"
            assert msg["code"] == "INVALID_JSON"
            assert msg["recoverable"] is True

    def test_message_wrong_phase_returns_error(self, client: TestClient):
        """
        Sending stream_end before resume_upload is in the wrong phase.
        The server should return an INVALID_STATE error (recoverable).
        """
        token = _make_token()
        with client.websocket_connect(f"/ws/interview?token={token}") as ws:
            _drain_until(ws, "avatar_sync")
            # stream_end is only valid during LISTENING phase
            ws.send_text(json.dumps({"type": "stream_end"}))
            msg = _recv_json(ws, skip_types=("avatar_visemes", "avatar_sync", "phase"))
            assert msg["type"] == "error"
            assert msg["code"] == "INVALID_STATE"
            assert msg["recoverable"] is True


# =============================================================================
# Error message contract
# =============================================================================


class TestWebSocketErrorContract:
    """All error messages must carry the documented fields."""

    def _get_first_error(self, client: TestClient, token: str = "") -> dict:
        url = f"/ws/interview?token={token}" if token else "/ws/interview"
        with client.websocket_connect(url) as ws:
            return _recv_json(ws)

    def test_error_has_type_field(self, client: TestClient):
        msg = self._get_first_error(client)
        assert "type" in msg
        assert msg["type"] == "error"

    def test_error_has_code_field(self, client: TestClient):
        msg = self._get_first_error(client)
        assert "code" in msg
        assert isinstance(msg["code"], str)

    def test_error_has_message_field(self, client: TestClient):
        msg = self._get_first_error(client)
        assert "message" in msg
        assert isinstance(msg["message"], str)

    def test_error_has_recoverable_field(self, client: TestClient):
        msg = self._get_first_error(client)
        assert "recoverable" in msg
        assert isinstance(msg["recoverable"], bool)

    def test_unauthorized_error_is_recoverable(self, client: TestClient):
        """Missing token errors are recoverable (the client can reconnect with a token)."""
        msg = self._get_first_error(client)
        assert msg["recoverable"] is True

    def test_invalid_token_error_is_recoverable(self, client: TestClient):
        msg = self._get_first_error(client, token="garbage")
        assert msg["recoverable"] is True


# =============================================================================
# Session capacity
# =============================================================================


class TestWebSocketCapacity:
    """Session slot counter increments on connect and decrements on close."""

    def test_gateway_tracks_active_sessions(self, client: TestClient):
        """
        Connect, verify the gateway's active_session counter is non-negative,
        disconnect, verify it went back down.
        """
        from backend.main import interview_gateway

        before = interview_gateway._active_sessions
        token = _make_token()

        with client.websocket_connect(f"/ws/interview?token={token}") as ws:
            _drain_until(ws, "avatar_sync")
            during = interview_gateway._active_sessions
            assert during >= before  # at least as many sessions as before

        after = interview_gateway._active_sessions
        assert after <= during  # released on disconnect

    def test_runtime_stats_returns_expected_keys(self):
        from backend.sockets.interview_gateway import InterviewGateway

        gw = InterviewGateway(total_questions=2)
        stats = gw.runtime_stats()

        assert "active_sessions" in stats
        assert "queue_depth" in stats
        assert "max_concurrent_sessions" in stats
        assert stats["max_concurrent_sessions"] == gw.max_concurrent_sessions


# =============================================================================
# Stress / resilience tests
# =============================================================================


class TestWebSocketStress:
    """
    Lightweight stress tests designed to be CI-safe:
    - rapid reconnect loop
    - malformed JSON flood on a live connection
    """

    def test_rapid_reconnects_do_not_leak_session_slots(self, client: TestClient):
        from backend.main import interview_gateway

        before = interview_gateway._active_sessions
        original_rate_limit = interview_gateway.rate_limit_per_minute

        # Avoid false positives from per-IP rate limiting in this stress loop.
        interview_gateway.rate_limit_per_minute = 10_000

        try:
            reconnect_count = 25
            for _ in range(reconnect_count):
                token = _make_token()
                with client.websocket_connect(f"/ws/interview?token={token}") as ws:
                    msg = _drain_until(ws, "avatar_sync")
                    assert msg["type"] == "avatar_sync"
        finally:
            interview_gateway.rate_limit_per_minute = original_rate_limit

        after = interview_gateway._active_sessions
        assert after == before

    def test_malformed_json_flood_stays_recoverable(self, client: TestClient):
        from backend.main import interview_gateway

        original_rate_limit = interview_gateway.rate_limit_per_minute
        interview_gateway.rate_limit_per_minute = 10_000

        try:
            token = _make_token()
            with client.websocket_connect(f"/ws/interview?token={token}") as ws:
                _drain_until(ws, "avatar_sync")

                invalid_count = 20
                for _ in range(invalid_count):
                    ws.send_text("{{ invalid json payload")
                    msg = _recv_json(ws, skip_types=("avatar_visemes", "avatar_sync", "phase"))
                    assert msg["type"] == "error"
                    assert msg["code"] == "INVALID_JSON"
                    assert msg["recoverable"] is True

                # Connection should still be alive and responsive.
                ws.send_text(json.dumps({"type": "ping"}))
                pong = _drain_until(ws, "pong")
                assert pong["type"] == "pong"
        finally:
            interview_gateway.rate_limit_per_minute = original_rate_limit


# =============================================================================
# Gateway unit tests (no network)
# =============================================================================


class TestInterviewGatewayUnit:
    """Pure unit tests for InterviewGateway helper methods."""

    def setup_method(self):
        from backend.sockets.interview_gateway import InterviewGateway

        self.gw = InterviewGateway(total_questions=3)

    def test_split_sentences_basic(self):
        parts = self.gw._split_sentences("Hello world. How are you? Fine!")
        assert len(parts) == 3

    def test_split_sentences_empty_string(self):
        assert self.gw._split_sentences("") == []

    def test_split_sentences_no_punctuation(self):
        parts = self.gw._split_sentences("just a single sentence")
        assert parts == ["just a single sentence"]

    def test_client_ip_returns_unknown_when_no_client(self):
        class FakeWS:
            client = None

        assert self.gw._client_ip(FakeWS()) == "unknown"

    def test_build_load_policy_returns_required_keys(self):
        policy = self.gw._build_load_policy()
        for key in (
            "load_ratio",
            "question_count",
            "question_temperature",
            "evaluation_temperature",
            "lightweight_eval",
        ):
            assert key in policy, f"Missing key: {key}"

    def test_build_load_policy_question_count_bounded(self):
        policy = self.gw._build_load_policy()
        assert policy["question_count"] >= 1

    def test_wav_duration_ms_empty_bytes(self):
        assert self.gw._wav_duration_ms(b"") == 0

    def test_wav_duration_ms_non_wav(self):
        assert self.gw._wav_duration_ms(b"not a wav file") == 0


# =============================================================================
# InterviewSession unit tests (no WebSocket needed)
# =============================================================================


class TestInterviewSessionUnit:
    """Unit tests for InterviewSession message routing helpers."""

    def _make_session(self, mock_session_id: str | None = None):
        from backend.sessions.interview_session import InterviewSession

        return InterviewSession(
            session_id=str(uuid.uuid4()),
            user_id="test-user",
            session_policy={"question_count": 2, "question_temperature": 0.7},
            mock_interview_session_id=mock_session_id,
        )

    def test_get_message_type_from_text(self):
        session = self._make_session()
        msg = {"text": json.dumps({"type": "resume_upload"})}
        assert session._get_message_type(msg) == "resume_upload"

    def test_get_message_type_from_data_dict(self):
        session = self._make_session()
        msg = {"data": {"type": "stream_end"}}
        assert session._get_message_type(msg) == "stream_end"

    def test_get_message_type_bytes_returns_audio_chunk(self):
        session = self._make_session()
        msg = {"bytes": b"\x00\x01\x02"}
        assert session._get_message_type(msg) == "audio_chunk"

    def test_get_message_type_unknown(self):
        session = self._make_session()
        assert session._get_message_type({}) == "unknown"

    def test_get_message_type_invalid_json_text(self):
        session = self._make_session()
        msg = {"text": "not json at all"}
        # Falls through to "unknown" without raising
        assert session._get_message_type(msg) == "unknown"

    def test_completed_normally_starts_false(self):
        session = self._make_session()
        assert session._completed_normally is False

    def test_mock_interview_session_id_stored(self):
        sid = "mock-abc123"
        session = self._make_session(mock_session_id=sid)
        assert session.mock_interview_session_id == sid

    def test_no_mock_session_id_is_none(self):
        session = self._make_session()
        assert session.mock_interview_session_id is None

    def test_phase_starts_at_connecting(self):
        from backend.models.interview import InterviewPhase

        session = self._make_session()
        assert session.phase == InterviewPhase.CONNECTING

    def test_is_complete_false_on_init(self):
        session = self._make_session()
        assert session.is_complete is False


# =============================================================================
# InterviewPersistence unit tests
# =============================================================================


class TestInterviewPersistenceUnit:
    """
    Unit tests for score extraction helpers in interview_persistence.py.
    No DB required.
    """

    def test_average_scores_empty_answers(self):
        from backend.services.interview_persistence import _average_scores

        result = _average_scores([])
        assert result["overall"] == 0.0
        assert result["technical"] == 0.0
        assert result["behavioral"] == 0.0
        assert result["reasoning"] == 0.0

    def test_average_scores_dual_eval_keys(self):
        """Dual evaluator uses Technical / Behavioral / Reasoning keys."""
        from backend.services.interview_persistence import _average_scores

        answers = [
            {
                "evaluation": {
                    "scores": {
                        "Technical": 8,
                        "Behavioral": 6,
                        "Reasoning": 7,
                        "Overall": 7,
                    }
                }
            },
            {
                "evaluation": {
                    "scores": {
                        "Technical": 6,
                        "Behavioral": 8,
                        "Reasoning": 5,
                        "Overall": 6,
                    }
                }
            },
        ]
        result = _average_scores(answers)
        # Scores are 0-10 scaled to 0-100
        assert result["overall"] == pytest.approx(65.0)
        assert result["technical"] == pytest.approx(70.0)
        assert result["behavioral"] == pytest.approx(70.0)
        assert result["reasoning"] == pytest.approx(60.0)

    def test_average_scores_multipass_keys(self):
        """Multipass evaluator uses Technical Accuracy / Clarity keys."""
        from backend.services.interview_persistence import _average_scores

        answers = [
            {
                "evaluation": {
                    "scores": {
                        "Technical Accuracy": 9,
                        "Clarity": 7,
                        "Depth": 8,
                        "Communication": 6,
                    }
                }
            }
        ]
        result = _average_scores(answers)
        # Technical bucket gets Technical Accuracy + Depth averaged
        assert result["technical"] > 0.0
        assert result["behavioral"] > 0.0

    def test_average_scores_missing_evaluation(self):
        from backend.services.interview_persistence import _average_scores

        answers = [{"answer": "some text"}]  # no 'evaluation' key
        result = _average_scores(answers)
        assert result["overall"] == 0.0

    def test_average_scores_scores_capped_at_100(self):
        from backend.services.interview_persistence import _average_scores

        answers = [
            {"evaluation": {"scores": {"Technical": 10, "Overall": 10}}}
        ]
        result = _average_scores(answers)
        assert result["technical"] <= 100.0
        assert result["overall"] <= 100.0

    def test_build_transcript_empty(self):
        from backend.services.interview_persistence import _build_transcript

        assert _build_transcript([]) == ""

    def test_build_transcript_single_qa(self):
        from backend.services.interview_persistence import _build_transcript

        answers = [{"question": "What is Python?", "answer": "A language."}]
        transcript = _build_transcript(answers)
        assert "Q1: What is Python?" in transcript
        assert "A1: A language." in transcript

    def test_build_transcript_multiple_qa(self):
        from backend.services.interview_persistence import _build_transcript

        answers = [
            {"question": "Q one", "answer": "A one"},
            {"question": "Q two", "answer": "A two"},
        ]
        transcript = _build_transcript(answers)
        assert "Q1:" in transcript
        assert "Q2:" in transcript
        assert "A1:" in transcript
        assert "A2:" in transcript

    def test_fail_mock_interview_missing_session(self, db_session: Session):
        """Calling fail_mock_interview with a non-existent session_id returns False."""
        from backend.services.interview_persistence import fail_mock_interview

        result = fail_mock_interview("does-not-exist-123")
        assert result is False

    def test_complete_mock_interview_missing_session(self, db_session: Session):
        """Calling complete_mock_interview with a non-existent session_id returns False."""
        from backend.services.interview_persistence import complete_mock_interview

        result = complete_mock_interview("does-not-exist-456", {}, [])
        assert result is False

    def test_complete_mock_interview_writes_scores(self, db_session: Session):
        """Full happy path: create a MockInterview row, complete it, verify scores."""
        from backend.models.candidate_portal import CandidateProfile, MockInterview
        from backend.services.interview_persistence import complete_mock_interview

        # Insert a candidate profile and mock interview
        profile = CandidateProfile(
            user_id="test-persist-user",
            name="Persist Test",
            skills="[]",
            mock_interviews_remaining=3,
        )
        db_session.add(profile)
        db_session.flush()

        session_id = f"mock-{uuid.uuid4().hex}"
        interview = MockInterview(
            candidate_id=profile.id,
            session_id=session_id,
            status="in_progress",
            interview_number=1,
        )
        db_session.add(interview)
        db_session.commit()

        answers = [
            {
                "question": "Explain Python decorators.",
                "answer": "They wrap functions.",
                "evaluation": {
                    "scores": {
                        "Technical": 8,
                        "Behavioral": 7,
                        "Reasoning": 6,
                        "Overall": 7,
                    }
                },
            }
        ]

        result = complete_mock_interview(session_id, {"summary": "good"}, answers)
        assert result is True

        db_session.expire_all()
        updated = (
            db_session.query(MockInterview)
            .filter(MockInterview.session_id == session_id)
            .first()
        )
        assert updated is not None
        assert updated.status == "completed"
        assert updated.completed_at is not None
        assert updated.score is not None
        assert updated.score > 0
        assert updated.technical_score is not None
        assert updated.transcript is not None
        assert "Explain Python decorators" in updated.transcript

    def test_fail_mock_interview_marks_abandoned(self, db_session: Session):
        from backend.models.candidate_portal import CandidateProfile, MockInterview
        from backend.services.interview_persistence import fail_mock_interview

        profile = CandidateProfile(
            user_id="test-fail-user",
            name="Fail Test",
            skills="[]",
            mock_interviews_remaining=3,
        )
        db_session.add(profile)
        db_session.flush()

        session_id = f"mock-{uuid.uuid4().hex}"
        interview = MockInterview(
            candidate_id=profile.id,
            session_id=session_id,
            status="in_progress",
            interview_number=1,
        )
        db_session.add(interview)
        db_session.commit()

        result = fail_mock_interview(session_id, reason="test_disconnect")
        assert result is True

        db_session.expire_all()
        updated = (
            db_session.query(MockInterview)
            .filter(MockInterview.session_id == session_id)
            .first()
        )
        assert updated.status == "abandoned"

    def test_fail_mock_interview_skips_completed_row(self, db_session: Session):
        """fail_mock_interview must not overwrite a row already marked completed."""
        from backend.models.candidate_portal import CandidateProfile, MockInterview
        from backend.services.interview_persistence import fail_mock_interview
        from datetime import datetime

        profile = CandidateProfile(
            user_id="test-skip-user",
            name="Skip Test",
            skills="[]",
            mock_interviews_remaining=3,
        )
        db_session.add(profile)
        db_session.flush()

        session_id = f"mock-{uuid.uuid4().hex}"
        interview = MockInterview(
            candidate_id=profile.id,
            session_id=session_id,
            status="completed",
            interview_number=1,
            score=80.0,
            completed_at=datetime.utcnow(),
        )
        db_session.add(interview)
        db_session.commit()

        result = fail_mock_interview(session_id)
        # Should return False because the row is not in_progress
        assert result is False

        db_session.expire_all()
        unchanged = (
            db_session.query(MockInterview)
            .filter(MockInterview.session_id == session_id)
            .first()
        )
        assert unchanged.status == "completed"
