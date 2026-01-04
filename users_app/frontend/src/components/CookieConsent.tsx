import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Cookie } from "lucide-react";
import Button from "./button";
import UnifiedTitle from "../components/UnifiedTitle";

const STORAGE_KEY = "cookie_consent_accepted_v1";
const COOKIE_NAME = "cookie_consent";

function getStoredConsent(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === "1";
  } catch {
    // localStorage may be unavailable in some privacy modes
    return false;
  }
}

function setConsent() {
  try {
    localStorage.setItem(STORAGE_KEY, "1");
  } catch {
    // ignore
  }

  try {
    const oneYearSeconds = 60 * 60 * 24 * 365;
    document.cookie = `${COOKIE_NAME}=accepted; Max-Age=${oneYearSeconds}; Path=/; SameSite=Lax`;
  } catch {
    // ignore
  }
}

export default function CookieConsent() {
  const { t, i18n } = useTranslation();
  const [accepted, setAcceptedState] = useState<boolean>(() => getStoredConsent());

  // Keep multiple tabs in sync.
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY) {
        setAcceptedState(e.newValue === "1");
      }
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  if (accepted) return null;

  const onAccept = () => {
    setConsent();
    setAcceptedState(true);
  };

  return (
    <div data-tag="
           cookieConsentContainer" className="fixed inset-0 z-50 flex items-end sm:items-center
           justify-center p-4
         "
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" aria-hidden="true" />

      {/* Dialog */}
      <section
        role="dialog"
        aria-modal="true"
        aria-label="Cookie consent"
        className="
          relative w-full max-w-xl rounded-2xl border border-slate-200 bg-white p-4 shadow-soft
          dark:bg-slate-900 dark:border-slate-700
        "
      >
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <UnifiedTitle icon={<Cookie className="h-4 w-4" />} title={t("app.cookieConsentTitle")} subtitle={t("app.cookieConsentBody")} />

          <div>
            <Button id="cookieAccept" onClick={onAccept}>
              {t("app.cookieConsentAccept")}
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
