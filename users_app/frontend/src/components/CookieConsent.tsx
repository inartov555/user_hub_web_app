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
      <div
        className="
          absolute inset-0 bg-gradient-to-b from-slate-900/50 via-slate-900/40 to-black/60 backdrop-blur-md
        "
        aria-hidden="true"
      />
      <div
        className="
          pointer-events-none absolute inset-0 opacity-[0.08]
          [background-image:radial-gradient(circle_at_1px_1px,white_1px,transparent_0)]
          [background-size:18px_18px]
        "
        aria-hidden="true"
      />

      {/* Dialog */}
      <div className="
             relative w-full max-w-xl rounded-2xl border p-4 shadow-lg border-slate-200/80
             bg-[linear-gradient(135deg,#e2e8f0_0%,#cbd5e1_45%,#bfdbfe_100%)] dark:border-slate-700/70
             dark:bg-[linear-gradient(135deg,#1f2937_0%,#374151_55%,#4b5563_100%)]
           "
      >
        <div className="flex flex-col">
          <UnifiedTitle icon={<Cookie className="h-4 w-4" />} title={t("app.cookieConsentTitle")} subtitle={t("app.cookieConsentBody")} />

          <div className="mt-auto flex justify-center pt-4">
            <Button id="cookieAccept" onClick={onAccept}>
              {t("app.cookieConsentAccept")}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
