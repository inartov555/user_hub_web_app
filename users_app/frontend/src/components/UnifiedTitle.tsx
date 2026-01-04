import React from "react";

export default function UnifiedTitle({
  title,
  subtitle,
  icon,
}: {
  title: string;
  subtitle?: string;
  icon?: React.ReactElement;
}) {
  return (
    <div className="px-3 sm:px-5 pt-5 sm:pt-6 pb-4">
      <div className="flex items-start gap-3">
        {icon && (
          <span
            className="
              shrink-0 inline-flex h-10 w-10 items-center justify-center rounded-2xl
              bg-slate-900/5 dark:bg-slate-50/10
              ring-1 ring-slate-900/10 dark:ring-slate-50/10 shadow-sm
            "
          >
            <span className="text-slate-700 dark:text-slate-200 [&>svg]:h-5 [&>svg]:w-5">
              {icon}
            </span>
          </span>
        )}

        <div className="min-w-0">
          <h2
            data-tag="pageTitle"
            className="
              relative inline-flex items-center
              text-lg sm:text-xl font-semibold tracking-tight
              text-slate-900 dark:text-slate-50
            "
          >
            <span className="truncate">{title}</span>

            {/* Accent underline */}
            <span
              aria-hidden="true"
              className="
                absolute -bottom-2 left-0 h-[3px] w-14 rounded-full
                bg-gradient-to-r from-red-500/70 via-orange-400/60 to-transparent
                dark:from-red-400/70 dark:via-orange-300/60
              "
            />
          </h2>

          {subtitle && (
            <p data-tag="pageSubtitle" 
               className="
                 mt-2 max-w-prose text-sm sm:text-[0.95rem] leading-relaxed text-slate-600 dark:text-slate-300
               "
            >
              {subtitle}
            </p>
          )}
        </div>
      </div>

      {/* Soft divider */}
      <div className="
             mt-4 h-px w-full bg-gradient-to-r from-slate-200 via-slate-200/60 to-transparent
             dark:from-slate-700 dark:via-slate-700/60
           "
      />
    </div>
  );
}
