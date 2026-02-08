// [Task]: T008, [From]: specs/003-landing-page/tasks.md#T008
// Type definitions for landing page components

import type { ReactNode } from 'react';

// Feature item type for FeaturesSection
export interface FeatureItem {
  title: string;
  description: string;
  icon?: ReactNode;
}

// Problem item type for ProblemSection
export interface ProblemItem {
  title: string;
  description: string;
}

// Solution highlight type
export interface SolutionHighlight {
  title: string;
  description: string;
}

// How it works step type
export interface HowItWorksStep {
  title: string;
  description: string;
  icon?: ReactNode;
}

// Preview screenshot type
export interface PreviewScreenshot {
  title: string;
  description: string;
  imagePath?: string;
}

// Target audience persona type
export interface Persona {
  title: string;
  description: string;
  icon?: ReactNode;
}

// Landing page section props base type
export interface LandingSectionProps {
  className?: string;
  id?: string;
}

// CTA Button props
export interface CTAButtonProps {
  href?: string;
  onClick?: () => void;
  children?: ReactNode;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  disabled?: boolean;
  className?: string;
}

// Button props
export interface ButtonProps extends CTAButtonProps {
  type?: 'button' | 'submit' | 'reset';
}

// Card props
export interface CardProps {
  children?: ReactNode;
  className?: string;
  onClick?: () => void;
}

// Section heading props
export interface SectionHeadingProps {
  title: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg';
  centered?: boolean;
  className?: string;
}

// Language selector props
export interface LanguageSelectorProps {
  className?: string;
  onLanguageChange?: (lang: string) => void;
}

// Landing page root component props
export interface LandingPageProps {
  className?: string;
}
