import React from 'react';

interface AIInsightsCardProps {
  recentActivity?: string[];
  skills?: string[];
}

export const AIInsightsCard: React.FC<AIInsightsCardProps> = ({
  recentActivity = [],
  skills = [],
}) => {
  const topSkills = skills.slice(0, 3);
  const hasActivity = recentActivity.length > 0;

  return (
    <div className="bg-primary/5 rounded-2xl p-8 flex flex-col justify-center border-l-4 border-primary">
      <div className="flex items-center gap-3 mb-4">
        <span className="material-symbols-outlined text-primary">psychology</span>
        <h3 className="font-bold font-headline text-primary">AI Insights</h3>
      </div>

      {hasActivity ? (
        <div className="mb-6">
          <p className="text-[10px] text-slate-400 font-bold uppercase mb-3 tracking-wider">Recent Activity</p>
          <ul className="space-y-2">
            {recentActivity.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-700 leading-relaxed">
                <span className="material-symbols-outlined text-primary text-sm mt-0.5" style={{ fontVariationSettings: "'FILL' 1" }}>
                  check_circle
                </span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="text-slate-700 leading-relaxed text-sm mb-6">
          Complete your profile and take a mock interview to receive personalized AI insights
          and recommendations for improving your candidacy.
        </p>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white/80 backdrop-blur p-4 rounded-xl">
          <p className="text-[10px] text-slate-400 font-bold uppercase mb-1">Key Skills</p>
          <p className="text-sm font-semibold text-slate-900">
            {topSkills.length > 0 ? topSkills.join(', ') : 'Upload resume'}
          </p>
        </div>
        <div className="bg-white/80 backdrop-blur p-4 rounded-xl">
          <p className="text-[10px] text-slate-400 font-bold uppercase mb-1">Next Step</p>
          <p className="text-sm font-semibold text-slate-900">
            {!hasActivity ? 'Complete Profile' : 'Practice Interview'}
          </p>
        </div>
      </div>
    </div>
  );
};
