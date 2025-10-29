import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { fetchAuthSettings, updateAuthSettings, AuthSettings } from "../lib/api/settings";
import { useAuthStore } from "../auth/store";

export default function Settings() {
  const { t } = useTranslation();
  const { user } = useAuthStore();
  const [form, setForm] = useState<AuthSettings>({
    JWT_RENEW_AT_SECONDS: 1200,
    IDLE_TIMEOUT_SECONDS: 900,
    ACCESS_TOKEN_LIFETIME: 1800,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let mounted = true;
    fetchAuthSettings()
      .then((s) => { if (mounted) setForm(s); })
      .catch(() => { if (mounted) setError(t("settings.loadError")); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [t]);

  if (!user?.is_staff) {
    return <div className="max-w-3xl mx-auto p-4">{t("errors.forbidden")}</div>;
  }
  if (loading) return <div className="max-w-3xl mx-auto p-4">{t("common.loading")}</div>;

  function onChange<K extends keyof AuthSettings>(k: K, v: number) {
    setForm((prev) => ({ ...prev, [k]: v }));
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true); setError(null); setSaved(false);
    try {
      const updated = await updateAuthSettings(form);
      setForm(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err: any) {
      setError(err?.response?.data?.detail || t("settings.saveError"));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-4">
      <h1 className="text-xl font-semibold mb-4">{t("settings.title")}</h1>
      <form className="space-y-6" onSubmit={onSubmit}>
        <Field
          label={t("settings.jwtRenew")}
          help={t("settings.jwtRenewHelp")}
          value={form.JWT_RENEW_AT_SECONDS}
          onChange={(v) => onChange("JWT_RENEW_AT_SECONDS", v)}
          min={0}
        />
        <Field
          label={t("settings.idleTimeout")}
          help={t("settings.idleTimeoutHelp")}
          value={form.IDLE_TIMEOUT_SECONDS}
          onChange={(v) => onChange("IDLE_TIMEOUT_SECONDS", v)}
          min={1}
        />
        <Field
          label={t("settings.accessLifetime")}
          help={t("settings.accessLifetimeHelp")}
          value={form.ACCESS_TOKEN_LIFETIME}
          onChange={(v) => onChange("ACCESS_TOKEN_LIFETIME", v)}
          min={1}
        />
        <div className="flex gap-3 items-center">
          <button className="btn" disabled={saving} type="submit">
            {saving ? t("common.saving") : t("common.save")}
          </button>
          {saved && <span className="text-green-600 text-sm">{t("common.saved")}</span>}
          {error && <span className="text-red-600 text-sm">{error}</span>}
        </div>
      </form>
      <p className="text-xs text-slate-500 mt-6">
        {t("settings.noteNewSessions")}
      </p>
    </div>
  );
}

function Field({
  label, help, value, onChange, min = 0,
}: {
  label: string;
  help?: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
}) {
  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium">{label}</label>
      {help && <p className="text-xs text-slate-500">{help}</p>}
      <input
        type="number"
        className="border rounded px-3 py-2 w-60"
        min={min}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value || "0", 10))}
      />
    </div>
  );
}
