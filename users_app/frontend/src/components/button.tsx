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
    "inline-flex items-center justify-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold " +
    "transition-all duration-200 select-none " +
    "focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 focus-visible:ring-offset-2 " +
    "dark:focus-visible:ring-brand-300 dark:focus-visible:ring-offset-slate-950";

  const styles =
    {
      primary:
        "text-white shadow-soft " +
        "bg-gradient-to-r from-brand-600/90 via-fuchsia-600/75 to-indigo-600/75 " +
        "hover:brightness-[1.02] hover:shadow-card " +
        "active:translate-y-[0.5px] active:brightness-[0.99] " +
        "ring-1 ring-white/10",

      secondary:
        "text-slate-900 dark:text-slate-100 " +
        "bg-white/70 dark:bg-slate-900/55 backdrop-blur " +
        "border border-slate-200/70 dark:border-slate-700/60 " +
        "shadow-sm hover:shadow-soft " +
        "hover:bg-white/80 dark:hover:bg-slate-900/65 " +
        "active:translate-y-[0.5px]",

      ghost:
        "text-slate-700 dark:text-slate-200 " +
        "bg-transparent " +
        "hover:bg-slate-100/60 dark:hover:bg-white/8 " +
        "active:bg-slate-200/50 dark:active:bg-white/12 " +
        "active:translate-y-[0.5px]",
    }[variant] || "";

  const disabledStyles =
    {
      primary:
        "bg-slate-400/60 text-white/75 shadow-none ring-0",
      secondary:
        "bg-slate-100/60 text-slate-400 border-slate-200/60 shadow-none dark:bg-slate-900/35 dark:text-slate-500 dark:border-slate-800",
      ghost:
        "text-slate-400 dark:text-slate-500",
    }[variant] || "bg-slate-200 text-slate-500";

  const commonDisabled =
    "cursor-not-allowed opacity-80 pointer-events-none";

  return (
    <button
      className={`${base} ${disabled ? `${disabledStyles} ${commonDisabled}` : styles} ${className}`}
      disabled={disabled}
      {...props}
    />
  );
}
