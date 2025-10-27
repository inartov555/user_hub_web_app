import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

// Static JSON import (keeps tree-shaking simple)
// For many languages, swap to lazy loading with i18next-http-backend.
import en_US from "../locales/en_US.json";
import et_EE from "../locales/et_EE.json";

i18n
  .use(LanguageDetector) // detects from localStorage, navigator, querystring, etc.
  .use(initReactI18next)
  .init({
    resources: {
      "en-US": { translation: en_US },
      "et-EE": { translation: et_EE },
    },
    fallbackLng: "en-US",
    supportedLngs: ["en-US", "et-EE"],
    interpolation: { escapeValue: false },
    detection: {
      order: ["querystring", "localStorage", "navigator", "htmlTag"],
      caches: ["localStorage"],
    },
  });

export default i18n;
