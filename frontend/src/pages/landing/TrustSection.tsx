import React from 'react';

export const TrustSection: React.FC = () => {
  return (
    <section className="py-16 bg-surface-container-low/50">
      <div className="max-w-7xl mx-auto px-8">
        <p className="text-center font-label text-xs font-bold uppercase tracking-[0.2em] text-outline mb-12">
          Trusted by Global Talent Leaders
        </p>
        <div className="flex flex-wrap justify-center items-center gap-12 md:gap-24 opacity-50 grayscale hover:grayscale-0 transition-all">
          <span className="font-headline font-extrabold text-2xl">SOLARIS</span>
          <span className="font-headline font-extrabold text-2xl">QUANTUM</span>
          <span className="font-headline font-extrabold text-2xl">HYPERION</span>
          <span className="font-headline font-extrabold text-2xl">NEXUS</span>
          <span className="font-headline font-extrabold text-2xl">EQUINOX</span>
        </div>
      </div>
    </section>
  );
};
