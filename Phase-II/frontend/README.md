# Phase II Todo - Frontend

Modern, dark-themed landing page and task management application built with Next.js 16.1.6.

## Tech Stack

- **Framework**: Next.js 16.1.6 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **Icons**: Lucide React
- **State Management**: TanStack Query v5

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the landing page.

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Landing page
│   ├── login/page.tsx        # Login page
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/
│   ├── landing/              # Landing page components
│   │   ├── hero-section.tsx
│   │   ├── phone-mockup.tsx
│   │   ├── features-section.tsx
│   │   ├── feature-card.tsx
│   │   └── cta-section.tsx
│   └── ui/                   # shadcn/ui components
│       ├── button.tsx
│       └── card.tsx
└── lib/
    └── utils.ts              # Utility functions
```

## Features

- **Hero Section**: Compelling headline with phone mockup showcasing dashboard
- **Features Section**: 4 key capabilities with icons and descriptions
- **CTA Section**: Call-to-action redirecting to login
- **Dark Mode**: Default dark theme with custom color palette
- **Responsive**: Mobile-first design, fully responsive
- **Accessible**: WCAG compliant with proper ARIA labels
- **Performant**: Optimized for Core Web Vitals

## Build

```bash
# Production build
npm run build

# Start production server
npm start
```

## License

MIT
