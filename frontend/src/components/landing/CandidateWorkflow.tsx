import React from 'react';
import { Mail, Calendar, Mic2, Star } from 'lucide-react';

export default function CandidateWorkflow() {
  const steps = [
    {
      icon: <Mail className="w-6 h-6 text-on-primary" />,
      title: "1. One-Click Invite",
      description: "Recruiter generates a custom 'Magic Link'. No account creation needed for candidates.",
      color: "bg-primary"
    },
    {
      icon: <Calendar className="w-6 h-6 text-on-primary" />,
      title: "2. Async Scheduling",
      description: "Candidates start the interview anytime, 24/7. Perfect for passive candidates.",
      color: "bg-accent"
    },
    {
      icon: <Mic2 className="w-6 h-6 text-on-primary" />,
      title: "3. Voice Interview",
      description: "An adaptive, 15-minute conversation covering background, skills, and scenarios.",
      color: "bg-success"
    },
    {
      icon: <Star className="w-6 h-6 text-on-primary" />,
      title: "4. Scored & Ranked",
      description: "You receive a structured evaluation, transcript, and audio recording immediately.",
      color: "bg-[#f59e0b]" // amber
    }
  ];

  return (
    <section id="workflow" className="py-24 bg-surface-container-lowest">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row items-center gap-16">
          <div className="flex-1">
            <h2 className="text-primary font-semibold tracking-wide uppercase text-sm mb-3">Seamless Experience</h2>
            <h3 className="font-headline text-3xl font-bold text-on-surface sm:text-4xl mb-6">A friction-free process for everyone</h3>
            <p className="text-lg text-on-surface-variant mb-10 max-w-lg">
              We've designed Intervux to be completely painless for candidates while giving recruiters highly structured, actionable data.
            </p>
            
            <div className="space-y-8">
              {steps.map((step, index) => (
                <div key={index} className="flex gap-6 relative">
                  {index !== steps.length - 1 && (
                    <div className="absolute left-6 top-14 bottom-[-2rem] w-px bg-outline-variant/50"></div>
                  )}
                  <div className={`w-12 h-12 rounded-full flex shrink-0 items-center justify-center shadow-lg ${step.color}`}>
                    {step.icon}
                  </div>
                  <div className="pt-2">
                    <h4 className="text-xl font-bold text-on-surface mb-2">{step.title}</h4>
                    <p className="text-on-surface-variant">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="flex-1 w-full max-w-lg relative">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-accent/10 rounded-full blur-[100px] -z-10"></div>
            {/* Visual Phone Mockup / Interview Screen */}
            <div className="relative mx-auto w-[320px] h-[650px] bg-surface rounded-[3rem] border-[8px] border-surface-container-high shadow-2xl overflow-hidden p-6 flex flex-col items-center">
              <div className="w-32 h-6 bg-surface-container-high rounded-full absolute top-0 -translate-y-1/2"></div>
              
              <div className="flex w-full justify-between items-center mt-6 mb-12">
                <div className="font-bold">Intervux AI</div>
                <div className="w-8 h-8 rounded-full border border-outline-variant flex items-center justify-center">?</div>
              </div>

              <div className="w-32 h-32 rounded-full overflow-hidden mb-8 border-4 border-primary/20 relative shadow-xl">
                 <img src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=200&h=200" alt="AI Interviewer" className="w-full h-full object-cover" />
                 <div className="absolute inset-0 bg-primary/10 mix-blend-overlay"></div>
              </div>

              <div className="text-center mb-16">
                 <h4 className="text-xl font-bold text-on-surface mb-2">Sarah</h4>
                 <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-success/10 text-success text-xs font-semibold">
                    <div className="w-2 h-2 rounded-full bg-success animate-pulse"></div> Active
                 </div>
              </div>

              <div className="w-full space-y-4">
                 <div className="bg-surface-container p-4 rounded-2xl rounded-tl-sm w-[85%] text-sm text-on-surface-variant">
                    Hi! I'm Sarah, your AI interviewer for the Senior Frontend Engineer position. Are you ready to begin?
                 </div>
                 <div className="bg-primary p-4 rounded-2xl rounded-tr-sm w-[85%] ml-auto text-sm text-on-primary">
                    Yes, I'm ready. Let's get started!
                 </div>
              </div>

              <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-16 h-16 rounded-full bg-error text-on-error flex items-center justify-center shadow-lg cursor-pointer hover:scale-105 transition-transform">
                <Mic2 className="w-8 h-8" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
