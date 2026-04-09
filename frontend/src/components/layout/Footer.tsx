import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-slate-200/50 dark:border-slate-800/50 bg-slate-50 dark:bg-slate-950">
      <div className="flex flex-col md:flex-row justify-between items-center px-8 py-12 max-w-7xl mx-auto gap-8">
        <div className="flex flex-col gap-4 items-center md:items-start">
          <span className="text-lg font-bold text-slate-900 dark:text-white font-headline">Intervux AI</span>
          <p className="font-body text-xs font-medium text-slate-500 dark:text-slate-400">© 2024 Intervux AI. All rights reserved.</p>
        </div>
        <div className="flex gap-8">
          <a className="font-body text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors" href="#">Product</a>
          <a className="font-body text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors" href="#">Documentation</a>
          <a className="font-body text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors" href="#">Careers</a>
          <a className="font-body text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors" href="#">Contact</a>
          <a className="font-body text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-slate-900 dark:text-white" href="#">Legal</a>
        </div>
      </div>
    </footer>
  );
};
