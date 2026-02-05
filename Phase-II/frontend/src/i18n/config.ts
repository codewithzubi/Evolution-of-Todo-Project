// [Task]: T002, [From]: specs/003-landing-page/tasks.md#T002
// i18n configuration for next-intl with language constants

export const SUPPORTED_LANGUAGES = {
  EN: 'en',
  UR: 'ur',
  UR_ROMAN: 'ur-roman',
} as const;

export const DEFAULT_LANGUAGE = SUPPORTED_LANGUAGES.EN;

export const LANGUAGES = [
  { code: SUPPORTED_LANGUAGES.EN, name: 'English', nativeName: 'English' },
  { code: SUPPORTED_LANGUAGES.UR, name: 'Urdu', nativeName: 'اردو' },
  { code: SUPPORTED_LANGUAGES.UR_ROMAN, name: 'Roman Urdu', nativeName: 'Urdu' },
] as const;

// Type-safe language code
export type LanguageCode = typeof SUPPORTED_LANGUAGES[keyof typeof SUPPORTED_LANGUAGES];

// Language metadata for RTL support
export const isRTLLanguage = (lang: LanguageCode): boolean => {
  return lang === SUPPORTED_LANGUAGES.UR;
};
