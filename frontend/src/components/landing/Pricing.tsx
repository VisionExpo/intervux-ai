import React from 'react';
import { Check } from 'lucide-react';

export default function Pricing() {
  return (
    <section id="pricing" className="py-24 bg-surface-container-highest">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="font-headline text-3xl font-bold text-on-surface sm:text-4xl mb-4">Transparent Pricing</h2>
          <p className="text-lg text-on-surface-variant">Simple, volume-based pricing. No hidden fees or complex tiers.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Starter Plan */}
          <div className="p-8 rounded-[2rem] bg-surface flex flex-col justify-between border border-outline-variant/30 hover:border-primary/50 transition-colors">
            <div>
              <h3 className="text-2xl font-bold text-on-surface mb-2">Growth</h3>
              <p className="text-on-surface-variant mb-6 h-12">Perfect for growing startups and agencies.</p>
              <div className="mb-8">
                <span className="text-4xl font-bold text-on-surface">$500</span>
                <span className="text-on-surface-variant">/month</span>
              </div>
              <ul className="space-y-4 mb-8">
                {['Up to 200 interviews / mo', 'Standard AI Voices (ElevenLabs)', 'Basic Evaluation Criteria', 'Email Support'].map((feature, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                      <Check className="w-3 h-3 text-primary" />
                    </div>
                    <span className="text-on-surface-variant">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
            <button onClick={() => window.location.hash = '#/signup'} className="w-full py-4 rounded-full border-2 border-primary text-primary font-medium hover:bg-primary hover:text-on-primary transition-colors">Start Free Trial</button>
          </div>

          {/* Scale Plan */}
          <div className="p-8 rounded-[2rem] bg-primary flex flex-col justify-between shadow-xl shadow-primary/20 relative">
            <div className="absolute top-0 right-8 -translate-y-1/2 px-4 py-1.5 bg-[#f59e0b] text-white text-xs font-bold rounded-full uppercase tracking-wider shadow-lg">Most Popular</div>
            <div>
              <h3 className="text-2xl font-bold text-on-primary mb-2">Enterprise</h3>
              <p className="text-on-primary/80 mb-6 h-12">For large-scale hiring teams with custom requirements.</p>
              <div className="mb-8">
                <span className="text-4xl font-bold text-on-primary">Custom</span>
              </div>
              <ul className="space-y-4 mb-8">
                {['Unlimited interviews', 'Custom Voice Cloning', 'Advanced Custom Rubrics & Calibrations', 'ATS Integrations (Greenhouse, Lever)', 'Dedicated Success Manager'].map((feature, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full bg-on-primary/20 flex items-center justify-center shrink-0">
                      <Check className="w-3 h-3 text-on-primary" />
                    </div>
                    <span className="text-on-primary/90">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
            <button className="w-full py-4 rounded-full bg-on-primary text-primary font-medium hover:bg-white hover:shadow-lg transition-all">Contact Sales</button>
          </div>
        </div>
      </div>
    </section>
  );
}
