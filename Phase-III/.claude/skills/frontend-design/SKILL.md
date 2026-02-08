---
name: "frontend-design"
description: "Build modern, responsive pages, components, and layouts with clean styling. Use when the user asks to create UI, design web interfaces, build components, or style applications."
version: "1.0.0"
---

# Frontend Design Skill

## When to Use This Skill
- When the user asks to "create a page", "build a component", or "design a UI"
- When the user mentions layout, styling, responsive design, or web interface
- When the user needs help with HTML, CSS, React components, or frontend frameworks
- When creating dashboards, landing pages, forms, or any web application interface

## Procedure

1. **Understand requirements**: Clarify the purpose, target users, and key functionality
2. **Choose the right stack**: Select appropriate framework (React, HTML, Next.js) based on context
3. **Design mobile-first**: Start with mobile layout, then scale up to desktop
4. **Structure semantically**: Use proper HTML elements and component hierarchy
5. **Style with utility classes**: Apply Tailwind CSS core utilities for consistent design
6. **Add interactivity**: Implement necessary state management and event handlers
7. **Optimize for performance**: Minimize JavaScript, lazy load where appropriate

## Output Format

**Component Structure**: Clear file organization and component hierarchy  
**Responsive Design**: Mobile-first breakpoints (sm, md, lg, xl)  
**Styling Approach**: Tailwind utility classes with consistent spacing/colors  
**Interactivity**: Event handlers, state management, form handling  
**Accessibility**: Semantic HTML, ARIA labels, keyboard navigation  

## Quality Criteria

### Design Quality
- **Distinctive, not generic**: Avoid bland, default-looking UIs that scream "AI-generated"
- **Visual hierarchy**: Clear focal points, proper spacing, intentional color usage
- **Consistency**: Unified spacing scale (4px, 8px, 16px, 24px, 32px), limited color palette
- **Polish**: Rounded corners, subtle shadows, smooth transitions where appropriate

### Code Quality
- **Component composition**: Break complex UIs into reusable, focused components
- **Semantic HTML**: Use `<header>`, `<nav>`, `<main>`, `<section>`, `<article>` appropriately
- **Tailwind best practices**: Use core utilities only (no custom classes that require compilation)
- **Performance-conscious**: Server Components by default (Next.js), minimal client-side JS

### Responsive Design
- **Mobile-first**: Base styles for mobile, add complexity at larger breakpoints
- **Breakpoint strategy**: `sm:` (640px), `md:` (768px), `lg:` (1024px), `xl:` (1280px)
- **Touch-friendly**: Minimum 44x44px touch targets, adequate spacing
- **Flexible layouts**: Use flexbox/grid that adapt naturally to viewport changes

### Styling Approach
- **Spacing scale**: `p-2`, `p-4`, `p-6`, `p-8` (avoid random values like `p-7`)
- **Color palette**: 2-3 primary colors maximum, use shades thoughtfully
- **Typography**: Clear hierarchy with `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`
- **Dark mode ready**: Consider `dark:` variants when appropriate

## Anti-Patterns to Avoid

❌ **Generic layouts**: Cookie-cutter centered-card designs  
❌ **Inconsistent spacing**: Random margin/padding values throughout  
❌ **Color chaos**: Using 8 different colors with no system  
❌ **Over-engineering**: Adding complexity when simplicity works  
❌ **Ignoring mobile**: Desktop-first designs that break on phones  
❌ **Accessibility neglect**: Missing alt text, labels, or keyboard support  
❌ **Non-semantic HTML**: `<div>` soup instead of proper elements  

## Framework-Specific Guidelines

### React / Next.js
```jsx
// Server Component (Next.js default)
export default async function Page() {
  const data = await fetchData();
  return <div className="p-4 md:p-8">...</div>;
}

// Client Component (when needed)
'use client';
export default function Interactive() {
  const [state, setState] = useState();
  return <button onClick={...}>...</button>;
}
```

### HTML + Tailwind
```html
<!-- Mobile-first responsive structure -->
<div class="container mx-auto px-4">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Cards -->
  </div>
</div>
```

## Example

**Input**: "Create a pricing page with three tiers"

**Output**:

