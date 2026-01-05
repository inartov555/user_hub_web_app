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
           max-w-xl mx-auto p-4 rounded-2xl shadow bg-white border dark:bg-slate-800
           dark:text-slate-100 dark:border-slate-700
         "
    >
      <UnifiedTitle icon={<UserPlus className="h-4 w-4" />} title={t("signup.title")} />
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput placeholder={t("signup.email")}
                   id="email" value={email} onChange={e=>setEmail(e.target.value)} />
        <FormInput placeholder={t("signup.username")}
                   id="username" type="username" value={username} onChange={e=>setUsername(e.target.value)} />
        <PasswordInput placeholder={t("signup.password")}
                       id="password" value={password} onChange={e=>setPassword(e.target.value)} />
        {error && <SimpleErrorMessage errorBackend={t("signup.signupFailed", { message: error })} />}
        <div id="create" className="mt-2 flex justify-center">
          <Button type="submit">{t("auth.createAccount")}</Button>
        </div>
      </form>
      <div className="mt-4 text-sm flex justify-between">
        <Link
          className="
            inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 underline underline-offset-4 decoration-2
            transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md
          "
          to="/login"
        >
          {t("auth.signin")}
        </Link>
      </div>
    </div>
  );
}
