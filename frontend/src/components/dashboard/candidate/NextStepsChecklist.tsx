import React from 'react';

interface Step {
  label: string;
  detail: string;
  status: 'done' | 'active' | 'pending';
  path?: string;
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
    path: '/profile',
  });

  // Complete profile
  const profileDone = profileScore >= 50;
  steps.push({
    label: 'Complete Profile',
    detail: profileDone ? `Profile score: ${profileScore.toFixed(0)}%` : 'Fill in your skills and experience',
    status: profileDone ? 'done' : resumeUploaded ? 'active' : 'pending',
    path: '/profile',
  });

  // Mock interview
  const interviewDone = mockInterviewScore > 0;
  steps.push({
    label: 'Practice Mock Interview',
    detail: interviewDone ? `Last score: ${mockInterviewScore.toFixed(0)}%` : 'Complete a mock interview to prepare',
    status: interviewDone ? 'done' : profileDone ? 'active' : 'pending',
    path: '/mock-interview',
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

  const handleStepClick = (step: Step) => {
    if (step.status === 'pending') {
      // In a real app, maybe show a toast
      return;
    }
    if (step.path) {
      window.location.hash = `#${step.path}`;
    }
  };

  return (
    <div className="col-span-12 lg:col-span-4 bg-surface-container-low rounded-2xl p-6 space-y-6">
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
            onClick={() => handleStepClick(step)}
            className={`flex items-start gap-4 p-3 rounded-xl transition-all duration-200
              ${step.status === 'done' ? 'bg-surface-container-lowest shadow-sm cursor-pointer hover:bg-white' : ''}
              ${step.status === 'active' ? 'bg-white ring-2 ring-primary shadow-md cursor-pointer hover:scale-[1.02] active:scale-95' : ''}
              ${step.status === 'pending' ? 'bg-slate-100/50 opacity-60 border border-dashed border-slate-200 cursor-not-allowed group' : ''}
            `}
          >
            <div className="flex-shrink-0 mt-0.5 relative">
              {step.status === 'done' && (
                <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
                  check_circle
                </span>
              )}
              {step.status === 'active' && (
                <span className="material-symbols-outlined text-primary animate-pulse">radio_button_checked</span>
              )}
              {step.status === 'pending' && (
                <>
                  <span className="material-symbols-outlined text-slate-300 group-hover:hidden">circle</span>
                  <span className="material-symbols-outlined text-slate-400 hidden group-hover:block text-sm">lock</span>
                </>
              )}
            </div>
            <div className="flex-1">
              <p className={`text-sm ${step.status === 'active' ? 'font-bold' : 'font-semibold'} text-slate-900 dark:text-slate-800 flex items-center gap-2`}>
                {step.label}
                {step.status === 'pending' && <span className="text-[9px] font-bold bg-slate-200 text-slate-500 px-1.5 py-0.5 rounded uppercase tracking-tighter">Locked</span>}
              </p>
              <p className={`text-xs leading-relaxed ${step.status === 'active' ? 'text-primary font-medium' : 'text-slate-400'}`}>
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
