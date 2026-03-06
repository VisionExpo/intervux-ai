CREATE TABLE candidates (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    resume_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE interviews (
    id UUID PRIMARY KEY,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    overall_score FLOAT NOT NULL,
    technical_score FLOAT NOT NULL,
    communication_score FLOAT NOT NULL,
    problem_solving_score FLOAT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NOT NULL
);

CREATE TABLE interview_questions (
    id UUID PRIMARY KEY,
    interview_id UUID NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    score FLOAT NOT NULL,
    feedback TEXT NOT NULL
);

CREATE TABLE interview_events (
    id UUID PRIMARY KEY,
    interview_id UUID NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_interviews_candidate_id ON interviews(candidate_id);
CREATE INDEX idx_questions_interview_id ON interview_questions(interview_id);
CREATE INDEX idx_events_interview_id ON interview_events(interview_id);
CREATE INDEX idx_events_type ON interview_events(event_type);
