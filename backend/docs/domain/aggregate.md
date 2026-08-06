# Aggregate Structure

This document details the internal entity and value object structure of the `InterviewAggregate`.

## InterviewAggregate (Root)

The root class orchestrating all mutations.

### Properties
- `id` (UUID): Unique identifier.
- `version` (int): Optimistic concurrency version.
- `status` (InterviewStatus): The current lifecycle state.
- `candidate` (CandidateVO): Value object representing the candidate.
- `session` (SessionMetadataVO): Metadata regarding the current execution.
- `timeline` (List[TimelineEvent]): Chronological log of major events.
- `conversation` (List[TranscriptMessage]): The ongoing chat history.
- `evaluation` (EvaluationState): Aggregated score and coverage.
- `pending_events` (List[DomainEvent]): Queue of unpublished events.

## Value Objects (VOs)

Value objects are immutable. Any change requires replacing the object entirely.

### CandidateVO
- `name` (str)
- `role_target` (str)
- `experience_level` (str)
- `resume_text` (str)

### SessionMetadataVO
- `started_at` (datetime)
- `completed_at` (datetime | null)

## Entities

Entities have their own lifecycle within the aggregate but are strictly controlled by the root.

### TranscriptMessage
- `id` (UUID)
- `speaker` ("ai" | "candidate")
- `text` (str)
- `timestamp` (datetime)
