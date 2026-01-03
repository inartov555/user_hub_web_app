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
import SimpleErrorMessage from "../components/ErrorAlert";

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
    <div className="max-w-xl mx-auto p-4 rounded-2xl shadow bg-white border dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
      <UnifiedTitle icon=<LogIn className="h-4 w-4" /> title={t("auth.login")} />
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput placeholder={t("signup.username")}
                   id="username" type="username" value={username} onChange={e=>setUsername(e.target.value)} />
        <PasswordInput placeholder={t("signup.password")}
                       id="password" value={password} onChange={e=>setPassword(e.target.value)} />
        <SimpleErrorMessage error_message={t("auth.loginFailed"} error={error} />
        <div className="mt-2 flex justify-center">
          <Button type="submit">{t("auth.signin")}</Button>
        </div>
      </form>
      <div className="mt-4 text-sm flex justify-between">
        <Link
          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 underline underline-offset-4 decoration-2
             transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md"
          to="/signup"
        >
          {t("auth.createAccount")}
        </Link>
        <Link
          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 underline underline-offset-4 decoration-2
             transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md"
          to="/reset-password"
        >
          {t("auth.forgotPassword")}
        </Link>
      </div>
    </div>
  );
}
