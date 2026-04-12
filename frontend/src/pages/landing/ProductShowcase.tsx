import React from 'react';

export const ProductShowcase: React.FC = () => {
  return (
    <section className="py-32 bg-surface overflow-hidden">
      <div className="max-w-7xl mx-auto px-8">
        <div className="grid lg:grid-cols-2 gap-24 items-center">
          <div>
            <h2 className="text-display-lg font-headline font-bold text-5xl leading-tight mb-8">
              A Unified Workspace for the <span className="text-primary">Whole Team</span>
            </h2>
            <div className="space-y-8">
              <div className="flex gap-6">
                <div className="shrink-0 w-12 h-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                  <span className="material-symbols-outlined">person_search</span>
                </div>
                <div>
                  <h4 className="font-bold text-lg mb-1">Recruiter Dashboard</h4>
                  <p className="text-on-surface-variant">Manage pipelines with AI-prioritized rankings and deep-dive scorecards.</p>
                </div>
              </div>
              
              <div className="flex gap-6">
                <div className="shrink-0 w-12 h-12 rounded-xl bg-tertiary/10 text-tertiary flex items-center justify-center">
                  <span className="material-symbols-outlined">videocam</span>
                </div>
                <div>
                  <h4 className="font-bold text-lg mb-1">Candidate Environment</h4>
                  <p className="text-on-surface-variant">A premium, distraction-free interface that puts candidates at ease.</p>
                </div>
              </div>
              
              <div className="flex gap-6">
                <div className="shrink-0 w-12 h-12 rounded-xl bg-secondary/10 text-secondary flex items-center justify-center">
                  <span className="material-symbols-outlined">admin_panel_settings</span>
                </div>
                <div>
                  <h4 className="font-bold text-lg mb-1">Admin Control Center</h4>
                  <p className="text-on-surface-variant">Set organization-wide guardrails, rubrics, and compliance standards.</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="relative">
            <div className="bg-surface-container-high rounded-[2.5rem] p-4 lg:ml-12 shadow-2xl">
              <img 
                alt="Dashboard Mockup" 
                className="rounded-[2rem] w-full object-cover aspect-[4/3] shadow-inner" 
                src="/assets/hero-dashboard.png"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
