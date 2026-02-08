// [Task]: T008-T051, [From]: specs/003-landing-page/spec.md
// Locale layout wrapper for i18n routing with custom LanguageProvider

import { ReactNode } from 'react';
import { LanguageProvider } from '@/providers/LanguageContext';
import { SUPPORTED_LANGUAGES, type LanguageCode } from '@/i18n/config';

interface LocaleLayoutProps {
  children: ReactNode;
  params: Promise<{
    locale: string;
  }>;
}

export async function generateStaticParams() {
  return Object.values(SUPPORTED_LANGUAGES).map((locale) => ({
    locale,
  }));
}

async function loadMessages(locale: string) {
  try {
    const messages = (await import(`@/i18n/locales/${locale}.json`)).default;
    return messages;
  } catch (error) {
    console.error(`Failed to load messages for locale: ${locale}`, error);
    // Fallback to English if locale not found
    return (await import(`@/i18n/locales/en.json`)).default;
  }
}

export default async function LocaleLayout({
  children,
  params,
}: LocaleLayoutProps) {
  const { locale } = await params;
  const messages = await loadMessages(locale);

  return (
    <LanguageProvider locale={locale as LanguageCode} messages={messages}>
      {children}
    </LanguageProvider>
  );
}
