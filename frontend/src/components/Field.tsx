type FieldProps = {
  label: string;
  value: string;
  className?: string; // styles the value box
};

export default function Field({ label, value, className = "" }: FieldProps) {
  return (
    <div>
      <div className="text-xs font-medium text-slate-500 dark:text-slate-400">{label}</div>
      <div
        className={[
          "mt-1 rounded-md border px-3 py-2",
          "bg-slate-50 text-slate-900 border-slate-300",
          "dark:bg-slate-900 dark:text-slate-100 dark:border-slate-700",
          className,
        ].join(" ")}
      >
        {value}
      </div>
    </div>
  );
}
