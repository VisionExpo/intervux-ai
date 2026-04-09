import React from 'react';

interface Step {
  label: string;
  detail: string;
  status: 'done' | 'active' | 'pending';
}

interface NextStepsChecklistProps {
  resumeUploaded?: boolean;
  profileScore?: number;
  mockInterviewScore?: number;
}

function buildSteps(resumeUploaded: boolean, profileScore: number, mockInterviewScore: number): Step[] {
  const steps: Step[] = [];

  // Resume upload
  steps.push({
    label: 'Upload Resume',
    detail: resumeUploaded ? 'Resume analyzed' : 'Upload your resume to get started',
    status: resumeUploaded ? 'done' : 'active',
  });

  // Complete profile
  const profileDone = profileScore >= 50;
  steps.push({
    label: 'Complete Profile',
    detail: profileDone ? `Profile score: ${profileScore.toFixed(0)}%` : 'Fill in your skills and experience',
    status: profileDone ? 'done' : resumeUploaded ? 'active' : 'pending',
  });

  // Mock interview
  const interviewDone = mockInterviewScore > 0;
  steps.push({
    label: 'Practice Mock Interview',
    detail: interviewDone ? `Last score: ${mockInterviewScore.toFixed(0)}%` : 'Complete a mock interview to prepare',
    status: interviewDone ? 'done' : profileDone ? 'active' : 'pending',
  });

  // Ready for review
  const allDone = resumeUploaded && profileDone && interviewDone;
  steps.push({
    label: 'Ready for Review',
    detail: allDone ? 'Your profile is visible to recruiters' : 'Complete previous steps first',
    status: allDone ? 'done' : 'pending',
  });

  return steps;
}

export const NextStepsChecklist: React.FC<NextStepsChecklistProps> = ({
  resumeUploaded = false,
  profileScore = 0,
  mockInterviewScore = 0,
}) => {
  const steps = buildSteps(resumeUploaded, profileScore, mockInterviewScore);
  const completedCount = steps.filter((s) => s.status === 'done').length;
  const completionPct = Math.round((completedCount / steps.length) * 100);

  return (
    <div className="col-span-12 md:col-span-4 bg-surface-container-low rounded-2xl p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-bold font-headline text-slate-900 dark:text-slate-800">Next Steps</h3>
        <span className="text-[10px] font-bold bg-white px-2 py-1 rounded text-primary shadow-sm">
          {completionPct}% COMPLETE
        </span>
      </div>
      <div className="space-y-3">
        {steps.map((step) => (
          <div
            key={step.label}
            className={`flex items-start gap-4 p-3 rounded-xl transition-transform hover:scale-[1.02] cursor-pointer
              ${step.status === 'done' ? 'bg-surface-container-lowest shadow-sm' : ''}
              ${step.status === 'active' ? 'bg-white ring-2 ring-primary shadow-md' : ''}
              ${step.status === 'pending' ? 'bg-surface/50 opacity-60 border border-transparent' : ''}
            `}
          >
            {step.status === 'done' && (
              <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
                check_circle
              </span>
            )}
            {step.status === 'active' && (
              <span className="material-symbols-outlined text-primary">radio_button_checked</span>
            )}
            {step.status === 'pending' && (
              <span className="material-symbols-outlined text-slate-300">circle</span>
            )}
            <div>
              <p className={`text-sm ${step.status === 'active' ? 'font-bold' : 'font-semibold'} text-slate-900 dark:text-slate-800`}>
                {step.label}
              </p>
              <p className={`text-xs ${step.status === 'active' ? 'text-primary font-medium' : 'text-slate-400'}`}>
                {step.detail}
              </p>
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-slate-400 italic px-2 text-center pt-2">
        AI Tip: A complete profile increases your visibility to recruiters.
      </p>
    </div>
  );
};
