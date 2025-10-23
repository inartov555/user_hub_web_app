import * as React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "outline";
  size?: "sm" | "md";
};

export function Button({ variant = "default", size = "md", className = "", ...props }: ButtonProps) {
  const base = "inline-flex items-center justify-center rounded-xl px-4 py-2 border transition-colors";
  const v = variant === "outline" ? "border-slate-200 bg-transparent hover:bg-slate-50"
                                  : "border-slate-200 bg-white hover:bg-slate-50";
  const s = size === "sm" ? "text-sm px-3 py-1.5" : "";
  return <button className={'${base} ${v} ${s} ${className}'} {...props} />;
}
