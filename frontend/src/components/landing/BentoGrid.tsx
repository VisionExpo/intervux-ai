
import { UserSearch, FileCheck, BrainCircuit, Mic, BarChart3 } from 'lucide-react';

export default function BentoGrid() {
  const features = [
    {
      title: "Natural Voice Conversations",
      description: "Our AI converses with candidate naturally, understanding context, nuance, and even brief pauses just like a human.",
      icon: <Mic className="w-6 h-6 text-primary" />,
      className: "md:col-span-2 md:row-span-2 bg-surface",
      visual: (
        <div className="mt-6 flex gap-2 items-end h-24 p-4 bg-surface-container rounded-xl">
          {['h-[40%]', 'h-[70%]', 'h-[45%]', 'h-[90%]', 'h-[65%]', 'h-[30%]', 'h-[80%]', 'h-[50%]', 'h-[100%]', 'h-[60%]'].map((h, i) => (
            <div key={i} className={`w-full bg-primary/40 rounded-t-sm transition-all duration-500 hover:bg-primary ${h}`}></div>
          ))}
        </div>
      )
    },
    {
      title: "Real-time Evaluation",
      description: "Candidates are scored dynamically against your custom rubric as they speak.",
      icon: <BrainCircuit className="w-6 h-6 text-accent" />,
      className: "bg-surface-container-low",
      visual: (
         <div className="mt-4 p-3 bg-surface rounded-lg flex items-center justify-between shadow-sm">
            <span className="text-sm font-medium">Technical Depth</span>
            <span className="text-success font-bold">8.5/10</span>
         </div>
      )
    },
    {
      title: "Secure & Compliant",
      description: "Enterprise-grade security with advanced prompt-injection defenses.",
      icon: <FileCheck className="w-6 h-6 text-success" />,
      className: "bg-surface-container-low"
    },
    {
      title: "Seamless ATS Integration",
      description: "Push candidate scores, transcripts, and audio recordings directly into your existing workflow.",
      icon: <UserSearch className="w-6 h-6 text-primary" />,
      className: "md:col-span-2 bg-surface",
      visual: (
         <div className="mt-6 flex justify-between items-center px-8 text-on-surface-variant">
            <div className="w-12 h-12 bg-surface-container-highest rounded-xl flex items-center justify-center font-bold">WF</div>
            <div className="flex-1 h-0.5 bg-outline-variant/50 mx-4 relative">
               <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-primary rounded-full animate-ping"></div>
            </div>
            <div className="w-12 h-12 bg-primary text-on-primary rounded-xl flex items-center justify-center font-bold">IX</div>
         </div>
      )
    },
    {
      title: "Deep Analytics",
      description: "Uncover hiring trends and eliminate unconscious bias across your interview process.",
      icon: <BarChart3 className="w-6 h-6 text-accent" />,
      className: "bg-surface-container-low"
    }
  ];

  return (
    <section id="features" className="py-24 bg-surface">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-primary font-semibold tracking-wide uppercase text-sm mb-3">Core Platform</h2>
          <h3 className="font-headline text-3xl font-bold text-on-surface sm:text-4xl">Everything you need to hire at scale</h3>
          <p className="mt-4 text-lg text-on-surface-variant">
            A complete suite of tools designed to automate your screening process without sacrificing candidate experience.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[250px]">
          {features.map((feature, index) => (
            <div key={index} className={`p-8 rounded-[2rem] border border-outline-variant/30 transition-all hover:shadow-lg hover:border-outline-variant/60 flex flex-col justify-between overflow-hidden group ${feature.className}`}>
              <div>
                <div className="w-12 h-12 rounded-xl bg-surface-container-highest flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-on-surface mb-2">{feature.title}</h3>
                <p className="text-on-surface-variant text-sm leading-relaxed max-w-sm">
                  {feature.description}
                </p>
              </div>
              {feature.visual && (
                 <div className="relative z-10 transition-transform group-hover:-translate-y-2">
                    {feature.visual}
                 </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
