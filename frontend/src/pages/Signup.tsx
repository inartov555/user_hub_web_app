import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import FormInput from "../components/FormInput";
import { extractApiError } from "../lib/httpErrors";
import Button from "../components/button";

export default function Signup() {
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      await api.post("/auth/users/", { email, username, password });
      navigate("/login");
    } catch (err: any) {
      const parsed = extractApiError(err as unknown);
      setError(`${parsed.message}`);
    }
  }

  return (
    <div className="max-w-xl mx-auto p-4 rounded-2xl shadow bg-white border dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
      <h1 className="text-2xl font-semibold mb-4">Sign up</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput placeholder={t("signup.email")} className="
            w-full rounded-xl px-3 py-2
            bg-white text-slate-900 placeholder-slate-500
            border border-slate-300
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
            dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700
          " id="email" type="email" value={email} onChange={e=>setEmail(e.target.value)} maxLength={40} required />
        <FormInput placeholder={t("signup.username")} className="
            w-full rounded-xl px-3 py-2
            bg-white text-slate-900 placeholder-slate-500
            border border-slate-300
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
            dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700
          " id="username" type="username" value={username} onChange={e=>setUsername(e.target.value)} maxLength={40} required />
        <FormInput placeholder={t("signup.password")} className="
            w-full rounded-xl px-3 py-2
            bg-white text-slate-900 placeholder-slate-500
            border border-slate-300
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
            dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700
          " id="password" type="password" value={password} onChange={e=>setPassword(e.target.value)} maxLength={40} required />
        {error && <p className="text-red-600 text-sm whitespace-pre-line">{t("signup.signupFailed", { message: error })}</p>}
        <div id="create" className="mt-2 flex justify-center">
          <Button variant="secondary" className="gap-2" type="submit">{t("auth.createAccount")}</Button>
        </div>
      </form>
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
