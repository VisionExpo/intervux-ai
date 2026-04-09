import React from 'react';

export const TopNavbar: React.FC = () => {
  return (
    <nav className="fixed top-0 w-full z-50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl shadow-sm dark:shadow-none">
      <div className="flex justify-between items-center px-8 py-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-8">
          <a href="#/" className="text-xl font-bold tracking-tighter text-slate-900 dark:text-white font-headline hover:opacity-80 transition-opacity">Intervux AI</a>
          <div className="hidden md:flex gap-6">
            <a className="font-headline text-sm font-semibold tracking-tight text-slate-600 dark:text-slate-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors duration-200" href="#/features">Features</a>
            <a className="font-headline text-sm font-semibold tracking-tight text-slate-600 dark:text-slate-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors duration-200" href="#/pricing">Pricing</a>
            <a className="font-headline text-sm font-semibold tracking-tight text-slate-600 dark:text-slate-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors duration-200" href="#/solutions">Solutions</a>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <a href="#/login" className="font-headline text-sm font-semibold tracking-tight text-slate-600 dark:text-slate-400 hover:text-blue-700 transition-colors duration-200">Login</a>
          <a href="#/signup" className="inline-block bg-surface-container-high text-on-surface px-5 py-2.5 rounded-xl font-headline text-sm font-semibold tracking-tight hover:scale-95 active:opacity-80 transition-all">Book Demo</a>
          <a href="#/signup" className="inline-block bg-primary text-on-primary px-5 py-2.5 rounded-xl font-headline text-sm font-semibold tracking-tight hover:scale-95 active:opacity-80 transition-all">Get Started</a>
        </div>
      </div>
    </nav>
  );
};
