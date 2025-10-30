import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import FormInput from "../components/FormInput";
import Button from "../components/button";

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
    <div className="max-w-md mx-auto card">
      <h1 className="text-2xl font-semibold mb-4">{t("resetPassword.resetPassword")}</h1>
      {sent ? <p>{t("resetPassword.checkEmailForResetLink")}</p> : (
        <form onSubmit={onSubmit} className="space-y-3">
          <FormInput placeholder="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
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
