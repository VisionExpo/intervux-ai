# Interview Invariants

The `InterviewAggregate` enforces strict business rules (invariants) upon every mutation. If a Command attempts to violate an invariant, the Aggregate must raise a `DomainException`, preventing the mutation and aborting the transaction.

## Core Invariants

1. **Monotonic Versioning**: The aggregate version must increment by exactly `1` on every successful state mutation.
2. **Immutable Events**: Once a Domain Event is appended to `pending_events`, it cannot be modified or removed (only cleared after publishing).
3. **Sequential Progression**: An interview cannot skip mandatory lifecycle states (e.g., cannot transition from `Created` directly to `Completed` without `Greeting`).
4. **Question Monotonicity**: The `question_index` can only increase or remain the same; it can never decrease.
5. **Evaluation Dependency**: An `Evaluation` cannot be generated or attached unless a corresponding `Recording` (candidate answer) exists for that specific question index.
6. **Completion Freeze**: Once the interview transitions to `Completed`, all further state-mutating commands (e.g., `AskQuestionCommand`, `ProcessAnswerCommand`) must be explicitly rejected.
7. **Single Active State**: There can only be one active question and one active workspace at any given time.
8. **Greeting Requirement**: An interview cannot be marked as `Completed` if the `Greeting` state was never reached.

These invariants form the basis of the Domain Unit Tests (`tests/domain/test_interview_aggregate.py`).
