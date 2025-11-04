import * as React from "react";

type PasswordInputProps = Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> & {
  label?: React.ReactNode;
  error?: string;
  className?: string;
  id: string;
};

export default function PasswordInput({ label, error, className = "", id, ...props }: PasswordInputProps) {
  const [show, setShow] = React.useState(false);
  return (
    <label className="block space-y-1">
      {label ? <span className="text-sm text-slate-700">{label}</span> : null}
      <div className="relative">
        <input
          id={id}
          type={show ? "text" : "password"}
          className={`w-full rounded-md border px-3 py-2 pr-10 outline-none focus:ring ${className}`}
          {...props}
        />
        <button
          type="button"
          aria-label={show ? "Hide password" : "Show password"}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-sm"
          onClick={() => setShow((s) => !s)}
        >
          {show ? "Hide" : "Show"}
        </button>
      </div>
      {error ? <span className="text-xs text-red-600">{error}</span> : null}
    </label>
  );
}
