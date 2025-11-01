import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import FormInput from "../components/FormInput";
import { extractApiError } from "../lib/httpErrors";
import { useAuthStore } from "../auth/store";
import Button from "../components/button";

export default function ChangePassword() {
  const { t, i18n } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const pwRef = useRef<HTMLInputElement | null>(null);
  useEffect(() => { pwRef.current?.focus(); }, []);

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    if (!password || password.length < 8) {
      setError(t("changePassword.atLeast8Chars"));
      return;
    }
    if (password !== confirmPassword) {
      setError(t("changePassword.notMatch"));
      return;
    }

    try {
      setSaving(true);
      await api.post(`/users/${id}/set-password/`, { password });
      navigate("/users", { replace: true });
    } catch (err) {
      const parsed = extractApiError(err as unknown);
      setError(parsed.message || t("changePassword.setPasswordFailed"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-4 rounded-2xl shadow bg-white border dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
      <h1 className="text-2xl font-semibold mb-4">{t("users.changePassword")}</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput
          ref={pwRef}
          placeholder={t("changePassword.newPassword")}
          type="password"
          id="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
          className="
            w-full rounded-xl px-3 py-2
            bg-white text-slate-900 placeholder-slate-500
            border border-slate-300
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
            dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700
          "
        />
        <FormInput
          placeholder={t("changePassword.confirmPassword")}
          type="password"
          id="confirmPassword"
          value={confirmPassword}
          onChange={e => setConfirmPassword(e.target.value)}
          required
          className="
            w-full rounded-xl px-3 py-2
            bg-white text-slate-900 placeholder-slate-500
            border border-slate-300
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
            dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700
          "
        />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <Button variant="secondary" className="gap-2" type="submit" disabled={saving}>
          {saving ? t("changePassword.saving") : t("profileEdit.save")}
        </Button>
        <Button variant="secondary" className="gap-2">
          <Link to="/users">{t("userDeleteConfirm.cancel")}</Link>
        </Button>
      </form>
    </div>
  );
}

