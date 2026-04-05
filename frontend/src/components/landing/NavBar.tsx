import React, { useState } from 'react';
import { Menu, X, ArrowRight } from 'lucide-react';

export default function NavBar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="fixed w-full z-50 bg-surface/80 backdrop-blur-lg border-b border-outline-variant/30 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => window.location.hash = '#/'}>
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
              <span className="text-on-primary font-bold text-xl">IX</span>
            </div>
            <span className="font-headline font-bold text-xl tracking-tight text-on-surface">Intervux AI</span>
          </div>
          
          <div className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-sm font-medium text-on-surface-variant hover:text-primary transition-colors">Platform</a>
            <a href="#workflow" className="text-sm font-medium text-on-surface-variant hover:text-primary transition-colors">How it Works</a>
            <a href="#pricing" className="text-sm font-medium text-on-surface-variant hover:text-primary transition-colors">Pricing</a>
          </div>

          <div className="hidden md:flex items-center gap-4">
            <button onClick={() => window.location.hash = '#/login'} className="text-sm font-medium text-on-surface hover:text-primary transition-colors px-4 py-2">
              Log in
            </button>
            <button onClick={() => window.location.hash = '#/signup'} className="text-sm font-medium bg-primary text-on-primary px-5 py-2.5 rounded-full hover:bg-on-primary-fixed-variant hover:shadow-lg hover:shadow-primary/20 transition-all duration-300 flex items-center gap-2 group">
              Start Hiring
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

          <div className="md:hidden flex items-center">
            <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="text-on-surface p-2">
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden absolute top-20 left-0 w-full bg-surface border-b border-outline-variant/30 shadow-lg animate-fade-up">
          <div className="px-4 py-6 space-y-4">
            <a href="#features" className="block text-base font-medium text-on-surface" onClick={() => setMobileMenuOpen(false)}>Platform</a>
            <a href="#workflow" className="block text-base font-medium text-on-surface" onClick={() => setMobileMenuOpen(false)}>How it Works</a>
            <a href="#pricing" className="block text-base font-medium text-on-surface" onClick={() => setMobileMenuOpen(false)}>Pricing</a>
            <div className="pt-4 border-t border-outline-variant/30 flex flex-col gap-3">
              <button onClick={() => { setMobileMenuOpen(false); window.location.hash = '#/login'; }} className="w-full text-center text-sm font-medium text-on-surface px-4 py-3 border border-outline-variant rounded-full">
                Log in
              </button>
              <button onClick={() => { setMobileMenuOpen(false); window.location.hash = '#/signup'; }} className="w-full text-center text-sm font-medium bg-primary text-on-primary px-4 py-3 rounded-full flex items-center justify-center gap-2">
                Start Hiring <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
