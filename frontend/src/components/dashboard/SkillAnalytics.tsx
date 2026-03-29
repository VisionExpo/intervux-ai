import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import type { SkillAnalyticsResponse } from "../../types";

interface SkillAnalyticsProps {
  analytics: SkillAnalyticsResponse | null;
}

export default function SkillAnalytics({ analytics }: SkillAnalyticsProps) {
  if (!analytics) {
    return (
      <section className="panel">
        <h2>Skill Analytics</h2>
        <p>Select a candidate to load skill distribution.</p>
      </section>
    );
  }

  const chartData = Object.entries(analytics.skills).map(([skill, score]) => ({
    skill: skill.replaceAll("_", " ").replace(/\b\w/g, (match) => match.toUpperCase()),
    score,
  }));

  return (
    <section className="panel">
      <h2>Skill Analytics</h2>
      <div className="chart-shell">
        <ResponsiveContainer width="100%" height={320}>
          <RadarChart cx="50%" cy="50%" outerRadius="65%" data={chartData}>
            <PolarGrid stroke="rgba(33, 45, 64, 0.25)" />
            <PolarAngleAxis dataKey="skill" tick={{ fill: "#21314a", fontSize: 12 }} />
            <Radar
              name="Score"
              dataKey="score"
              stroke="#c84630"
              fill="#c84630"
              fillOpacity={0.4}
            />
            <Tooltip />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