```jsx
export default function PricingPage() {
  const tiers = [
    {
      name: 'Starter',
      price: 29,
      features: ['10 projects', '5GB storage', 'Email support'],
      cta: 'Start Free Trial'
    },
    {
      name: 'Professional',
      price: 79,
      features: ['Unlimited projects', '100GB storage', 'Priority support', 'Advanced analytics'],
      cta: 'Start Free Trial',
      popular: true
    },
    {
      name: 'Enterprise',
      price: 199,
      features: ['Unlimited everything', 'Dedicated support', 'Custom integrations', 'SLA guarantee'],
      cta: 'Contact Sales'
    }
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-16 md:py-24">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-white mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
            Choose the plan that fits your needs. Upgrade or downgrade anytime.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {tiers.map((tier) => (
            <div
              key={tier.name}
              className={`relative bg-white dark:bg-slate-800 rounded-2xl shadow-lg p-8 ${
                tier.popular ? 'ring-2 ring-blue-500 scale-105' : ''
              }`}
            >
              {tier.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                  Most Popular
                </div>
              )}
              
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                {tier.name}
              </h3>
              
              <div className="mb-6">
                <span className="text-5xl font-bold text-slate-900 dark:text-white">
                  ${tier.price}
                </span>
                <span className="text-slate-600 dark:text-slate-400">/month</span>
              </div>

              <ul className="space-y-4 mb-8">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <svg className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-slate-600 dark:text-slate-300">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                className={`w-full py-3 px-6 rounded-lg font-medium transition-colors ${
                  tier.popular
                    ? 'bg-blue-500 hover:bg-blue-600 text-white'
                    : 'bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-900 dark:text-white'
                }`}
              >
                {tier.cta}
              </button>
            </div>
          ))}
        </div>

        {/* FAQ Link */}
        <div className="text-center mt-16">
          <p className="text-slate-600 dark:text-slate-400">
            Questions?{' '}
            <a href="#faq" className="text-blue-500 hover:text-blue-600 font-medium">
              Check our FAQ
            </a>
          </p>
        </div>
      </div>
    </main>
  );
}
```

**Why this works**:
- ✅ Mobile-first responsive grid (1 column → 3 columns)
- ✅ Visual hierarchy with popular tier scaled and highlighted
- ✅ Consistent spacing scale (p-4, p-8, gap-8, mb-16)
- ✅ Limited color palette (slate, blue, green accents)
- ✅ Semantic HTML structure
- ✅ Dark mode support with dark: variants
- ✅ Touch-friendly button sizes
- ✅ Smooth hover transitions

## Tips for Excellence

1. **Start simple, add complexity**: Begin with basic layout, refine incrementally
2. **Use real content**: Avoid "Lorem ipsum" - realistic content reveals design issues
3. **Test at breakpoints**: Check 375px (mobile), 768px (tablet), 1440px (desktop)
4. **Limit your palette**: Pick 1-2 brand colors, use their shades
5. **Consistent spacing**: Stick to 8px increments (Tailwind's spacing scale)
6. **White space is your friend**: Don't cram everything together
7. **Accessibility first**: Every interactive element needs proper labels
8. **Performance matters**: Lazy load images, minimize bundle size

## Common Requests

| User Says | Build |
|-----------|-------|
| "Create a dashboard" | Grid layout with cards, charts, stats |
| "Build a landing page" | Hero section, features, CTA, testimonials |
| "Make a form" | Input fields, validation, submit handling |
| "Design a navbar" | Responsive menu, mobile hamburger, dropdowns |
| "Build a card component" | Reusable card with image, title, description |

## Success Checklist

Before delivering, verify:
- [ ] Works on mobile (375px width)
- [ ] Responsive at tablet (768px) and desktop (1024px+)
- [ ] Uses semantic HTML elements
- [ ] Has consistent spacing throughout
- [ ] Color palette is limited and cohesive
- [ ] Interactive elements have hover/focus states
- [ ] Accessible (labels, alt text, keyboard navigation)
- [ ] Code is clean and well-organized
- [ ] Looks distinctive, not generic

---

**Remember**: Great frontend work balances aesthetics, usability, accessibility, and performance. When in doubt, favor simplicity and clarity over complexity.