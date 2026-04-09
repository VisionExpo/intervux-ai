import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';

interface PerformanceSummaryProps {
  profileScore?: number;
  resumeScore?: number;
  interviewScore?: number;
}

interface SkillBar {
  label: string;
  pct: number;
  color: string;
}

export const PerformanceSummary: React.FC<PerformanceSummaryProps> = ({
  profileScore = 0,
  resumeScore = 0,
  interviewScore = 0,
}) => {
  const skills: SkillBar[] = [
    { label: 'Profile Completeness', pct: Math.min(profileScore, 100), color: 'bg-primary' },
    { label: 'Resume Quality', pct: Math.min(resumeScore, 100), color: 'bg-primary' },
    { label: 'Interview Performance', pct: Math.min(interviewScore, 100), color: interviewScore >= 70 ? 'bg-primary' : 'bg-tertiary' },
  ];

  const avgScore = Math.round((profileScore + resumeScore + interviewScore) / 3);
  const isHighlyRecommended = avgScore >= 70;

  return (
    <DashboardCard>
      <div className="flex justify-between items-start mb-8">
        <div>
          <h3 className="text-xl font-bold font-headline text-slate-900 dark:text-slate-800">Your Performance</h3>
          <p className="text-sm text-slate-500">Based on your profile and assessments</p>
        </div>
        {isHighlyRecommended && (
          <div className="px-3 py-1 bg-primary-fixed rounded-full text-on-primary-fixed-variant text-[10px] font-bold whitespace-nowrap">
            HIGHLY RECOMMENDED
          </div>
        )}
      </div>
      <div className="space-y-6">
        {skills.map(({ label, pct, color }) => (
          <div key={label} className="space-y-2">
            <div className="flex justify-between text-sm font-medium">
              <span className="text-slate-700 dark:text-slate-600">{label}</span>
              <span className={pct >= 70 ? 'text-primary' : 'text-tertiary'}>{pct.toFixed(0)}%</span>
            </div>
            <div className="w-full h-3 bg-surface-container-low rounded-full overflow-hidden">
              <div
                className={`h-full ${color} rounded-full transition-all duration-700`}
                style={{ width: `${pct}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </DashboardCard>
  );
};
