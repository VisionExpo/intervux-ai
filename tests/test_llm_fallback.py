import pytest

from backend.core import llm_brain as lb


def test_run_json_task_falls_back_when_primary_is_unavailable(monkeypatch):
    calls: list[str] = []

    def fake_call_provider(provider: str, prompt: str, temperature: float, top_p: float = 1.0) -> str:
        calls.append(provider)
        if provider == "gemini":
            raise RuntimeError("Gemini is not configured: GOOGLE_API_KEY missing")
        return '{"ok": true}'

    monkeypatch.setattr(lb, "_provider_order", lambda: ["gemini", "qwen"])
    monkeypatch.setattr(lb, "_call_provider", fake_call_provider)
    monkeypatch.setattr(lb, "_is_circuit_open", lambda provider: False)

    payload, provider = lb._run_json_task("{}", dict, temperature=0.1)

    assert payload == {"ok": True}
    assert provider == "qwen"
    assert calls == ["gemini", "qwen"]


def test_run_json_task_does_not_fallback_for_non_retriable_error(monkeypatch):
    calls: list[str] = []

    def fake_call_provider(provider: str, prompt: str, temperature: float, top_p: float = 1.0) -> str:
        calls.append(provider)
        if provider == "gemini":
            raise RuntimeError("response schema mismatch")
        return '{"ok": true}'

    monkeypatch.setattr(lb, "_provider_order", lambda: ["gemini", "qwen"])
    monkeypatch.setattr(lb, "_call_provider", fake_call_provider)
    monkeypatch.setattr(lb, "_is_circuit_open", lambda provider: False)
    monkeypatch.setattr(lb, "LLM_FALLBACK_ON_ANY_ERROR", False)

    with pytest.raises(RuntimeError, match="response schema mismatch"):
        lb._run_json_task("{}", dict, temperature=0.1)

    assert calls == ["gemini"]


def test_prewarm_uses_fallback_provider_when_primary_fails(monkeypatch):
    calls: list[str] = []

    def fake_call_provider(provider: str, prompt: str, temperature: float, top_p: float = 1.0) -> str:
        calls.append(provider)
        if provider == "gemini":
            raise RuntimeError("service unavailable")
        return '{"status":"ok"}'

    monkeypatch.setattr(lb, "_provider_order", lambda: ["gemini", "qwen"])
    monkeypatch.setattr(lb, "_call_provider", fake_call_provider)
    monkeypatch.setattr(lb, "_is_circuit_open", lambda provider: False)
    monkeypatch.setattr(lb, "LLM_FALLBACK_ON_ANY_ERROR", False)

    lb.prewarm_llm()

    assert calls == ["gemini", "qwen"]
