import React, { useEffect } from 'react';
import NavBar from '../components/landing/NavBar';
import Hero from '../components/landing/Hero';
import TrustedBrands from '../components/landing/TrustedBrands';
import BentoGrid from '../components/landing/BentoGrid';
import CandidateWorkflow from '../components/landing/CandidateWorkflow';
import Testimonials from '../components/landing/Testimonials';
import Pricing from '../components/landing/Pricing';
import CTA from '../components/landing/CTA';
import Footer from '../components/landing/Footer';

export default function HomePage() {
  useEffect(() => {
    // Scroll to top on mount
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen bg-surface flex flex-col font-body selection:bg-primary/20 selection:text-primary">
      <NavBar />
      
      <main className="flex-1">
        <Hero />
        <TrustedBrands />
        <BentoGrid />
        <CandidateWorkflow />
        <Testimonials />
        <Pricing />
        <CTA />
      </main>

      <Footer />
    </div>
  );
}
