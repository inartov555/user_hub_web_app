import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import FormInput from "../components/FormInput";
import Button from "../components/button";
import { extractApiError } from "../lib/httpErrors";

export default function ResetPassword() {
  const { t, i18n } = useTranslation();
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    await api.post("/auth/users/reset_password/", { email });
    setSent(true);
  }

  return (
    <div className="max-w-xl mx-auto p-4 rounded-2xl shadow bg-white border dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
      <h1 className="text-2xl font-semibold mb-4">{t("resetPassword.resetPassword")}</h1>
      {sent ? <p>{t("resetPassword.checkEmailForResetLink")}</p> : (
        <form onSubmit={onSubmit} className="space-y-3">
          <FormInput placeholder="Email" type="email" className="
            w-full rounded-xl px-3 py-2
            bg-white text-slate-900 placeholder-slate-500
            border border-slate-300
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
            dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700
          " value={email} onChange={e=>setEmail(e.target.value)} required />
          <div className="mt-2 flex justify-center">
            <Button variant="secondary" className="gap-2" type="submit">{t("resetPassword.sendResetEmail")}</Button>
          </div>
        </form>
      )}
      <div className="mt-4 text-sm flex justify-between">
        <Link
          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 underline underline-offset-4 decoration-2
             transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md"
          to="/login"
        >
          {t("auth.signin")}
        </Link>
      </div>
    </div>
  );
}
