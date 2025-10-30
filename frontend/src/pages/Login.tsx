import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
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

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      useAuthStore.getState().logout?.(); // clears access+refresh in memory and storage
      const { data: tokens } = await api.post("/auth/jwt/create/", { username, password });
      useAuthStore.getState().applyRefreshedTokens?.(tokens.access, tokens.refresh);
      setTokens(tokens.access, tokens.refresh);
      const { data: me } = await api.get("/auth/users/me/");
      setUser(me);
      navigate("/users", { replace: true }); // navigating to /users and clearing back history
    } catch (err: any) {
      const parsed = extractApiError(err as unknown);
      setError(`${parsed.message}`);
    }
  }

  return (
    <div className="max-w-md mx-auto card">
      <h1 className="text-2xl font-semibold mb-4">{t("auth.login")}</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput placeholder={t("signup.username")} type="username" value={username} onChange={e=>setUsername(e.target.value)} required />
        <FormInput placeholder={t("signup.password")} type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
        {error && <p className="text-red-600 text-sm">{t("auth.loginFailed", { message: error })}</p>}
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
