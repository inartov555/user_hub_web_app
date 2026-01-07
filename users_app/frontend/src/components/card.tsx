import React from "react";
import UnifiedTitle from "../components/UnifiedTitle";

export function Card({ children, className = "" }: React.PropsWithChildren<{ className?: string }>) {
  return (
    <div className={
           `relative overflow-hidden rounded-2xl border p-4
            bg-white/75 backdrop-blur shadow-soft ring-1 ring-slate-900/5
            dark:bg-slate-900/50 dark:border-slate-700/70 dark:text-slate-100 dark:ring-white/5
            ${className}
         `}
    >
      <div aria-hidden
           className="
             pointer-events-none absolute inset-x-0 top-0 h-24
             bg-gradient-to-b from-brand-500/10 via-indigo-500/6 to-transparent
             dark:from-brand-400/12 dark:via-indigo-400/8
           "
      />
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, icon }: { title: string; subtitle?: string, icon?: React.ReactElement }) {
  return (
    <>
      {!subtitle && <UnifiedTitle icon={icon} title={title} />}
      {subtitle && <UnifiedTitle icon={icon} title={title} subtitle={subtitle} />}
    </>
  );
}

export function CardBody({ children, className = "" }: React.PropsWithChildren<{ className?: string }>) {
  return <div className={`px-4 sm:px-6 pb-4 sm:pb-6 ${className}`}>{children}</div>;
}
