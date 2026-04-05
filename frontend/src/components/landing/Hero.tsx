

export default function Hero() {
  return (
    <section className="pt-32 pb-20 px-8 max-w-7xl mx-auto">
      <div className="grid lg:grid-cols-2 gap-16 items-center">
        <div className="z-10">
          <span className="inline-block px-4 py-1.5 bg-primary-fixed text-on-primary-fixed-variant rounded-full text-xs font-bold tracking-wider mb-6">AI-DRIVEN RECRUITING</span>
          <h1 className="text-display-lg font-extrabold text-slate-900 leading-tight mb-6" style={{ fontSize: '3.5rem' }}>Hire with intelligence, not just <span className="text-primary italic">instinct</span>.</h1>
          <p className="text-lg text-slate-600 mb-8 max-w-lg leading-relaxed">Intervux AI transforms your interview process into a high-precision data engine. Automate candidate scoring, analyze sentiment, and find your perfect fit in half the time.</p>
          <div className="flex flex-wrap gap-4">
            <button onClick={() => window.location.hash = '#/signup'} className="bg-primary text-white px-8 py-4 rounded-xl font-bold flex items-center gap-2 hover:bg-primary/90 transition-all">
              Schedule a Demo
              <span className="material-symbols-outlined">arrow_forward</span>
            </button>
            <button className="bg-surface-container-high text-on-surface px-8 py-4 rounded-xl font-bold hover:bg-surface-container-highest transition-all">View Case Studies</button>
          </div>
          <div className="mt-12 flex items-center gap-4 opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mr-4">Trusted by leaders</p>
            <span className="text-xl font-bold">TECHFLOW</span>
            <span className="text-xl font-bold">LUMINA</span>
            <span className="text-xl font-bold">QUBIT</span>
          </div>
        </div>
        <div className="relative">
          <div className="absolute -inset-4 bg-primary-container/10 blur-3xl rounded-full"></div>
          <div className="relative bg-surface-container-lowest rounded-3xl p-4 shadow-2xl shadow-slate-200/50">
            <img alt="AI Intelligence Visual" className="w-full h-auto rounded-2xl object-cover aspect-square" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCtb8aYKgubD8BSP9w8ezF_Tvg9wK2hVU0T8nvXKR8WDnhSkrOInYzuiMzm5H98WBHrzgnPC5iOY1-adXGMrRWm8KAztW5AYnqCyoPCqOVXg0NM5s1sf4PWJXxTCoN5iv9fQo_bKTJz_1Hwg27wGtev4QJEHh3rhA99hdE98wivZCQ9dQzgDnUptaq44iUVZKGYqN4iaG4xkYaw7d7OQetLvAfwFw2NO2uDKE6Fl2tqGJ_J4Qju1rp9RHapaurhj812Mr4JGpuYmlM" />
            <div className="absolute -bottom-8 -left-8 bg-white p-6 rounded-2xl shadow-xl max-w-xs border border-slate-100">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-2 h-8 bg-primary rounded-full"></div>
                <span className="font-bold text-slate-900">AI Scoring Engine</span>
              </div>
              <p className="text-sm text-slate-500 leading-snug italic">"Candidate matches 94% of senior engineering competencies based on transcript analysis."</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
