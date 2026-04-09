import React from 'react';

interface HeroGreetingProps {
  userName: string;
  applicationStatus?: string;
  matchScore?: string;
  roleAppliedFor?: string;
}

export const HeroGreeting: React.FC<HeroGreetingProps> = ({
  userName,
  applicationStatus = 'Final Stage',
  matchScore = '94% AI Match',
  roleAppliedFor = 'Lead Cognitive Engineer',
}) => {
  return (
    <section className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-8">
      <div>
        <span className="text-primary font-semibold tracking-widest text-[10px] uppercase mb-2 block">
          Welcome Back
        </span>
        <h2 className="text-4xl font-bold font-headline text-slate-900 dark:text-slate-800">
          Hello, {userName}.
        </h2>
        <p className="text-slate-500 mt-2 max-w-md text-sm">
          Your next technical interview for the{' '}
          <span className="text-slate-900 dark:text-slate-700 font-semibold italic">{roleAppliedFor}</span>{' '}
          role is approaching.
        </p>
      </div>
      <div className="flex gap-4">
        <div className="px-6 py-4 bg-surface-container-lowest rounded-xl shadow-sm border-l-4 border-primary">
          <p className="text-xs text-slate-500 font-medium">Application Status</p>
          <p className="text-xl font-bold font-headline text-slate-900 dark:text-slate-800">{applicationStatus}</p>
        </div>
        <div className="px-6 py-4 bg-surface-container-lowest rounded-xl shadow-sm border-l-4 border-tertiary">
          <p className="text-xs text-slate-500 font-medium">Match Score</p>
          <p className="text-xl font-bold font-headline text-tertiary">{matchScore}</p>
        </div>
      </div>
    </section>
  );
};
