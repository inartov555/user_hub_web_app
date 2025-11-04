import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { fetchAuthSettings, updateAuthSettings, AuthSettings } from "../lib/settings";
import { useAuthStore } from "../auth/store";
import { extractApiError } from "../lib/httpErrors";
import Button from "../components/button";
import { fetchRuntimeAuth } from "../lib/settings";

export default function Settings() {
  const { t } = useTranslation();
  const { user } = useAuthStore();
  const [form, setForm] = useState<AuthSettings>({
    JWT_RENEW_AT_SECONDS: 1200,
    IDLE_TIMEOUT_SECONDS: 900,
    ACCESS_TOKEN_LIFETIME: 1800,
    ROTATE_REFRESH_TOKENS: true
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let mounted = true;
    fetchAuthSettings()
      .then((s) => { if (mounted) setForm(s); })
      .catch(() => { if (mounted) setError(t("appSettings.loadError")); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [t]);

  if (!user?.is_staff) {
    return <div className="max-w-3xl mx-auto p-4">{t("errors.forbidden")}</div>;
  }
  if (loading) return <div className="max-w-3xl mx-auto p-4">{t("users.loading")}</div>;

  function onChange<K extends keyof AuthSettings>(k: K, v: AuthSettings[K]) {
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
      const parsed = extractApiError(err as unknown);
      setError(`${t("appSettings.saveError")} ${parsed.message}`);
    } finally {
      setSaving(false);
      await fetchRuntimeAuth(); // let's store the fresh settings values
      useAuthStore.getState().setRuntimeAuth();
    }
  }

  return (
    <div className="max-w-xl mx-auto p-4 rounded-2xl shadow bg-white border dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
      <div className="max-w-3xl mx-auto p-4">
        <h1 className="text-xl font-semibold mb-4">{t("appSettings.title")}</h1>
        <form className="space-y-6" onSubmit={onSubmit}>
          {/* Rotate refresh tokens (controls visibility & value of renewAtSeconds) */}
          <label className="block text-sm font-medium">{t("appSettings.jwtRotateTokens")}</label>
          <p className="text-xs text-slate-500">{t("appSettings.jwtRotateTokensHelp")}</p>
          <select
            id="rotateRefreshTokens"
              className="w-full rounded-xl px-3 py-2
              bg-white text-slate-900 placeholder-slate-500
              border border-slate-300
              focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
              dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
              dark:border-slate-700"
            value={String(Boolean(form.ROTATE_REFRESH_TOKENS))}
            onChange={(e) => {
              const next = e.target.value === "true";

              if (next) {
                const base = Number(form.ACCESS_TOKEN_LIFETIME) || 0;
                const renew = Math.floor(base * 0.7);
                onChange("JWT_RENEW_AT_SECONDS", renew);
                onChange("ROTATE_REFRESH_TOKENS", true);
              } else {
                onChange("JWT_RENEW_AT_SECONDS", 0);
                onChange("ROTATE_REFRESH_TOKENS", false);
              }
            }}
          >
            <option value="true">true</option>
            <option value="false">false</option>
          </select>
          {/* Renew at (conditionally visible) */}
          {form.ROTATE_REFRESH_TOKENS && (
            <Field
              id="renewAtSeconds"
              label={t("appSettings.jwtRenew")}
              help={t("appSettings.jwtRenewHelp")}
              value={form.JWT_RENEW_AT_SECONDS}
              onChange={(v) => onChange("JWT_RENEW_AT_SECONDS", v)}
              min={0}
            />
          )}
          <Field
            id="idleTimeoutSeconds"
            label={t("appSettings.idleTimeout")}
            help={t("appSettings.idleTimeoutHelp")}
            value={form.IDLE_TIMEOUT_SECONDS}
            onChange={(v) => onChange("IDLE_TIMEOUT_SECONDS", v)}
            min={1}
          />
          {/* Access token lifetime (also keeps renewAtSeconds at 70% if rotate=true) */}
          <Field
            id="accessTokenLifetime"
            label={t("appSettings.accessLifetime")}
            help={t("appSettings.accessLifetimeHelp")}
            value={form.ACCESS_TOKEN_LIFETIME}
            onChange={(v) => {
              onChange("ACCESS_TOKEN_LIFETIME", v);
              if (form.ROTATE_REFRESH_TOKENS) {
                const base = Number(v) || 0;
                const renew = Math.floor(base * 0.7);
                onChange("JWT_RENEW_AT_SECONDS", renew);
              }
            }}
            min={1}
          />
          <div className="flex gap-3 items-center">
            <Button variant="secondary" className="border-red-600 text-red-700 hover:bg-red-50" disabled={saving} type="submit">
              {saving ? t("appSettings.saving") : t("profileEdit.save")}
            </Button>
            {saved && <span className="text-green-600 text-sm">{t("appSettings.saved")}</span>}
            {error && <span className="text-red-600 text-sm">{error}</span>}
          </div>
        </form>
      </div>
    </div>
  );
}

function Field({
  label, help, value, onChange, id, min = 0,
}: {
  label: string;
  help?: string;
  value: number;
  onChange: (v: number) => void;
  id: string;
  min?: number;
}) {
  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium">{label}</label>
      {help && <p className="text-xs text-slate-500">{help}</p>}
      <input
        id={id}
        type="number"
        min={min}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value || "0", 10))}
        className="
            w-full rounded-xl px-3 py-2
            bg-white text-slate-900 placeholder-slate-500
            border border-slate-300
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
            dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700
          "
      />
    </div>
  );
}
