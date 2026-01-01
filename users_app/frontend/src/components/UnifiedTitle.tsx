import React from "react";

export default function UnifiedTitle({ title, subtitle, icon }: { title: string; subtitle?: string, icon?: React.ReactElement }) {
  return (
    <div className="px-2 sm:px-4 pt-4 sm:pt-5 pb-4">
      <h2 className="text-base sm:text-lg font-semibold text-slate-900 dark:text-slate-100 inline-flex items-center gap-2">
        <span className="inline-flex items-center gap-2">
          <span className="shrink-0">{icon}</span>
          <span className="leading-none">{title}</span>
        </span>
      </h2>
      {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>}
    </div>
  );
}
