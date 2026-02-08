// [Task]: T021, T043, [From]: specs/003-landing-page/tasks.md#T021, T043
// Landing page root component that assembles all sections including FinalCTA

'use client';

import React from 'react';
import { useLanguage } from '@/hooks/useLanguage';
import LandingHeader from '@/components/landing/LandingHeader';
import Footer from '@/components/landing/Footer';
import HeroSection from '@/components/landing/HeroSection';
import ProblemSection from '@/components/landing/ProblemSection';
import SolutionSection from '@/components/landing/SolutionSection';
import FeaturesSection from '@/components/landing/FeaturesSection';
import FinalCTASection from '@/components/landing/FinalCTASection';

const LandingPage: React.FC = () => {
  const { isRTL } = useLanguage();

  return (
    <div dir={isRTL ? 'rtl' : 'ltr'} className="min-h-screen bg-white dark:bg-gray-950">
      <LandingHeader />
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <HeroSection />
        <ProblemSection />
        <SolutionSection />
        <FeaturesSection />
        {/* Additional sections to be added: HowItWorks, Preview, TargetAudience, Pricing */}
      </main>
      <FinalCTASection />
      <Footer />
    </div>
  );
};

export default LandingPage;
