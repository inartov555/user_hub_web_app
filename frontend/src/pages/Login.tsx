import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api, fetchRuntimeAuth } from "../lib/axios";
import { useAuthStore } from "../auth/store";
import FormInput from "../components/FormInput";
import { extractApiError } from "../lib/httpErrors";
import Button from "../components/button";

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
      console.log("Login page; start onSubmit")
      useAuthStore.getState().logout?.(); // clears access+refresh in memory and storage
      console.log("Login page; onSubmit; before /auth/jwt/create/")
      const { data: tokens } = await api.post("/auth/jwt/create/", { username, password });
      useAuthStore.getState().applyRefreshedTokens?.(tokens.access, tokens.refresh);
      console.log("Login page; onSubmit; after applyRefreshedTokens")
      setTokens(tokens.access, tokens.refresh);
      console.log("Login page; onSubmit; after setTokens")
      const { data: me } = await api.get("/auth/users/me/");
      setUser(me);
      console.log("Login page; onSubmit; after setUser(me);")
      const runtime = await fetchRuntimeAuth();
      console.log("Login page; onSubmit; after fetchRuntimeAuth")
      useAuthStore.getState().setRuntimeAuth(runtime);
      console.log("Login page; onSubmit; after setRuntimeAuth")
      // respect the ProtectedRoute’s saved destination
      const intended = localStorage.getItem("postLoginRedirect");
      console.log("login page onSubmit; intended = ", intended)
      if (intended) localStorage.removeItem("postLoginRedirect");
      navigate(intended || "/users"); // navigating to /users and clearing back history
    } catch (err: any) {
      const parsed = extractApiError(err as unknown);
      setError(`${parsed.message}`);
    }
  }

  return (
    <div className="max-w-xl mx-auto p-4 rounded-2xl shadow bg-white border dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
      <h1 className="text-2xl font-semibold mb-4">{t("auth.login")}</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput placeholder={t("signup.username")} className="
            w-full rounded-xl px-3 py-2
            bg-white text-slate-900 placeholder-slate-500
            border border-slate-300
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
            dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700
          " id="username" type="username" value={username} onChange={e=>setUsername(e.target.value)} required />
        <FormInput placeholder={t("signup.password")} className="
            w-full rounded-xl px-3 py-2
            bg-white text-slate-900 placeholder-slate-500
            border border-slate-300
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
            dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700
          " id="password" type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
        {error && <p className="text-red-600 text-sm whitespace-pre-line">{t("auth.loginFailed", { message: error })}</p>}
        <div className="mt-2 flex justify-center">
          <Button variant="secondary" className="gap-2" type="submit">{t("auth.signin")}</Button>
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
