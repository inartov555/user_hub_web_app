import React from "react";

export function Card({ children, className = "" }: React.PropsWithChildren<{ className?: string }>) {
  return (
    <div className={`rounded-2xl bg-white/80 backdrop-blur border border-white/60 shadow-card ${className}`}>
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="px-4 sm:px-6 pt-4 sm:pt-5 pb-2">
      <h2 className="text-base sm:text-lg font-semibold text-slate-900">{title}</h2>
      {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
    </div>
  );
}

export function CardBody({ children, className = "" }: React.PropsWithChildren<{ className?: string }>) {
  return <div className={`px-4 sm:px-6 pb-4 sm:pb-6 ${className}`}>{children}</div>;
}
