import type { CandidateListItem } from "./types";

interface CandidateListProps {
  candidates: CandidateListItem[];
  selectedCandidateId: string | null;
  onSelectCandidate: (candidate: CandidateListItem) => void;
}

export default function CandidateList({
  candidates,
  selectedCandidateId,
  onSelectCandidate,
}: CandidateListProps) {
  return (
    <section className="panel">
      <h2>Candidate List</h2>
      <div className="candidate-list">
        {candidates.map((candidate) => (
          <button
            key={candidate.id}
            type="button"
            className={`candidate-card${selectedCandidateId === candidate.id ? " selected" : ""}`}
            onClick={() => onSelectCandidate(candidate)}
          >
            <div>
              <strong>{candidate.name}</strong>
              <p>{candidate.role}</p>
            </div>
            <span>{candidate.email}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
