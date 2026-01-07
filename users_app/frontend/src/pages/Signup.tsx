import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import { UserPlus } from "lucide-react";
import { extractApiError } from "../lib/httpErrors";
import FormInput from "../components/FormInput";
import Button from "../components/button";
import PasswordInput from "../components/PasswordInput";
import UnifiedTitle from "../components/UnifiedTitle";
import { SimpleErrorMessage } from "../components/Alerts";
import CustomLink from "../components/CustomLink";

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
      <UnifiedTitle icon={<UserPlus className="h-4 w-4" />} title={t("signup.title")} />
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput placeholder={t("signup.email")}
                   id="email" value={email} onChange={e=>setEmail(e.target.value)} />
        <FormInput placeholder={t("signup.username")}
                   id="username" type="username" value={username} onChange={e=>setUsername(e.target.value)} />
        <PasswordInput placeholder={t("signup.password")}
                       id="password" value={password} onChange={e=>setPassword(e.target.value)} />
        {error && (<SimpleErrorMessage errorUi={t("signup.signupFailed")} errorBackend={error} />)}
        <div id="create" className="mt-2 flex justify-center">
          <Button type="submit">{t("auth.createAccount")}</Button>
        </div>
      </form>
      <div className="mt-4 text-sm flex justify-between">
        <CustomLink title={t("auth.login")} linkTo="/login" />
      </div>
    </div>
  );
}
