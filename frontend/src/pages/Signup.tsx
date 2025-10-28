import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import FormInput from "../components/FormInput";
import { extractApiError } from "../lib/httpErrors";

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
    <div className="max-w-md mx-auto card">
      <h1 className="text-2xl font-semibold mb-4">Sign up</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput placeholder={t("signup.email")} type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
        <FormInput placeholder={t("signup.username")} value={username} onChange={e=>setUsername(e.target.value)} required />
        <FormInput placeholder={t("signup.password")} type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
        {error && <p className="text-red-600 text-sm">{t("signup.signupFailed", { message: error })}</p>}
        <button className="btn w-full" type="submit">{t("auth.createAccount")}</button>
      </form>
      <div className="mt-4 text-sm flex justify-between">
        <Link to="/login">{t("auth.signin")}</Link>
      </div>
    </div>
  );
}
