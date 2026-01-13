import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

// Static JSON import (keeps tree-shaking simple)
// For many languages, swap to lazy loading with i18next-http-backend.
import en_US from "../locale/en_US.json";
import uk_UA from "../locale/uk_UA.json";
import et_EE from "../locale/et_EE.json";
import fi_FI from "../locale/fi_FI.json";
import cs_CZ from "../locale/cs_CZ.json";
import pl_PL from "../locale/pl_PL.json";
import es_ES from "../locale/es_ES.json";

i18n
  .use(LanguageDetector) 
  .use(initReactI18next)
  .init({
    resources: {
      "en-US": { translation: en_US },
      "uk-UA": { translation: uk_UA },
      "et-EE": { translation: et_EE },
      "fi-FI": { translation: fi_FI },
      "cs-CZ": { translation: cs_CZ },
      "pl-PL": { translation: pl_PL },
      "es-ES": { translation: es_ES },
    },
    fallbackLng: "en-US",
    supportedLngs: ["en-US", "et-EE", "fi-FI", "cs-CZ", "pl-PL", "uk-UA", "es-ES"],
    interpolation: { escapeValue: false },
    detection: {
      order: ["querystring", "localStorage", "navigator", "htmlTag"],
      caches: ["localStorage"],
    },
  });

export default i18n;
