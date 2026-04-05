

export default function Pricing() {
  return (
    <section className="bg-surface-container-low py-24 px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-slate-900 mb-4">Scalable intelligence</h2>
          <p className="text-slate-500">Select the plan that fits your current hiring volume.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {/* Startup */}
          <div className="bg-surface-container-lowest p-10 rounded-3xl border border-slate-100 flex flex-col">
            <h3 className="text-lg font-bold text-slate-900 mb-2">Startup</h3>
            <div className="flex items-baseline gap-1 mb-6">
              <span className="text-4xl font-extrabold text-slate-900">$49</span>
              <span className="text-slate-500 text-sm">/month</span>
            </div>
            <ul className="space-y-4 mb-10 flex-grow">
              <li className="flex items-center gap-3 text-sm text-slate-600">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span>
                Up to 50 interviews/mo
              </li>
              <li className="flex items-center gap-3 text-sm text-slate-600">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span>
                Basic sentiment analysis
              </li>
              <li className="flex items-center gap-3 text-sm text-slate-600">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span>
                Zoom & Meet integration
              </li>
            </ul>
            <button className="w-full py-4 rounded-xl font-bold border-2 border-slate-100 text-slate-900 hover:bg-slate-50 transition-all">Get Started</button>
          </div>
          {/* Professional */}
          <div className="bg-slate-900 p-10 rounded-3xl relative flex flex-col shadow-2xl xl:scale-105 z-10">
            <div className="absolute top-0 right-10 -translate-y-1/2 bg-primary text-white text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-tighter">Most Popular</div>
            <h3 className="text-lg font-bold text-white mb-2">Professional</h3>
            <div className="flex items-baseline gap-1 mb-6">
              <span className="text-4xl font-extrabold text-white">$199</span>
              <span className="text-slate-400 text-sm">/month</span>
            </div>
            <ul className="space-y-4 mb-10 flex-grow">
              <li className="flex items-center gap-3 text-sm text-slate-300">
                <span className="material-symbols-outlined text-primary-fixed text-lg">check_circle</span>
                Unlimited interviews
              </li>
              <li className="flex items-center gap-3 text-sm text-slate-300">
                <span className="material-symbols-outlined text-primary-fixed text-lg">check_circle</span>
                Full Skills Matrix AI
              </li>
              <li className="flex items-center gap-3 text-sm text-slate-300">
                <span className="material-symbols-outlined text-primary-fixed text-lg">check_circle</span>
                Advanced ATS sync
              </li>
              <li className="flex items-center gap-3 text-sm text-slate-300">
                <span className="material-symbols-outlined text-primary-fixed text-lg">check_circle</span>
                Dedicated support
              </li>
            </ul>
            <button className="w-full py-4 rounded-xl font-bold bg-primary text-white hover:bg-primary/90 transition-all">Start 14-Day Free Trial</button>
          </div>
          {/* Enterprise */}
          <div className="bg-surface-container-lowest p-10 rounded-3xl border border-slate-100 flex flex-col">
            <h3 className="text-lg font-bold text-slate-900 mb-2">Enterprise</h3>
            <div className="flex items-baseline gap-1 mb-6">
              <span className="text-4xl font-extrabold text-slate-900">Custom</span>
            </div>
            <ul className="space-y-4 mb-10 flex-grow">
              <li className="flex items-center gap-3 text-sm text-slate-600">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span>
                Custom model training
              </li>
              <li className="flex items-center gap-3 text-sm text-slate-600">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span>
                White-label reporting
              </li>
              <li className="flex items-center gap-3 text-sm text-slate-600">
                <span className="material-symbols-outlined text-primary text-lg">check_circle</span>
                On-prem deployment options
              </li>
            </ul>
            <button className="w-full py-4 rounded-xl font-bold border-2 border-slate-100 text-slate-900 hover:bg-slate-50 transition-all">Contact Sales</button>
          </div>
        </div>
      </div>
    </section>
  );
}
