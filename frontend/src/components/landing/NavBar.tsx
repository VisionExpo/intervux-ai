

export default function NavBar() {
  return (
    <nav className="fixed top-0 w-full z-50 bg-surface/70 backdrop-blur-xl flex justify-between items-center px-8 h-16">
      <div className="flex items-center gap-8">
        <span className="text-xl font-bold tracking-tight text-slate-900">Intervux AI</span>
        <div className="hidden md:flex items-center gap-6">
          <a className="text-blue-600 font-semibold border-b-2 border-blue-600" href="#">Product</a>
          <a className="text-slate-600 hover:text-slate-900 transition-colors" href="#">Features</a>
          <a className="text-slate-600 hover:text-slate-900 transition-colors" href="#">Pricing</a>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="hidden lg:flex items-center mr-4">
          <span className="material-symbols-outlined text-slate-500 mr-2">search</span>
          <input className="bg-surface-container-low border-none rounded-xl text-sm px-4 py-1.5 focus:ring-2 focus:ring-primary/20 w-48" placeholder="Search insights..." type="text" />
        </div>
        <button onClick={() => window.location.hash = '#/login'} className="text-slate-600 hover:bg-slate-100/50 px-4 py-2 rounded-xl transition-colors text-sm font-medium">Login</button>
        <button onClick={() => window.location.hash = '#/signup'} className="bg-primary text-white px-5 py-2 rounded-xl text-sm font-semibold active:scale-95 duration-150 shadow-sm">Get Started</button>
        <span className="material-symbols-outlined text-slate-500 cursor-pointer p-2 hover:bg-slate-100/50 rounded-full transition-colors" data-icon="notifications">notifications</span>
      </div>
    </nav>
  );
}
