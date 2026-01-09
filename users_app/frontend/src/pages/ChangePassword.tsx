import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { KeyRound } from "lucide-react";
import { api } from "../lib/axios";
import { extractApiError } from "../lib/httpErrors";
import { useAuthStore } from "../auth/store";
import FormInput from "../components/FormInput";
import Button from "../components/button";
import PasswordInput from "../components/PasswordInput";
import UnifiedTitle from "../components/UnifiedTitle";
import { SimpleErrorMessage } from "../components/Alerts";
import { Card } from "../components/card";

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

    try {
      setSaving(true);
      await api.post(`/users/${id}/set-password/`, { password, "confirm_password": confirmPassword });
      navigate("/users", { replace: true });
    } catch (err) {
      const parsed = extractApiError(err as unknown);
      setError(parsed.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card className="max-w-xl mx-auto">
      <UnifiedTitle icon={<KeyRound className="h-4 w-4" />} title={t("users.changePassword")} />
      <form onSubmit={onSubmit} className="space-y-3">
        <PasswordInput placeholder={t("changePassword.newPassword")}
                       id="password"
                       value={password}
                       onChange={e => setPassword(e.target.value)} />
        <PasswordInput placeholder={t("changePassword.confirmPassword")}
                       id="confirmPassword"
                       value={confirmPassword}
                       onChange={e => setConfirmPassword(e.target.value)} />
        {error && <SimpleErrorMessage errorUi={t("changePassword.setPasswordFailed")} errorBackend={error} />}
        <div className="flex gap-2 justify-center">
          <Button id="changePassword" type="submit" disabled={saving}>
            {saving ? t("changePassword.saving") : t("profileEdit.save")}
          </Button>
          <Button id="cancel" onClick={() => navigate("/users")}>
            {t("userDeleteConfirm.cancel")}
          </Button>
        </div>
      </form>
    </Card>
  );
}

