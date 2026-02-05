// [Task]: T020, [From]: specs/003-landing-page/tasks.md#T020
// SEO metadata and structured data for landing page

import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Evolution of Todo - Simple Task Management App',
  description:
    'Manage your tasks effortlessly. Free task management for students, freelancers, and teams. No credit card required.',
  keywords:
    'task management, todo app, productivity, task tracker, free app, multilingual',
  openGraph: {
    title: 'Evolution of Todo - Simple Task Management App',
    description:
      'Manage your tasks effortlessly. Free task management for students, freelancers, and teams.',
    type: 'website',
    locale: 'en_US',
    siteName: 'Evolution of Todo',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Evolution of Todo - Simple Task Management App',
    description:
      'Manage your tasks effortlessly. Free task management for students, freelancers, and teams.',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: 'https://example.com',
  },
};

// Schema.org structured data for SoftwareApplication
export const schema = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'Evolution of Todo',
  description:
    'Simple task management app for everyone. Free to start, no credit card required.',
  url: 'https://example.com',
  applicationCategory: 'ProductivityApplication',
  offers: {
    '@type': 'Offer',
    price: '0',
    priceCurrency: 'USD',
  },
  operatingSystem: 'Web',
  aggregateRating: {
    '@type': 'AggregateRating',
    ratingValue: '4.5',
    ratingCount: '100',
  },
  inLanguage: ['en', 'ur'],
};
