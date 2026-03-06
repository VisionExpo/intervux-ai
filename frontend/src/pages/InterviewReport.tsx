import type { CandidateInterviewReport } from "./types";

interface InterviewReportProps {
  report: CandidateInterviewReport | null;
}

export default function InterviewReport({ report }: InterviewReportProps) {
  if (!report) {
    return (
      <section className="panel">
        <h2>Candidate Report</h2>
        <p>Select a candidate to review interview scores and feedback.</p>
      </section>
    );
  }

  return (
    <section className="panel">
      <h2>Candidate Report</h2>
      <p className="muted">
        {report.candidate.name} - {report.interview.role}
      </p>
      <div className="score-grid">
        <div className="score-card">
          <span>Overall Score</span>
          <strong>{report.interview.overall_score.toFixed(1)} / 100</strong>
        </div>
        <div className="score-card">
          <span>Technical</span>
          <strong>{report.interview.technical_score.toFixed(1)}</strong>
        </div>
        <div className="score-card">
          <span>Communication</span>
          <strong>{report.interview.communication_score.toFixed(1)}</strong>
        </div>
        <div className="score-card">
          <span>Problem Solving</span>
          <strong>{report.interview.problem_solving_score.toFixed(1)}</strong>
        </div>
      </div>

      <h3>Question Breakdown</h3>
      <div className="question-grid">
        {report.questions.map((question) => (
          <article key={question.id} className="question-card">
            <div className="question-head">
              <strong>{question.question}</strong>
              <span>{question.score.toFixed(1)} / 10</span>
            </div>
            <p>{question.answer}</p>
            <p className="muted">Feedback: {question.feedback}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
