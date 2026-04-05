

export default function CandidateWorkflow() {
  return (
    <section className="bg-surface-container-low py-24 px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-20">
          <h2 className="text-4xl font-bold text-slate-900 mb-4">Architecting better hiring outcomes</h2>
          <p className="text-slate-500 max-w-2xl mx-auto">We've removed the manual friction and replaced it with editorial-grade insights that empower your talent teams.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-surface-container-lowest p-8 rounded-3xl xl:hover:-translate-y-2 transition-all duration-300 group">
            <div className="w-12 h-12 bg-primary-fixed flex items-center justify-center rounded-2xl mb-6 group-hover:scale-110 transition-transform">
              <span className="material-symbols-outlined text-primary" data-icon="videocam">videocam</span>
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-3">Seamless Capture</h3>
            <p className="text-slate-600 text-sm leading-relaxed">Connect your favorite meeting tools. Intervux records and transcribes every interview with enterprise-grade security.</p>
          </div>
          <div className="bg-surface-container-lowest p-8 rounded-3xl xl:hover:-translate-y-2 transition-all duration-300 group">
            <div className="w-12 h-12 bg-secondary-fixed flex items-center justify-center rounded-2xl mb-6 group-hover:scale-110 transition-transform">
              <span className="material-symbols-outlined text-on-secondary-fixed-variant" data-icon="psychology">psychology</span>
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-3">Neural Analysis</h3>
            <p className="text-slate-600 text-sm leading-relaxed">Our AI models extract intent, sentiment, and soft-skill signals that often go unnoticed by human interviewers.</p>
          </div>
          <div className="bg-surface-container-lowest p-8 rounded-3xl xl:hover:-translate-y-2 transition-all duration-300 group">
            <div className="w-12 h-12 bg-tertiary-fixed flex items-center justify-center rounded-2xl mb-6 group-hover:scale-110 transition-transform">
              <span className="material-symbols-outlined text-on-tertiary-fixed-variant" data-icon="summarize">summarize</span>
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-3">Instant Reports</h3>
            <p className="text-slate-600 text-sm leading-relaxed">Generate comprehensive candidate profiles with a skills matrix and bias-reduced scoring in seconds.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
