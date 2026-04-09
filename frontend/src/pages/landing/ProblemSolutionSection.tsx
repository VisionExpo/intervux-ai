import React from 'react';

export const ProblemSolutionSection: React.FC = () => {
  return (
    <section className="py-24 bg-surface">
      <div className="max-w-7xl mx-auto px-8">
        <div className="text-center mb-20">
          <h2 className="text-headline-md font-headline font-bold text-4xl mb-4">From Chaos to Clarity</h2>
          <p className="text-on-surface-variant max-w-2xl mx-auto">
            Traditional interviewing is broken. We rebuilt the experience from the ground up for the AI-first enterprise.
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-12">
          <div className="p-8 rounded-3xl bg-surface-container-low flex flex-col h-full">
            <div className="w-12 h-12 rounded-xl bg-error/10 text-error flex items-center justify-center mb-6">
              <span className="material-symbols-outlined">schedule</span>
            </div>
            <h3 className="text-xl font-bold mb-4">Scheduling Fatigue</h3>
            <p className="text-on-surface-variant mb-8 flex-grow">
              Coordinate weeks of back-and-forth for 30-minute screenings that could be automated.
            </p>
            <div className="p-4 bg-surface-container-lowest rounded-2xl border-l-4 border-primary">
              <p className="text-sm font-semibold text-primary">Intervux Solution</p>
              <p className="text-sm">24/7 autonomous screening sessions at the candidate's convenience.</p>
            </div>
          </div>
          
          <div className="p-8 rounded-3xl bg-surface-container-low flex flex-col h-full">
            <div className="w-12 h-12 rounded-xl bg-error/10 text-error flex items-center justify-center mb-6">
              <span className="material-symbols-outlined">psychology_alt</span>
            </div>
            <h3 className="text-xl font-bold mb-4">Interview Bias</h3>
            <p className="text-on-surface-variant mb-8 flex-grow">
              Human interviewers often rely on gut feel rather than objective data and structured rubrics.
            </p>
            <div className="p-4 bg-surface-container-lowest rounded-2xl border-l-4 border-primary">
              <p className="text-sm font-semibold text-primary">Intervux Solution</p>
              <p className="text-sm">Standardized scoring based on semantic analysis and skill verification.</p>
            </div>
          </div>
          
          <div className="p-8 rounded-3xl bg-surface-container-low flex flex-col h-full">
            <div className="w-12 h-12 rounded-xl bg-error/10 text-error flex items-center justify-center mb-6">
              <span className="material-symbols-outlined">summarize</span>
            </div>
            <h3 className="text-xl font-bold mb-4">Inconsistent Notes</h3>
            <p className="text-on-surface-variant mb-8 flex-grow">
              Messy, handwritten notes that lack context and fail to capture the nuance of a conversation.
            </p>
            <div className="p-4 bg-surface-container-lowest rounded-2xl border-l-4 border-primary">
              <p className="text-sm font-semibold text-primary">Intervux Solution</p>
              <p className="text-sm">Instant, high-fidelity transcripts and AI-generated synthesis scorecards.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
