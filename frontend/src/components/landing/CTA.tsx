

export default function CTA() {
  return (
    <section className="bg-white py-24 px-8 overflow-hidden rounded-t-[3rem] -mt-12 relative z-20">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-5xl md:text-6xl font-extrabold text-slate-900 mb-6 tracking-tight">Transform your hiring logic.</h2>
        <p className="text-xl text-slate-500 mb-10 max-w-2xl mx-auto leading-relaxed">Stop relying on gut feelings and start building teams based on data-driven intelligence. The future of talent acquisition is here.</p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button className="w-full sm:w-auto px-8 py-4 rounded-xl font-bold bg-primary text-white hover:bg-primary/90 transition-all flex items-center justify-center gap-2 group shadow-xl shadow-primary/20">
            Request a Demo
            <span className="material-symbols-outlined text-sm group-hover:translate-x-1 transition-transform">arrow_forward</span>
          </button>
          <button className="w-full sm:w-auto px-8 py-4 rounded-xl font-bold bg-surface-container-low text-slate-900 border border-slate-200 hover:bg-slate-100 transition-all">
            View Live Examples
          </button>
        </div>
      </div>
    </section>
  );
}
