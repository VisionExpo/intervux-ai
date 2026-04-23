# LLM Layer: Reliability & Safety

LLM outputs are inherently non-deterministic and "untrusted." The LLM Layer in Intervux AI is designed to wrap these outputs in a safety harness.

## 🛡 Key Safety Patterns

### 1. `run_safe_json_task`
- **Files**: `backend/core/llm_brain.py`.
- **Problem**: LLMs often append conversational text or invalid JSON.
- **Solution**: A regex-based extraction layer that isolates JSON blocks, combined with Pydantic validation. If validation fails, it triggers a "Repair Pass" automatically.

### 2. Provider Fallback & Circuit Breakers
- **Providers**: Primary (Google Gemini), Fallback (OpenAI/Local).
- **Circuit Breaker**: If 3 consecutive requests to the primary provider fail or time out, the "Circuit Opens," and all traffic is routed to the fallback for a cooldown period (e.g., 60 seconds). This prevents system-wide cascading failures.

### 3. Pydantic v2 Validation
- Every LLM response is validated against a strictly defined schema. 
- **Example**: An evaluation must contain a `float` score and a `List[str]` of feedback. If it returns a string for a score, Pydantic catches it immediately, preventing downstream database crashes.

## 🔗 Code Mapping

### Component: LLM Service
- **Files**: `backend/services/llm_service.py`.
- **What it does**: High-level API for structured LLM interactions.
- **Why it exists**: Provides a clean interface for other services without them needing to know about provider switching or regex logic.
- **Connects to**: `LLM Brain`.

### Component: LLM Brain (Low Level)
- **Files**: `backend/core/llm_brain.py`.
- **What it does**: Direct integration with SDKs (Google GenAI), fallback logic, and circuit breaker implementation.
- **Why it exists**: The technical "hardened" core of the AI system.

## 🧠 Why this matters for SaaS
In a production SaaS environment, "99.9% uptime" is expected. Since AI APIs are prone to rate-limiting and intermittent downtime, this multi-layered safety approach ensures that Intervux AI remains "up" even when its AI providers are "down."
