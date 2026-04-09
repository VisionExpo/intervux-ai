import React from 'react';

export const WorkflowSection: React.FC = () => {
  return (
    <section className="py-24 bg-surface-container-low">
      <div className="max-w-7xl mx-auto px-8">
        <h2 className="text-headline-md font-headline font-bold text-center mb-20">The Intelligent Workflow</h2>
        <div className="relative">
          <div className="hidden lg:block absolute top-1/2 left-0 w-full h-0.5 bg-outline-variant/30 -translate-y-1/2"></div>
          <div className="grid lg:grid-cols-5 gap-8">
            <div className="relative bg-surface-container-lowest p-6 rounded-2xl shadow-sm z-10 text-center">
              <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center mx-auto mb-4 font-bold">1</div>
              <h4 className="font-bold mb-2">Candidate Joins</h4>
              <p className="text-xs text-on-surface-variant">Browser-based lobby, no software install required.</p>
            </div>
            
            <div className="relative bg-surface-container-lowest p-6 rounded-2xl shadow-sm z-10 text-center">
              <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center mx-auto mb-4 font-bold">2</div>
              <h4 className="font-bold mb-2">AI Asks</h4>
              <p className="text-xs text-on-surface-variant">Adaptive questioning based on resume context.</p>
            </div>
            
            <div className="relative bg-surface-container-lowest p-6 rounded-2xl shadow-sm z-10 text-center">
              <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center mx-auto mb-4 font-bold">3</div>
              <h4 className="font-bold mb-2">Responses Evaluated</h4>
              <p className="text-xs text-on-surface-variant">Real-time analysis of sentiment and expertise.</p>
            </div>
            
            <div className="relative bg-surface-container-lowest p-6 rounded-2xl shadow-sm z-10 text-center">
              <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center mx-auto mb-4 font-bold">4</div>
              <h4 className="font-bold mb-2">Recruiter Scorecard</h4>
              <p className="text-xs text-on-surface-variant">Full synthesis with clips and competency scores.</p>
            </div>
            
            <div className="relative bg-surface-container-lowest p-6 rounded-2xl shadow-sm z-10 text-center">
              <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center mx-auto mb-4 font-bold">5</div>
              <h4 className="font-bold mb-2">Admin Tracks</h4>
              <p className="text-xs text-on-surface-variant">Global performance metrics and ROI dashboard.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
