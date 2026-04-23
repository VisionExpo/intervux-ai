# 🎤 How to Explain This System (Interview Guide)

This guide provides three levels of depth for explaining Intervux AI to recruiters and technical interviewers.

---

## ⏱ The 2-Minute "Elevator Pitch"
"Intervux AI is a production-grade AI platform that automates first-round technical interviews. I built a real-time, low-latency system where candidates interact with a 3D avatar that adapts its questions based on their resume and real-time responses. The system doesn't just record answers—it uses a multi-pass AI evaluation pipeline to analyze the candidate's reasoning, technical depth, and consistency across the session. Architecturally, it’s a FastAPI-based backend with a stateful WebSocket gateway, supported by Celery workers for async audio and AI processing, ensuring a smooth, human-like interaction."

---

## 🏗 The 5-Minute Technical Deep Dive

1.  **Orchestration & Scale**: "The backend uses an **App Factory pattern** to handle modular concerns like security, observability, and domain-specific routing. This allows us to scale individual modules like the 'Interview Engine' separately from the 'Recruiter Dashboard'."
2.  **Real-Time Challenges**: "The biggest challenge was low-latency audio synchronization. I implemented a custom **Viseme Engine** that maps LLM-generated text to mouth shapes, which are streamed via WebSockets alongside audio chunks. This ensures perfect lip-sync even under varying network conditions."
3.  **State Management**: "To handle disconnects, I built a **Stateless-at-Runtime** architecture. Every phase transition is persisted to Redis (Lazy Persistence). If a candidate's internet drops, the session re-hydrates instantly upon reconnection, so no data or progress is ever lost."
4.  **AI Reliability**: "I didn't trust raw LLM output. I implemented a **Safety Layer** that uses Pydantic validation, regex extraction, and an automated 'Repair Pass' for malformed JSON. If the primary LLM provider (Gemini) is down, a **Circuit Breaker** automatically flips traffic to a fallback provider."
5.  **The Evaluation Engine**: "The evaluation isn't just a single prompt. It’s a **Multi-Pass Pipeline**. We analyze reasoning, score competencies, and then perform a 'Consistency Check' to see if the candidate's answers contradict each other. This results in a high-fidelity report that recruiters can actually trust."

---

## 💡 Key Technical Highlights (Buzzwords that hit hard)
- **"App Factory Pattern"**: Shows you understand professional Python architecture.
- **"Circuit Breaker & Fallbacks"**: Shows you design for failure (SRE mindset).
- **"Lazy Persistence"**: Shows you understand I/O optimization and Redis performance.
- **"Viseme Synchronization"**: Shows you can handle complex front-to-back real-time problems.
- **"Multi-Pass Reasoning"**: Shows you are thinking about AI quality, not just "connecting an API."

---

## ❓ Potential Interviewer Questions

**Q: How did you handle WebSocket latency?**
> A: "By decoupling transcription and synthesis into Celery tasks and using a chunk-based streaming approach. We don't wait for the whole audio to finish—we stream audio and visemes in small packets to the frontend immediately."

**Q: Why use Redis for session state?**
> A: "Speed and re-hydration. PostgreSQL is our source of truth for records, but hitting a relational DB for every WebSocket chunk is inefficient. Redis gives us the sub-millisecond response time needed for a real-time state machine."

**Q: What happens if the LLM hallucinations?**
> A: "We use structured output validation via Pydantic. If the LLM returns data that doesn't fit our schema, the system catches it, logs it to our observability layer, and attempts a correction pass before falling back to a safe default."
