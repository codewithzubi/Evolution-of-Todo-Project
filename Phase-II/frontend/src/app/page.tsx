// [Task]: T-008, [From]: specs/002-task-ui-frontend/spec.md#Requirements
// Home page - redirects to tasks dashboard or login

import { redirect } from 'next/navigation';

/**
 * Home Page
 * Redirects to /en (landing page with i18n routing)
 * Users see the landing page first, then can navigate to tasks or auth
 */
export default function HomePage(): React.ReactNode {
    // Redirect to English landing page
  redirect('/en');
}
