import React from 'react';

export const PricingSection: React.FC = () => {
  return (
    <section className="py-24 bg-surface-container-low">
      <div className="max-w-7xl mx-auto px-8">
        <div className="text-center mb-16">
          <h2 className="text-headline-md font-headline font-bold text-4xl mb-4">Predictable Pricing</h2>
          <p className="text-on-surface-variant">Scale your hiring without breaking the bank.</p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {/* Starter */}
          <div className="bg-surface-container-lowest p-10 rounded-[2rem] shadow-sm flex flex-col">
            <h3 className="font-bold text-xl mb-2">Starter</h3>
            <p className="text-on-surface-variant text-sm mb-6">For small teams and startups.</p>
            <div className="flex items-baseline gap-1 mb-8">
              <span className="text-4xl font-bold font-headline">$499</span>
              <span className="text-on-surface-variant">/mo</span>
            </div>
            <ul className="space-y-4 mb-10 flex-grow">
              <li className="flex items-center gap-3 text-sm">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span> 50 Interviews / mo
              </li>
              <li className="flex items-center gap-3 text-sm">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span> AI Transcription
              </li>
              <li className="flex items-center gap-3 text-sm">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span> Email Support
              </li>
            </ul>
            <a href="#/signup" className="block text-center w-full py-4 rounded-xl border border-outline-variant font-bold hover:bg-surface-container-low transition-all">
              Get Started
            </a>
          </div>
          
          {/* Growth */}
          <div className="bg-surface-container-lowest p-10 rounded-[2rem] shadow-xl border-2 border-primary relative flex flex-col">
            <span className="absolute top-0 right-10 -translate-y-1/2 bg-primary text-white px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest">
              Recommended
            </span>
            <h3 className="font-bold text-xl mb-2">Growth</h3>
            <p className="text-on-surface-variant text-sm mb-6">For rapidly expanding companies.</p>
            <div className="flex items-baseline gap-1 mb-8">
              <span className="text-4xl font-bold font-headline">$1,299</span>
              <span className="text-on-surface-variant">/mo</span>
            </div>
            <ul className="space-y-4 mb-10 flex-grow">
              <li className="flex items-center gap-3 text-sm">
                <span className="material-symbols-outlined text-primary text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span> 250 Interviews / mo
              </li>
              <li className="flex items-center gap-3 text-sm">
                <span className="material-symbols-outlined text-primary text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span> Advanced AI Analysis
              </li>
              <li className="flex items-center gap-3 text-sm">
                <span className="material-symbols-outlined text-primary text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span> API Access
              </li>
              <li className="flex items-center gap-3 text-sm">
                <span className="material-symbols-outlined text-primary text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span> Priority Support
              </li>
            </ul>
            <a href="#/signup" className="block text-center w-full py-4 rounded-xl bg-primary text-white font-bold hover:bg-primary/90 transition-all shadow-lg shadow-primary/20">
              Get Started
            </a>
          </div>
          
          {/* Enterprise */}
          <div className="bg-surface-container-lowest p-10 rounded-[2rem] shadow-sm flex flex-col">
            <h3 className="font-bold text-xl mb-2">Enterprise</h3>
            <p className="text-on-surface-variant text-sm mb-6">Custom solutions for massive scale.</p>
            <div className="flex items-baseline gap-1 mb-8">
              <span className="text-4xl font-bold font-headline">Custom</span>
            </div>
            <ul className="space-y-4 mb-10 flex-grow">
              <li className="flex items-center gap-3 text-sm">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span> Unlimited Interviews
              </li>
              <li className="flex items-center gap-3 text-sm">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span> Single Sign-On (SSO)
              </li>
              <li className="flex items-center gap-3 text-sm">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span> Custom Rubrics
              </li>
              <li className="flex items-center gap-3 text-sm">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span> Dedicated Account Manager
              </li>
            </ul>
            <a href="#/signup" className="block text-center w-full py-4 rounded-xl border border-outline-variant font-bold hover:bg-surface-container-low transition-all">
              Contact Sales
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};
