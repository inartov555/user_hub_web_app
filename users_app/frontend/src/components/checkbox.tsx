import * as React from "react";

type CheckboxProps = Omit<React.InputHTMLAttributes<HTMLInputElement>, "type" | "size"> & {
  variant?: "default" | "outline";
  size?: "sm" | "md";
  label?: React.ReactNode;
  indeterminate?: boolean;
};

export function Checkbox({
  variant = "default",
  size = "md",
  className = "",
  label,
  indeterminate = false,
  ...props
}: CheckboxProps) {
  const ref = React.useRef<HTMLInputElement>(null);

  React.useEffect(() => {
    if (ref.current) {
      ref.current.indeterminate = !!indeterminate;
    }
  }, [indeterminate]);

  const boxBase = "h-4 w-4 rounded border";
  const boxVariant =
    variant === "outline"
      ? "border-slate-300 bg-transparent hover:bg-slate-50"
      : "border-slate-300 bg-white hover:bg-slate-50";
  const boxSize = size === "sm" ? "h-3.5 w-3.5" : "";

  return (
    <label className="inline-flex items-center gap-2 cursor-pointer">
      <input
        ref={ref}
        type="checkbox"
        className={`${boxBase} ${boxVariant} ${boxSize} ${className}`}
        {...props}
      />
      {label ? <span className={size === "sm" ? "text-sm" : ""}>{label}</span> : null}
    </label>
  );
}
