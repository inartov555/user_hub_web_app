import * as React from "react";
import { useTranslation } from "react-i18next";

type PasswordInputProps = Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> & {
  label?: React.ReactNode;
  error?: string;
  className?: string;
  id: string;
};

export default function PasswordInput({ label, error, className = "", id, ...props }: PasswordInputProps) {
  const { t } = useTranslation();
  const [show, setShow] = React.useState(false);
  return (
    <label className="block space-y-1">
      {label ? <span className="text-sm text-slate-700">{label}</span> : null}
      <div className="relative">
        <input
          id={id}
          maxLength={40}
          type={show ? "text" : "password"}
          className={`w-full rounded-md border px-3 py-2 pr-10 outline-none focus:ring ${className}`}
          {...props}
        />
        <button
          type="button"
          data-tag={show ? "hide" : "show"}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-sm"
          onClick={() => setShow((s) => !s)}
        >
          {show ? <>{t("passwordComponent.hide")}</> : <>{t("passwordComponent.show")}</>}
        </button>
      </div>
      {error ? <span className="text-xs text-red-600">{error}</span> : null}
    </label>
  );
}
