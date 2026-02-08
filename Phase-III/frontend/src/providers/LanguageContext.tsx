// Custom Language Context to replace next-intl
// Provides translation and locale information without config file discovery

'use client';

import { createContext, ReactNode, useContext } from 'react';
import { SUPPORTED_LANGUAGES, isRTLLanguage, type LanguageCode } from '@/i18n/config';

interface TranslationFunction {
  (key: string, defaultValue?: string): string;
  raw: (key: string) => any;
}

interface LanguageContextType {
  locale: LanguageCode;
  t: TranslationFunction;
  isRTL: boolean;
  isSupported: boolean;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

interface LanguageProviderProps {
  children: ReactNode;
  locale: LanguageCode;
  messages: Record<string, any>;
}

export function LanguageProvider({ children, locale, messages }: LanguageProviderProps) {
  const isRTL = isRTLLanguage(locale);

  // Helper function to get nested values from messages
  const getNestedValue = (key: string): any => {
    const keys = key.split('.');
    let value: any = messages;

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return undefined;
      }
    }

    return value;
  };

  // Translation function that supports both string and raw data access
  const t: TranslationFunction = ((key: string, defaultValue: string = key): string => {
    const value = getNestedValue(key);
    return typeof value === 'string' ? value : defaultValue;
  }) as TranslationFunction;

  // Add the .raw method to access non-string values (arrays, objects, etc.)
  t.raw = (key: string) => {
    return getNestedValue(key);
  };

  const value: LanguageContextType = {
    locale,
    t,
    isRTL,
    isSupported: Object.values(SUPPORTED_LANGUAGES).includes(locale),
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
}
