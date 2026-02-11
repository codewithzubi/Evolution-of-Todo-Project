# Quick Start Guide - Landing Page

## Prerequisites
- Node.js 18+ installed
- npm or yarn installed

## Installation & Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

This will install:
- Next.js 16.1.6
- React 19
- TypeScript 5.7.2
- Tailwind CSS 3.4.17
- TanStack Query v5
- Lucide React icons
- shadcn/ui dependencies

### 3. Create Environment File
```bash
cp .env.example .env.local
```

Edit `.env.local` if needed (defaults should work for local development).

### 4. Run Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## What You Should See

### Landing Page (/)
1. **Hero Section**
   - Headline: "Never forget a task again."
   - Subheadline: "Simple. Powerful. Yours."
   - Blue "Get Started" button
   - Phone mockup on the right showing dashboard with tasks

2. **Features Section**
   - 4 feature cards in a grid
   - Icons: CheckCircle, Filter, Lock, Globe
   - Hover effects on cards

3. **CTA Section**
   - "Ready to get organized?" heading
   - "Get Started Free" button

### Login Page (/login)
- Login form with email and password inputs
- "Sign In" button
- Link back to home

### Test Navigation
- Click "Get Started" in hero → should go to /login
- Click "Get Started Free" in CTA → should go to /login
- Click "Back to home" on login page → should return to /

## Testing Responsive Design

### Mobile View (375px)
```bash
# Open DevTools (F12)
# Toggle device toolbar (Ctrl+Shift+M)
# Select iPhone SE or similar
```
- Hero section should stack vertically
- Features should show 1 column
- Phone mockup should be centered below headline

### Tablet View (768px)
- Features should show 2 columns
- Hero may stack or show side-by-side

### Desktop View (1024px+)
- Hero should show side-by-side layout
- Features should show 4 columns
- Content should be centered with max-width

## Build for Production

### Test Production Build
```bash
npm run build
npm start
```

Open [http://localhost:3000](http://localhost:3000) to verify production build.

### Check for Errors
```bash
# TypeScript check
npx tsc --noEmit

# Lint check
npm run lint
```

## Common Issues

### Port Already in Use
If port 3000 is already in use:
```bash
# Kill the process using port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use a different port:
npm run dev -- -p 3001
```

### Module Not Found Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Styling Not Applied
```bash
# Restart dev server
# Clear browser cache (Ctrl+Shift+R)
```

## Next Steps

1. **Manual Testing**: Use TESTING-CHECKLIST.md to verify all features
2. **Accessibility Testing**: Test with screen reader and keyboard navigation
3. **Performance Testing**: Run Lighthouse audit in Chrome DevTools
4. **Deploy**: Deploy to Vercel, Netlify, or your preferred platform

## Deployment

### Deploy to Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Deploy to Netlify
```bash
# Build
npm run build

# Deploy the .next folder
# Configure build command: npm run build
# Configure publish directory: .next
```

## Support

- See IMPLEMENTATION.md for detailed implementation notes
- See STATUS-REPORT.md for requirements verification
- See TESTING-CHECKLIST.md for comprehensive testing guide
- See README.md for project documentation

## Success Indicators

✅ Page loads without errors
✅ All sections are visible
✅ CTA buttons navigate to /login
✅ Phone mockup shows dashboard preview
✅ Responsive design works on all screen sizes
✅ Dark theme is applied
✅ Animations play smoothly

Enjoy your new landing page! 🚀
