import React, { useEffect } from 'react';
import { TopNavbar } from '../components/layout/TopNavbar';
import { HeroSection } from './landing/HeroSection';
import { TrustSection } from './landing/TrustSection';
import { ProblemSolutionSection } from './landing/ProblemSolutionSection';
import { WorkflowSection } from './landing/WorkflowSection';
import { ProductShowcase } from './landing/ProductShowcase';
import { PricingSection } from './landing/PricingSection';
import { CTABanner } from './landing/CTABanner';
import { Footer } from '../components/layout/Footer';

export const LandingPage: React.FC = () => {
  // Ensure the page takes the global surface background from the design system
  useEffect(() => {
    document.body.className = 'bg-surface font-body text-on-surface antialiased';
    return () => {
      document.body.className = '';
    };
  }, []);

  return (
    <div className="w-full">
      <TopNavbar />
      <HeroSection />
      <TrustSection />
      <ProblemSolutionSection />
      <WorkflowSection />
      <ProductShowcase />
      <PricingSection />
      <CTABanner />
      <Footer />
    </div>
  );
};
