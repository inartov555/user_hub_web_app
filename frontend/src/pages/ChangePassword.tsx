import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import FormInput from "../components/FormInput";
import { extractApiError } from "../lib/httpErrors";
import { useAuthStore } from "../auth/store";

export default function ChangePassword() {
  const { t, i18n } = useTranslation();s
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
    <div className="max-w-md mx-auto card p-4 rounded-2xl border bg-white">
      <h1 className="text-2xl font-semibold mb-4">{t("users.changePassword")}</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput
          ref={pwRef}
          placeholder={t("changePassword.newPassword")}
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <FormInput
          placeholder={t("changePassword.confirmPassword")}
          type="password"
          value={confirmPassword}
          onChange={e => setConfirmPassword(e.target.value)}
          required
        />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button className="btn w-full" type="submit" disabled={saving}>
          {saving ? t("changePassword.saving") : t("profileEdit.save")}
        </button>
      </form>
    </div>
  );
}

