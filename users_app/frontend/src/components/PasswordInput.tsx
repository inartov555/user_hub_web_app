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
      <div data-tag="passwordField" className="relative">
        <input
          id={id}
          maxLength={40}
          type={show ? "text" : "password"}
          className={`
            w-full rounded-xl px-3 py-2
            bg-white text-slate-900 placeholder-slate-500
            border border-slate-300
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
            dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700
            ${className}
          `}
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
