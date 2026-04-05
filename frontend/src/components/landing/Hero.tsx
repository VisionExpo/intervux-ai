import React from 'react';
import { ArrowRight, Sparkles, Play, Users, Clock, ShieldCheck } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-primary/20 rounded-full blur-[120px] -z-10 mix-blend-multiply opacity-70"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div className="text-center max-w-4xl mx-auto mb-16 animate-fade-up">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-primary/20 bg-primary/5 text-primary text-sm font-medium mb-8">
            <Sparkles className="w-4 h-4" />
            <span>Next-Generation AI Interviewer</span>
          </div>
          
          <h1 className="font-headline text-5xl lg:text-7xl font-bold tracking-tight text-on-surface mb-8 leading-[1.1]">
            Scale Your Hiring Operations with{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent relative inline-block">
              Cognitive AI
              <div className="absolute -bottom-2 left-0 w-full h-3 bg-primary/20 -z-10 transform -rotate-1"></div>
            </span>
          </h1>
          
          <p className="text-xl text-on-surface-variant mb-10 max-w-2xl mx-auto leading-relaxed">
            Replace preliminary phone screens with fully autonomous, conversational AI interviews. Evaluate technical skills, cultural fit, and problem-solving without human intervention.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button onClick={() => window.location.hash = '#/signup'} className="w-full sm:w-auto px-8 py-4 bg-primary text-on-primary rounded-full font-medium shadow-xl shadow-primary/25 hover:shadow-2xl hover:-translate-y-0.5 transition-all flex items-center justify-center gap-2 text-lg">
              Start Free Trial <ArrowRight className="w-5 h-5" />
            </button>
            <button className="w-full sm:w-auto px-8 py-4 bg-surface text-on-surface border border-outline-variant rounded-full font-medium hover:bg-surface-variant transition-all flex items-center justify-center gap-2 text-lg">
              <Play className="w-5 h-5" fill="currentColor" /> Watch Interactive Demo
            </button>
          </div>
          
          <div className="mt-10 flex items-center justify-center gap-8 text-sm text-on-surface-variant font-medium">
            <div className="flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-success" /> SOC2 Compliant</div>
            <div className="flex items-center gap-2"><Users className="w-4 h-4 text-primary" /> 10k+ Interviews Hosted</div>
            <div className="flex items-center gap-2 hidden sm:flex"><Clock className="w-4 h-4 text-accent" /> Setup in 5 Minutes</div>
          </div>
        </div>

        {/* Dashboard Preview */}
        <div className="relative mx-auto mt-20 rounded-[2rem] border border-outline-variant/30 bg-surface shadow-2xl p-2 sm:p-4 lg:p-6 animate-fade-up stagger-2 backdrop-blur-sm z-10">
          <div className="absolute -inset-1 bg-gradient-to-r from-primary/30 to-accent/30 rounded-[2.5rem] blur opacity-30 -z-10"></div>
          <div className="rounded-2xl border border-surface-container overflow-hidden shadow-sm bg-surface-container-lowest">
            {/* Fake Browser Toolbar */}
            <div className="h-12 border-b border-surface-container bg-surface flex items-center px-4 gap-2">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-error"></div>
                <div className="w-3 h-3 rounded-full bg-[#f59e0b]"></div>
                <div className="w-3 h-3 rounded-full bg-success"></div>
              </div>
              <div className="mx-auto bg-surface-container-high rounded-md h-6 w-1/3 max-w-sm flex items-center px-3 justify-center text-xs text-on-surface-variant/50 font-medium">
                app.intervux.ai/dashboard
              </div>
            </div>
            
            <div className="flex h-[400px] md:h-[600px] overflow-hidden">
              {/* Fake Sidebar */}
              <div className="w-64 border-r border-surface-container bg-surface hidden md:block p-4">
                <div className="flex items-center gap-2 mb-8 px-2">
                   <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                    <span className="text-on-primary font-bold text-xs">IX</span>
                  </div>
                  <span className="font-bold">Intervux</span>
                </div>
                <div className="space-y-2">
                  <div className="h-10 bg-primary/10 text-primary rounded-lg flex items-center px-4 font-medium text-sm">Overview</div>
                  <div className="h-10 text-on-surface-variant flex items-center px-4 font-medium text-sm hover:bg-surface-variant/50 rounded-lg">Job Posts</div>
                  <div className="h-10 text-on-surface-variant flex items-center px-4 font-medium text-sm hover:bg-surface-variant/50 rounded-lg">Candidates <span className="ml-auto bg-primary text-on-primary text-[10px] px-2 py-0.5 rounded-full">New</span></div>
                  <div className="h-10 text-on-surface-variant flex items-center px-4 font-medium text-sm hover:bg-surface-variant/50 rounded-lg">Interviews</div>
                  <div className="h-10 text-on-surface-variant flex items-center px-4 font-medium text-sm hover:bg-surface-variant/50 rounded-lg">Analytics</div>
                </div>
              </div>
              
              {/* Fake Main Content */}
              <div className="flex-1 bg-surface-container-lowest p-6 overflow-hidden relative">
                <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-primary/5 rounded-full blur-[80px]"></div>
                
                <div className="flex justify-between items-center mb-8">
                  <div>
                    <h2 className="text-2xl font-bold">Good morning, Recruiter</h2>
                    <p className="text-on-surface-variant text-sm">Here's what's happening with your interviews today.</p>
                  </div>
                  <div className="flex gap-4">
                    <div className="h-10 w-40 bg-surface-variant rounded-lg animate-pulse"></div>
                    <div className="h-10 w-10 bg-primary/10 rounded-lg flex items-center justify-center">
                       <span className="w-5 h-5 block bg-primary rounded-full"></span>
                    </div>
                  </div>
                </div>
                
                {/* Stats Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
                  {[
                    { label: 'Total Candidates', value: '1,248', change: '+12%', color: 'from-primary/10 to-transparent border-primary/20 text-primary' },
                    { label: 'Completed Interviews', value: '856', change: '+24%', color: 'from-accent/10 to-transparent border-accent/20 text-accent' },
                    { label: 'Avg. Score', value: '7.8/10', change: '+0.4', color: 'from-success/10 to-transparent border-success/20 text-success' }
                  ].map((stat, i) => (
                    <div key={i} className={`p-6 rounded-2xl border bg-gradient-to-b ${stat.color} transition-transform hover:-translate-y-1`}>
                      <div className="text-sm font-medium opacity-80 mb-2 mt-4">{stat.label}</div>
                      <div className="text-3xl font-bold flex items-end gap-3">
                        {stat.value}
                        <span className="text-sm font-medium bg-surface/50 px-2 py-1 rounded-md mb-1">{stat.change}</span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Main Panel Content */}
                <div className="grid grid-cols-3 gap-6 h-full">
                   <div className="col-span-2 border border-surface-container rounded-xl bg-surface p-6 h-[250px] shadow-sm flex flex-col justify-between relative overflow-hidden">
                      <div className="font-semibold mb-4 z-10 relative text-on-surface">Recent Candidates</div>
                      <div className="flex-1 space-y-3 z-10 relative">
                         {[1, 2, 3].map(i => (
                            <div key={i} className="flex items-center justify-between p-3 rounded-lg border border-surface-container-high bg-surface-container-lowest transition-all hover:border-primary/30">
                              <div className="flex items-center gap-3">
                                 <div className="w-8 h-8 rounded-full bg-surface-variant"></div>
                                 <div>
                                   <div className="h-3 w-24 bg-surface-variant rounded mb-1.5"></div>
                                   <div className="h-2 w-16 bg-surface-container-highest rounded"></div>
                                 </div>
                              </div>
                              <div className="flex gap-2">
                                <div className="h-6 w-16 bg-success/10 border border-success/20 rounded-full"></div>
                                <div className="h-6 w-6 bg-surface-variant rounded-md"></div>
                              </div>
                            </div>
                         ))}
                      </div>
                   </div>
                   <div className="col-span-1 border border-surface-container rounded-xl bg-primary text-on-primary p-6 h-[250px] shadow-lg relative overflow-hidden">
                      <div className="absolute -right-10 -bottom-10 w-32 h-32 bg-on-primary/10 rounded-full blur-2xl"></div>
                      <div className="font-semibold opacity-90 mb-4 z-10">AI Evaluator Status</div>
                      <div className="flex items-center justify-center h-24 mb-4">
                        <div className="relative">
                          <div className="w-16 h-16 border-4 border-on-primary/20 rounded-full border-t-on-primary animate-spin"></div>
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-lg font-bold">12</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-sm text-center opacity-80 z-10">Active Interviews</div>
                   </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
