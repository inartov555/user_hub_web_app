import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { KeySquare } from "lucide-react";
import { api } from "../lib/axios";
import { extractApiError } from "../lib/httpErrors";
import FormInput from "../components/FormInput";
import Button from "../components/button";
import UnifiedTitle from "../components/UnifiedTitle";
import { SimpleErrorMessage, SimpleInfoMessage } from "../components/Alerts";
import CustomLink from "../components/CustomLink";

export default function ResetPassword() {
  const { t, i18n } = useTranslation();
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.post("/auth/users/reset_password/", { email });
      setSent(true);
    } catch (err: any) {
      const parsed = extractApiError(err as unknown);
      setError(parsed.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="
           relative overflow-hidden
           rounded-2xl border p-4
           bg-white/75 backdrop-blur shadow-soft ring-1 ring-slate-900/5
           dark:bg-slate-900/50 dark:border-slate-700/70 dark:text-slate-100 dark:ring-white/5
         "
    >
      <div aria-hidden
           className="
             pointer-events-none absolute inset-x-0 top-0 h-24
             bg-gradient-to-b from-brand-500/10 via-indigo-500/6 to-transparent
             dark:from-brand-400/12 dark:via-indigo-400/8
           "
      />
      <UnifiedTitle icon={<KeySquare className="h-4 w-4" />} title={t("resetPassword.resetPassword")} />
      {sent ? <SimpleInfoMessage message={t("resetPassword.checkEmailForResetLink")} /> : (
        <form onSubmit={onSubmit} className="space-y-3">
          <FormInput placeholder="Email" id="email" value={email} onChange={e=>setEmail(e.target.value)} />
          {error && (<SimpleErrorMessage errorUi={t("resetPassword.resetPasswordFailed")} errorBackend={error} />)}
          <div id="recoverEmail" className="mt-2 flex justify-center">
            <Button type="submit">{t("resetPassword.sendResetEmail")}</Button>
          </div>
        </form>
      )}
      <div className="mt-4 text-sm flex justify-between">
        <CustomLink title={t("auth.login")} linkTo="/login" />
      </div>
    </div>
  );
}
