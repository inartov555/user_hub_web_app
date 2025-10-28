import { useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import FormInput from "../components/FormInput";

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
          <button className="btn w-full" type="submit">{t("resetPassword.sendResetEmail")}</button>
        </form>
      )}
      <div className="mt-4 text-sm flex justify-between">
        <Link to="/login">{t("auth.signin")}</Link>
      </div>
    </div>
  );
}
