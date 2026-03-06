import { useMemo, useState } from "react";

import type { ReplaySegment } from "./types";

interface InterviewReplayProps {
  segments: ReplaySegment[];
}

export default function InterviewReplay({ segments }: InterviewReplayProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const activeSegment = useMemo(
    () => segments[activeIndex] ?? null,
    [activeIndex, segments]
  );

  if (!segments.length) {
    return (
      <section className="panel">
        <h2>Interview Replay</h2>
        <p>No replay segments available for this interview.</p>
      </section>
    );
  }

  return (
    <section className="panel">
      <h2>Interview Replay</h2>
      <div className="replay-tabs">
        {segments.map((segment, index) => (
          <button
            key={`${segment.question}-${index}`}
            type="button"
            onClick={() => setActiveIndex(index)}
            className={index === activeIndex ? "active" : ""}
          >
            Q{index + 1}
          </button>
        ))}
      </div>

      {activeSegment && (
        <div className="replay-card">
          <h3>{activeSegment.question}</h3>
          <audio controls preload="none">
            <source src={activeSegment.candidate_audio} />
            Your browser does not support audio playback.
          </audio>
          <p>
            <strong>Transcript:</strong> {activeSegment.transcript}
          </p>
          <div className="metric-row">
            <span>Technical: {activeSegment.evaluation.technical.toFixed(1)}</span>
            <span>Clarity: {activeSegment.evaluation.clarity.toFixed(1)}</span>
            <span>Reasoning: {activeSegment.evaluation.reasoning.toFixed(1)}</span>
          </div>
        </div>
      )}
    </section>
  );
}
