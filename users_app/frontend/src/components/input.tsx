import * as React from "react";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className = "", ...props }, ref) => (
    <input
      ref={ref}
      className={`w-full rounded-xl border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-300
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
  )
);
Input.displayName = "Input";
