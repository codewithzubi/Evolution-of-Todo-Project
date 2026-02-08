// [Task]: T008-T051, [From]: specs/003-landing-page/spec.md
// Locale root page - render landing page

export { metadata } from './(landing)/metadata';

// Disable static generation for dynamic i18n routes
export const dynamic = 'force-dynamic';

export default async function LocalePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  // Await params (required for Next.js dynamic routes)
  await params;

  // Dynamically import the landing page component
  const { default: LandingPage } = await import('./(landing)/page');

  return <LandingPage />;
}
