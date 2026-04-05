

export default function Testimonials() {
  return (
    <section className="bg-white py-24 px-8 overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-slate-900 mb-4 italic leading-tight">"The most significant upgrade to our recruiting stack in a decade."</h2>
          <div className="flex justify-center items-center gap-4 mt-8">
            <img alt="Sarah Chen" className="w-16 h-16 rounded-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCEw5eb2Mme54EPPeMdnPsYpMYdAXHy_j4fsmV8ZznEfSTxtusRhokdLBq740WnFWw_j2KbjxdASjy6f6j5jQtbINhtyREI1RaVJr0Twuz4ypdh_PLnBJuPpI1Q138VfXLdblVwESfy6oddkbPqHzFum3AmrKRr8fQdbFdkS7aVweNsnloDjNpmTpfvELvCdK3zEJ8sVcRFGlpG0YcVxc56berOGEJgkXylgy87JZCqFwE8VZ5AA9RFWlrQh9yLdctn7YkBWS04DEM" />
            <div className="text-left">
              <p className="font-bold text-slate-900">Sarah Chen</p>
              <p className="text-sm text-slate-500">Head of Talent, Nexus Global</p>
            </div>
          </div>
        </div>
        <div className="grid md:grid-cols-3 gap-12 border-t border-slate-100 pt-16">
          <div>
            <p className="text-4xl font-extrabold text-primary mb-2">40%</p>
            <p className="text-sm font-bold text-slate-900 uppercase tracking-widest mb-2">Efficiency Gain</p>
            <p className="text-slate-500 text-sm">Recruiters spend less time on manual scorecards and more on human connection.</p>
          </div>
          <div>
            <p className="text-4xl font-extrabold text-primary mb-2">2.4x</p>
            <p className="text-sm font-bold text-slate-900 uppercase tracking-widest mb-2">Retention Rate</p>
            <p className="text-slate-500 text-sm">Candidates identified by AI insights are showing significantly longer tenure.</p>
          </div>
          <div>
            <p className="text-4xl font-extrabold text-primary mb-2">15+</p>
            <p className="text-sm font-bold text-slate-900 uppercase tracking-widest mb-2">ATS Integrations</p>
            <p className="text-slate-500 text-sm">Works seamlessly with Greenhouse, Lever, Workday, and every major platform.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
