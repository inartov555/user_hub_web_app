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
           max-w-xl mx-auto p-4 rounded-2xl shadow bg-white border dark:bg-slate-800
           dark:text-slate-100 dark:border-slate-700
         "
    >
      <UnifiedTitle icon={<KeySquare className="h-4 w-4" />} title={t("resetPassword.resetPassword")} />
      {sent ? <SimpleInfoMessage message={t("resetPassword.checkEmailForResetLink")} /> : (
        <form onSubmit={onSubmit} className="space-y-3">
          <FormInput placeholder="Email" id="email" value={email} onChange={e=>setEmail(e.target.value)} />
          {/* {error && <SimpleErrorMessage errorBackend={error} />} */}
          {error && (<SimpleErrorMessage errorUi={t("resetPassword.resetPasswordFailed")} errorBackend={error} />)}
          <div id="recoverEmail" className="mt-2 flex justify-center">
            <Button type="submit">{t("resetPassword.sendResetEmail")}</Button>
          </div>
        </form>
      )}
      <div className="mt-4 text-sm flex justify-between">
        <CustomLink title={t("auth.signin")} linkTo="/login" />
      </div>
    </div>
  );
}
