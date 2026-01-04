import React from "react";
import UnifiedTitle from "../components/UnifiedTitle";

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
    <>
      {!subtitle && <UnifiedTitle icon={icon} title={title} />}
      {subtitle && <UnifiedTitle icon={icon} title={title} subtitle={subtitle} />}
    </>
  );
}

export function CardBody({ children, className = "" }: React.PropsWithChildren<{ className?: string }>) {
  return <div className={`px-4 sm:px-6 pb-4 sm:pb-6 ${className}`}>{children}</div>;
}
