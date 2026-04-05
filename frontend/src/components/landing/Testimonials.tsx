import React from 'react';

export default function Testimonials() {
  const testimonials = [
    {
      quote: "Intervux completely transformed our top-of-funnel. We went from taking 3 weeks to screen 100 candidates to completing it over a weekend. The quality of our on-site interviews skyrocketed.",
      author: "Elena Rodriguez",
      role: "VP of Talent, GlobalTech",
      image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=150&h=150"
    },
    {
      quote: "The evaluation reports are incredibly objective. We found that the AI surfaced hidden gems—candidates who might have been overlooked by junior recruiters simply parsing resumes for keywords.",
      author: "Marcus Chen",
      role: "Engineering Manager, FinServe",
      image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=150&h=150"
    },
    {
      quote: "I was skeptical about AI interviewing, but our candidates love the flexibility of interviewing at 9 PM on a Sunday. The natural voice flow is uncanny.",
      author: "Sarah Jenkins",
      role: "Head of People, StartupX",
      image: "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?auto=format&fit=crop&q=80&w=150&h=150"
    }
  ];

  return (
    <section className="py-24 bg-surface">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="font-headline text-3xl font-bold text-on-surface sm:text-4xl">Loved by recruiting teams</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((test, i) => (
            <div key={i} className="p-8 rounded-[2rem] bg-surface-container-low border border-outline-variant/30 flex flex-col justify-between hover:shadow-lg transition-transform hover:-translate-y-1">
              <div>
                <div className="flex gap-1 mb-6 text-[#f59e0b]">
                   {[1,2,3,4,5].map(s => (
                     <svg key={s} className="w-5 h-5 fill-current" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                   ))}
                </div>
                <p className="text-on-surface-variant text-lg italic mb-8">"{test.quote}"</p>
              </div>
              <div className="flex items-center gap-4">
                <img src={test.image} alt={test.author} className="w-12 h-12 rounded-full border-2 border-primary/20" />
                <div>
                  <div className="font-bold text-on-surface">{test.author}</div>
                  <div className="text-sm text-on-surface-variant font-medium">{test.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
