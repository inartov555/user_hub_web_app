import React from "react";

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};
export default function Button({ variant = "primary", className = "", ...props }: Props) {
  const base = "inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm shadow-soft";
  const styles = {
      primary: "bg-brand-600 text-white hover:bg-brand-700 shadow-soft",
      secondary: "bg-white text-slate-900 border border-slate-200 hover:bg-slate-60 shadow-soft",
      ghost: "text-slate-700 hover:bg-slate-100",
  }[variant];
  return <button className={`${base} ${styles} ${className}`} {...props} />;
}
