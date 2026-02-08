// [Task]: T002, [From]: specs/003-landing-page/tasks.md#T002
// next-intl configuration file for i18n setup

import { getRequestConfig } from 'next-intl/server';

export default getRequestConfig(async ({ locale = 'en' }) => ({
  locale,
  messages: (
    await import(`@/i18n/locales/${locale}.json`)
  ).default,
}));
