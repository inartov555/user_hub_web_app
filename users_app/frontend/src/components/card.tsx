import React from "react";

export function Card({ children, className = "" }: React.PropsWithChildren<{ className?: string }>) {
  return (
    <div className={`rounded-2xl border shadow-card backdrop-blur
                  bg-white/80 border-white/60
                  dark:bg-slate-800/80 dark:border-slate-700/60
                  ${className}`}>
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, icon }: { title: string; subtitle?: string, icon?: React.ReactElement }) {
  return (
    <div className="px-2 sm:px-4 pt-4 sm:pt-5 pb-4">
      <h2 className="text-base sm:text-lg font-semibold text-slate-900 dark:text-slate-100 inline-flex items-center gap-2">
        <span className="shrink-0">{icon}</span>
        <span className="leading-none">{title}</span>
      </h2>
      {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>}
    </div>
  );
}

export function CardBody({ children, className = "" }: React.PropsWithChildren<{ className?: string }>) {
  return <div className={`px-4 sm:px-6 pb-4 sm:pb-6 ${className}`}>{children}</div>;
}
