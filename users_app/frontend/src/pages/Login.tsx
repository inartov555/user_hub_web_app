import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { LogIn } from "lucide-react";
import { api } from "../lib/axios";
import { extractApiError } from "../lib/httpErrors";
import { fetchRuntimeAuth } from "../lib/settings";
import { useAuthStore } from "../auth/store";
import FormInput from "../components/FormInput";
import Button from "../components/button";
import PasswordInput from "../components/PasswordInput";
import UnifiedTitle from "../components/UnifiedTitle";
import { SimpleErrorMessage } from "../components/Alerts";
import CustomLink from "../components/CustomLink";

export default function Login() {
  const { t } = useTranslation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { setTokens, setUser, user } = useAuthStore();
  const { pathname } = useLocation();
  
  // if already logged in, leave /login immediately
  useEffect(() => {
    if (user) {
      const intended = localStorage.getItem("postLoginRedirect");
      if (intended) localStorage.removeItem("postLoginRedirect");
      navigate(intended || "/users", { replace: true });
    }
  }, [user, navigate]);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      useAuthStore.getState().logout?.(); // clears access+refresh in memory and storage
      const { data: tokens } = await api.post("/auth/jwt/create/", { username, password });
      useAuthStore.getState().applyRefreshedTokens?.(tokens.access, tokens.refresh);
      setTokens(tokens.access, tokens.refresh);
      const { data: me } = await api.get("/auth/users/me/");
      setUser(me);
      await fetchRuntimeAuth(); // let's store the fresh settings values
      useAuthStore.getState().setRuntimeAuth(); // let's set the run time settings
      // respect the ProtectedRoute’s saved destination
      const intended = localStorage.getItem("postLoginRedirect");
      if (intended) localStorage.removeItem("postLoginRedirect");
      navigate(intended || "/users", { replace: true }); // navigating to /users and clearing back history
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
      <UnifiedTitle icon={<LogIn className="h-4 w-4" />} title={t("auth.login")} />
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput placeholder={t("signup.username")}
                   id="username" type="username" value={username} onChange={e=>setUsername(e.target.value)} />
        <PasswordInput placeholder={t("signup.password")}
                       id="password" value={password} onChange={e=>setPassword(e.target.value)} />
        {error && (<SimpleErrorMessage errorUi={t("auth.loginFailed")} errorBackend={error} />)}
        <div className="mt-2 flex justify-center">
          <Button type="submit">{t("auth.login")}</Button>
        </div>
      </form>
      <div className="mt-4 text-sm flex justify-between">
        <CustomLink title={t("auth.createAccount")} linkTo="/signup" />
        <CustomLink title={t("auth.forgotPassword")} linkTo="/reset-password" />
      </div>
    </div>
  );
}
