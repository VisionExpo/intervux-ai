import React from 'react';

export const HeroSection: React.FC = () => {
  return (
    <header className="relative pt-32 pb-24 lg:pt-48 lg:pb-40 overflow-hidden bg-surface">
      <div className="max-w-7xl mx-auto px-8 grid lg:grid-cols-2 gap-16 items-center">
        <div className="relative z-10">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-container/10 text-primary font-label text-xs font-bold uppercase tracking-widest mb-6">
            <span className="material-symbols-outlined text-[14px]">bolt</span> New: Version 2.0 Released
          </span>
          <h1 className="text-display-lg font-headline font-bold text-on-surface tracking-tight leading-[1.1] mb-6 text-5xl lg:text-7xl">
            AI-Powered Interview <span className="text-primary">Intelligence</span> for Smarter Hiring
          </h1>
          <p className="text-lg text-on-surface-variant font-body leading-relaxed mb-10 max-w-xl">
            Automate candidate interviews, generate AI-powered scorecards, and help recruiters make faster, better hiring decisions with high-fidelity conversational intelligence.
          </p>
          <div className="flex flex-wrap gap-4">
            <button className="bg-primary hover:bg-primary/90 text-white px-8 py-4 rounded-xl font-headline font-bold text-base transition-all shadow-lg shadow-primary/20">
              Start Free Trial
            </button>
            <button className="bg-surface-container-lowest border border-outline-variant/30 text-on-surface px-8 py-4 rounded-xl font-headline font-bold text-base hover:bg-surface-container-low transition-all">
              Book Live Demo
            </button>
          </div>
        </div>
        
        <div className="relative">
          <div className="absolute -top-20 -right-20 w-96 h-96 bg-primary-container/20 blur-[120px] rounded-full"></div>
          <div className="bg-surface-container-lowest rounded-[2rem] shadow-2xl p-4 border border-outline-variant/10">
            <div className="bg-surface-container-low rounded-[1.5rem] p-6">
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-secondary-container"></div>
                  <div>
                    <p className="font-bold text-sm">Senior UI Designer</p>
                    <p className="text-xs text-on-surface-variant">Active Search • 42 Candidates</p>
                  </div>
                </div>
                <span className="material-symbols-outlined text-outline">more_horiz</span>
              </div>
              <div className="space-y-4">
                <div className="bg-surface-container-lowest p-4 rounded-xl flex items-center justify-between shadow-sm border border-outline-variant/10">
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-full bg-slate-200"></div>
                    <p className="font-semibold text-sm">Alex Rivera</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 bg-primary-fixed text-on-primary-fixed-variant rounded-full text-[10px] font-bold">98/100</span>
                    <span className="material-symbols-outlined text-primary text-sm">verified</span>
                  </div>
                </div>
                <div className="bg-surface-container-lowest p-4 rounded-xl flex items-center justify-between shadow-sm border border-outline-variant/10 opacity-70">
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-full bg-slate-200"></div>
                    <p className="font-semibold text-sm">Sarah Chen</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 bg-surface-container-high text-on-surface-variant rounded-full text-[10px] font-bold">84/100</span>
                  </div>
                </div>
              </div>
              <div className="mt-8 pt-8 border-t border-outline-variant/10">
                <h4 className="text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-4">AI Insights</h4>
                <div className="flex gap-2">
                  <div className="flex-1 h-2 bg-primary rounded-full"></div>
                  <div className="flex-1 h-2 bg-primary/40 rounded-full"></div>
                  <div className="flex-1 h-2 bg-primary/20 rounded-full"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
