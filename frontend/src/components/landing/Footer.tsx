

export default function Footer() {
  return (
    <footer className="bg-slate-900 pt-24 pb-12 px-8 text-slate-400">
      <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-x-8 gap-y-16 mb-24">
        <div className="col-span-2 lg:col-span-2">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-primary-fixed flex items-center justify-center shadow-lg">
              <span className="material-symbols-outlined text-white text-lg">psychology</span>
            </div>
            <span className="font-extrabold text-white text-xl tracking-tight">Intervux AI</span>
          </div>
          <p className="text-sm text-slate-500 max-w-xs mb-8">The cognitive architecture for modern recruiting. Elevate your hiring process with deterministic AI insights.</p>
          <div className="flex gap-4">
            <a href="#" className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center hover:bg-slate-700 transition-colors">
              <span className="material-symbols-outlined text-sm">alternate_email</span>
            </a>
            <a href="#" className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center hover:bg-slate-700 transition-colors">
              <span className="material-symbols-outlined text-sm">forum</span>
            </a>
            <a href="#" className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center hover:bg-slate-700 transition-colors">
              <span className="material-symbols-outlined text-sm">language</span>
            </a>
          </div>
        </div>
        <div className="col-span-2 md:col-span-1 lg:col-span-1">
          <h4 className="text-white font-bold mb-6">Product</h4>
          <ul className="space-y-4 text-sm">
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Sentiment Analysis</a></li>
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Skills Matrix</a></li>
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Automation</a></li>
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Integrations</a></li>
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Pricing</a></li>
          </ul>
        </div>
        <div className="col-span-2 md:col-span-1 lg:col-span-1">
          <h4 className="text-white font-bold mb-6">Resources</h4>
          <ul className="space-y-4 text-sm">
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Documentation</a></li>
            <li><a href="#" className="hover:text-primary-fixed transition-colors">API Reference</a></li>
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Case Studies</a></li>
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Blog</a></li>
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Help Center</a></li>
          </ul>
        </div>
        <div className="col-span-2 md:col-span-1 lg:col-span-1">
          <h4 className="text-white font-bold mb-6">Company</h4>
          <ul className="space-y-4 text-sm">
            <li><a href="#" className="hover:text-primary-fixed transition-colors">About Us</a></li>
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Careers</a></li>
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Security</a></li>
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Terms of Service</a></li>
            <li><a href="#" className="hover:text-primary-fixed transition-colors">Privacy Policy</a></li>
          </ul>
        </div>
        <div className="col-span-2 md:col-span-1 lg:col-span-1">
          <h4 className="text-white font-bold mb-6">Subscribe</h4>
          <p className="text-xs text-slate-500 mb-4">Get the latest updates on AI recruiting.</p>
          <div className="flex gap-2">
            <input type="email" placeholder="Email address" className="bg-slate-800 text-white text-sm rounded-lg px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-primary" />
            <button className="bg-primary hover:bg-primary/90 text-white rounded-lg px-3 flex items-center justify-center transition-colors">
              <span className="material-symbols-outlined text-sm">send</span>
            </button>
          </div>
        </div>
      </div>
      <div className="max-w-7xl mx-auto pt-8 border-t border-slate-800 flex flex-col md:flex-row justify-between items-center gap-4">
        <p className="text-sm">© 2026 Intervux AI. All rights reserved.</p>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span className="text-sm">All systems operational</span>
        </div>
      </div>
    </footer>
  );
}
