

export default function BentoGrid() {
  return (
    <section className="py-24 px-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-end mb-12">
        <div className="max-w-lg">
          <h2 className="text-4xl font-bold text-slate-900 mb-4">Engineered for precision</h2>
          <p className="text-slate-600">The tools you need to move beyond standard interview notes and embrace hard data.</p>
        </div>
        <div className="hidden md:block">
          <a className="text-primary font-bold flex items-center gap-2 hover:gap-3 transition-all" href="#">Explore all features <span className="material-symbols-outlined">east</span></a>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-6 md:grid-rows-[auto_auto] gap-6 md:h-auto">
        {/* Sentiment Card */}
        <div className="md:col-span-3 bg-surface-container rounded-3xl p-8 relative overflow-hidden flex flex-col justify-between">
          <div className="z-10">
            <span className="inline-block px-3 py-1 bg-white/50 backdrop-blur rounded-full text-[10px] font-bold uppercase tracking-widest mb-4">Real-time Intelligence</span>
            <h3 className="text-2xl font-bold text-slate-900 mb-4">Candidate Sentiment Analysis</h3>
            <p className="text-slate-600 text-sm max-w-xs">Track enthusiasm, hesitance, and confidence levels throughout the conversation with our emotional AI layer.</p>
          </div>
          <div className="mt-8">
            <img alt="Sentiment Data" className="w-full h-40 object-cover rounded-2xl shadow-lg" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCk6nG_yIqxjdlYGOWqDoriOTdGAXu7pWne4Dwikbprqd2ltzVp0WQXIHNZOAY-Vu_Mr2Cj3YGtnvJJP2Zm8o5kWlr481Wx2YtyVy5KsZnYOJxxxMMMfZUwbUM3et25ZCmKEPraNFOenk2jbjB3WKquFhTztfbqcATkMeEEYSSybkpHMxgmDK0zoTNfvrrNArCr3nu2BreTuVD71KYUa9SuAdj7FU_qNtNq3CAWrG6q0_JDh2SVISM9hZpoX--L7wmL9T9ajprwGGQ" />
          </div>
        </div>
        {/* Skills Matrix */}
        <div className="md:col-span-3 bg-slate-900 rounded-3xl p-8 relative overflow-hidden">
          <h3 className="text-2xl font-bold text-white mb-4">Competency Skills Matrix</h3>
          <p className="text-slate-400 text-sm max-w-xs mb-8">Automatically map interview answers to specific role requirements and benchmark against top performers.</p>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-800 p-4 rounded-xl border border-slate-700">
              <div className="text-primary-fixed-dim text-xs font-bold mb-2">Technical Leadership</div>
              <div className="h-1 w-full bg-slate-700 rounded-full">
                <div className="h-1 w-4/5 bg-primary rounded-full"></div>
              </div>
            </div>
            <div className="bg-slate-800 p-4 rounded-xl border border-slate-700">
              <div className="text-primary-fixed-dim text-xs font-bold mb-2">Strategic Thinking</div>
              <div className="h-1 w-full bg-slate-700 rounded-full">
                <div className="h-1 w-1/2 bg-primary rounded-full"></div>
              </div>
            </div>
          </div>
          <div className="absolute bottom-[-20px] right-[-20px] opacity-20">
            <span className="material-symbols-outlined text-[120px] text-white" data-icon="grid_view">grid_view</span>
          </div>
        </div>
        {/* Automation */}
        <div className="md:col-span-2 bg-primary text-white rounded-3xl p-8 flex flex-col justify-center text-center">
          <span className="material-symbols-outlined text-4xl mb-4" data-icon="bolt">bolt</span>
          <h3 className="text-xl font-bold mb-2">Workflow Automation</h3>
          <p className="text-white/80 text-xs text-center max-w-[200px] mx-auto">Trigger follow-ups and update your ATS instantly based on AI outcome predictions.</p>
        </div>
        {/* Global Search */}
        <div className="md:col-span-4 bg-surface-container-high rounded-3xl p-8 flex flex-col sm:flex-row items-center justify-between overflow-hidden gap-8">
          <div className="max-w-xs">
            <h3 className="text-xl font-bold text-slate-900 mb-2">Universal Talent Search</h3>
            <p className="text-slate-600 text-sm">Search through years of interview transcripts with natural language queries like "Who had the best answer on scalability?"</p>
          </div>
          <div className="bg-white p-4 rounded-2xl shadow-md rotate-3 translate-x-12 min-w-[200px]">
            <div className="flex items-center gap-2 mb-2">
              <span className="w-3 h-3 rounded-full bg-primary"></span>
              <div className="h-2 w-24 bg-slate-100 rounded-full"></div>
            </div>
            <div className="h-2 w-32 bg-slate-50 rounded-full mb-1"></div>
            <div className="h-2 w-28 bg-slate-50 rounded-full"></div>
          </div>
        </div>
      </div>
    </section>
  );
}
