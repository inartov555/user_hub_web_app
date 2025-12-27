import * as React from "react";

type FormInputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: React.ReactNode;
  error?: string;
  className?: string;
};

const FormInput = React.forwardRef<HTMLInputElement, FormInputProps>(
  ({ label, error, className = "", ...props }, ref) => {
    return (
      <label className="block space-y-1">
        {label ? <span className="text-sm text-slate-700">{label}</span> : null}
        <input
          ref={ref}
          className={`w-full rounded-md border px-3 py-2 outline-none focus:ring
                      w-full rounded-xl px-3 py-2
                      bg-white text-slate-900 placeholder-slate-500
                      border border-slate-300
                      focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
                      dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
                      dark:border-slate-700`}
          {...props}
        />
        {error ? <span className="text-xs text-red-600">{error}</span> : null}
      </label>
    );
  }
);

FormInput.displayName = "FormInput";
export default FormInput;
