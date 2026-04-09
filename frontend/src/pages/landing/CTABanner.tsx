import React from 'react';

export const CTABanner: React.FC = () => {
  return (
    <section className="py-24 px-8">
      <div className="max-w-7xl mx-auto bg-primary rounded-[3rem] p-12 lg:p-24 text-center relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-white/5 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3"></div>
        <h2 className="text-display-lg font-headline font-bold text-white mb-8 relative z-10">
          Start Building Smarter Hiring Workflows Today
        </h2>
        <div className="flex flex-wrap justify-center gap-6 relative z-10">
          <a href="#/signup" className="inline-block bg-white text-primary px-10 py-5 rounded-xl font-headline font-bold text-lg hover:bg-surface-container transition-all">
            Start Free Trial
          </a>
          <a href="#/signup" className="inline-block bg-primary-container text-white px-10 py-5 rounded-xl font-headline font-bold text-lg hover:bg-blue-700 transition-all border border-white/20">
            Book Live Demo
          </a>
        </div>
      </div>
    </section>
  );
};
