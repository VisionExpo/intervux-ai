import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { EvaluationDashboardResponse } from "./types";

interface AIEvaluationDashboardProps {
  data: EvaluationDashboardResponse | null;
}

const PIE_COLORS = ["#c84630", "#1a2940", "#6b8e23", "#d08c00", "#387780"];

function StatCard({
  label,
  value,
  subtitle,
}: {
  label: string;
  value: string;
  subtitle?: string;
}) {
  return (
    <article className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
      {subtitle ? <p>{subtitle}</p> : null}
    </article>
  );
}

export default function AIEvaluationDashboard({ data }: AIEvaluationDashboardProps) {
  if (!data) {
    return (
      <section className="panel evaluation-panel">
        <h2>AI Evaluation Dashboard</h2>
        <p className="muted">No evaluation telemetry found yet. Complete interviews to populate this view.</p>
      </section>
    );
  }

  const qualityCards = [
    { label: "Accuracy", value: `${(data.model_quality.accuracy * 100).toFixed(1)}%` },
    { label: "Hallucination Rate", value: `${data.model_quality.hallucination_rate.toFixed(1)}%` },
    { label: "Consistency Score", value: data.model_quality.consistency_score.toFixed(2) },
    { label: "Reasoning Score", value: data.model_quality.reasoning_score.toFixed(2) },
  ];

  const performanceCards = [
    { label: "p50 Latency", value: `${data.performance.latency.p50.toFixed(2)}s` },
    { label: "p95 Latency", value: `${data.performance.latency.p95.toFixed(2)}s` },
    { label: "p99 Latency", value: `${data.performance.latency.p99.toFixed(2)}s` },
    { label: "Error Rate", value: `${data.performance.error_rate.toFixed(2)}%` },
    { label: "RPS", value: data.performance.throughput.requests_per_second.toFixed(2) },
    { label: "Tokens / Sec", value: data.performance.throughput.tokens_per_second.toFixed(2) },
  ];

  return (
    <section className="evaluation-stack">
      <section className="panel evaluation-panel">
        <div className="section-head">
          <div>
            <h2>AI Evaluation Dashboard</h2>
            <p className="muted">Generated {new Date(data.generated_at).toLocaleString()}</p>
          </div>
        </div>
        <div className="summary-callout">
          <h3>AI Hiring Summary</h3>
          <p>{data.ai_hiring_summary}</p>
        </div>
      </section>

      <section className="panel">
        <h2>Model Quality</h2>
        <div className="stat-grid">
          {qualityCards.map((item) => (
            <StatCard key={item.label} label={item.label} value={item.value} />
          ))}
        </div>
      </section>

      <section className="panel">
        <h2>Performance</h2>
        <div className="stat-grid">
          {performanceCards.map((item) => (
            <StatCard key={item.label} label={item.label} value={item.value} />
          ))}
        </div>
      </section>

      <section className="evaluation-two-col">
        <section className="panel">
          <h2>Token Usage</h2>
          <div className="stat-grid">
            <StatCard label="Avg Prompt Tokens" value={data.token_usage.average_prompt_tokens.toFixed(0)} />
            <StatCard label="Avg Completion Tokens" value={data.token_usage.average_completion_tokens.toFixed(0)} />
            <StatCard label="Total Tokens Today" value={data.token_usage.total_tokens_today.toString()} />
          </div>
        </section>

        <section className="panel">
          <h2>System Health</h2>
          <div className="stat-grid">
            <StatCard label="Active Sessions" value={data.system_health.active_interview_sessions.toFixed(0)} />
            <StatCard label="Queue Length" value={data.system_health.queue_length.toFixed(0)} />
            <StatCard label="GPU Allocated" value={`${data.system_health.gpu_memory_allocated_mb.toFixed(0)} MB`} />
            <StatCard label="GPU Reserved" value={`${data.system_health.gpu_memory_reserved_mb.toFixed(0)} MB`} />
          </div>
        </section>
      </section>

      <section className="evaluation-two-col">
        <section className="panel">
          <h2>Cost</h2>
          <div className="stat-grid">
            <StatCard label="Avg Cost / Request" value={`$${data.cost.average_cost_per_request.toFixed(4)}`} />
            <StatCard label="Daily AI Spend" value={`$${data.cost.daily_ai_spend.toFixed(2)}`} />
          </div>
          <div className="chart-shell">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data.cost.cost_by_model}>
                <XAxis dataKey="model" tick={{ fill: "#21314a", fontSize: 12 }} />
                <YAxis tick={{ fill: "#21314a", fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="cost" fill="#c84630" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="panel">
          <h2>Model Usage</h2>
          <div className="chart-shell">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={data.model_usage}
                  dataKey="percentage"
                  nameKey="model"
                  outerRadius={90}
                  innerRadius={45}
                  paddingAngle={3}
                >
                  {data.model_usage.map((entry, index) => (
                    <Cell key={entry.model} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number | string | undefined) =>
                    `${Number(value ?? 0).toFixed(2)}%`
                  }
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="legend-list">
            {data.model_usage.map((item, index) => (
              <div key={item.model} className="legend-row">
                <span className="legend-dot" style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }} />
                <strong>{item.model}</strong>
                <span>{item.percentage.toFixed(1)}% ({item.requests})</span>
              </div>
            ))}
          </div>
        </section>
      </section>

      <section className="evaluation-two-col">
        <section className="panel">
          <h2>Interview Metrics</h2>
          <div className="stat-grid">
            <StatCard label="Candidate Success Rate" value={`${data.interview_metrics.candidate_success_rate.toFixed(1)}%`} />
            <StatCard
              label="Avg Interview Time"
              value={`${data.interview_metrics.average_interview_duration_minutes.toFixed(1)} min`}
            />
          </div>
          <div className="chart-shell">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data.interview_metrics.skill_evaluation_distribution}>
                <XAxis dataKey="skill" tick={{ fill: "#21314a", fontSize: 12 }} />
                <YAxis tick={{ fill: "#21314a", fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="score" fill="#1a2940" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="panel">
          <h2>Alerts</h2>
          <div className="alert-list">
            {data.alerts.map((alert) => (
              <article key={alert.message} className={`alert-card alert-${alert.severity}`}>
                <strong>{alert.severity.toUpperCase()}</strong>
                <p>{alert.message}</p>
              </article>
            ))}
          </div>
        </section>
      </section>
    </section>
  );
}
