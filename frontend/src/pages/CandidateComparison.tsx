import type { CandidateComparisonRow } from "./types";

interface CandidateComparisonProps {
  rows: CandidateComparisonRow[];
}

export default function CandidateComparison({ rows }: CandidateComparisonProps) {
  return (
    <section className="panel">
      <h2>Candidate Comparison</h2>
      <table className="comparison-table">
        <thead>
          <tr>
            <th>Candidate</th>
            <th>Technical</th>
            <th>Communication</th>
            <th>Overall</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.candidate_id}>
              <td>{row.candidate_name}</td>
              <td>{row.technical.toFixed(1)}</td>
              <td>{row.communication.toFixed(1)}</td>
              <td>{row.overall.toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
