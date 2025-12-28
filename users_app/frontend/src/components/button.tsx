import React from "react";

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};

export default function Button({
  variant = "primary",
  className = "",
  disabled,
  ...props
}: Props) {
  const base =
    "inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm shadow-soft transition-colors";

  const styles =
    {
      primary: "bg-brand-600 text-white hover:bg-brand-700",
      secondary: "bg-white text-slate-900 border border-slate-200 hover:bg-slate-50",
      ghost: "text-slate-700 hover:bg-slate-100",
    }[variant] || "";

  // more obvious disabled colors per variant + no hover + cursor
  const disabledStyles =
    {
      primary: "bg-slate-300 text-slate-600",
      secondary: "bg-slate-100 text-slate-400 border-slate-200",
      ghost: "text-slate-400",
    }[variant] || "bg-slate-200 text-slate-500";

  const commonDisabled = "cursor-not-allowed opacity-80 shadow-none hover:bg-none";

  return (
    <button
      className={`${base} ${disabled ? `${disabledStyles} ${commonDisabled}` : styles} ${className}`}
      disabled={disabled}
      {...props}
    />
  );
}
