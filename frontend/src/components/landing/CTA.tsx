import React from 'react';
import { ArrowRight } from 'lucide-react';

export default function CTA() {
  return (
    <section className="py-24 bg-surface relative overflow-hidden">
      <div className="absolute inset-0 bg-primary/5"></div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-primary/20 rounded-full blur-[120px] -z-10"></div>
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative text-center">
        <h2 className="font-headline text-4xl font-bold text-on-surface sm:text-5xl mb-6">Ready to upgrade your hiring?</h2>
        <p className="text-xl text-on-surface-variant mb-10 max-w-2xl mx-auto">Join forward-thinking talent teams who use Intervux AI to interview faster, better, and more fairly.</p>
        
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button onClick={() => window.location.hash = '#/signup'} className="w-full sm:w-auto px-8 py-4 bg-primary text-on-primary rounded-full font-medium shadow-xl shadow-primary/25 hover:shadow-2xl hover:-translate-y-0.5 transition-all flex items-center justify-center gap-2 text-lg">
            Start Free Trial <ArrowRight className="w-5 h-5" />
          </button>
          <button className="w-full sm:w-auto px-8 py-4 bg-surface text-on-surface border border-outline-variant rounded-full font-medium hover:bg-surface-variant transition-all text-lg">
            Talk to Sales
          </button>
        </div>
      </div>
    </section>
  );
}
