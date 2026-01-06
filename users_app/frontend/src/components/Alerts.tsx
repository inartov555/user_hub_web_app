import * as React from "react";
import { AlertTriangle, CheckCircle, Info } from "lucide-react";

export function SimpleErrorMessage({ errorUi, errorBackend }: { errorUi?: string, errorBackend?: string | null; } ) {
  /*
   * errorUi (string): this one describes UI error, e.g., auth.loginFailed
   * errorBackend (string): backend error
   */
  if (!errorUi && !errorBackend) return null;
  // const text = [errorUi, errorBackend].filter(Boolean).join(" ");
  return (
    <div data-tag="simpleErrorMessage"
         className="
           rounded-xl border border-rose-200/60 bg-rose-50/40 px-3 py-2
           backdrop-blur-sm text-sm text-rose-600 whitespace-pre-line
           dark:border-rose-500/25 dark:bg-rose-950/20 dark:text-rose-300
         "
    >
      <div className="mt-4 mb-2 text-sm flex">
        <AlertTriangle className="h-6 w-6 text-rose-600 dark:text-rose-300" />
        {errorUi && <span className="ml-2 mt-1">{errorUi}</span>}
      </div>
      <div className="ml-2">{errorBackend && <span>{errorBackend}</span>}</div>
    </div>
  );
}

export function SimpleSuccessMessage({ message, block }: { message?: string; block?: React.ReactElement; }) {
  /*
   * It maybe either message or HTML block, or both
   */
  if (!message && !block) return null;

  return (
    <div
      data-tag="simpleSuccessMessage"
      className="
        rounded-xl border border-emerald-200/60 bg-emerald-50/40 px-3 py-2
        backdrop-blur-sm text-sm text-emerald-800 whitespace-pre-line
        dark:border-emerald-400/25 dark:bg-emerald-950/20 dark:text-emerald-100
      "
    >
      <div className="mt-4 mb-2 text-sm flex">
        <CheckCircle className="h-6 w-6 mb-2 mt-2 text-emerald-800 dark:text-emerald-100" />
        { message && <span className="ml-2 mt-1">{message}</span> }
      </div>
      <div className="ml-2">{ block }</div>
    </div>
  );
}

export function SimpleInfoMessage({ message, block }: { message?: string; block?: React.ReactElement; }) {
  /*
   * It maybe either message or HTML block, or both
   */
  if (!message && !block) return null;

  return (
    <div
      data-tag="simpleInfoMessage"
      className="
        rounded-xl border border-sky-200/60 bg-sky-50/40 px-3 py-2
        backdrop-blur-sm text-sm text-sky-800 whitespace-pre-line
        dark:border-sky-400/25 dark:bg-sky-950/20 dark:text-sky-200
      "
    >
      <div className="mt-4 mb-2 text-sm flex">
        <Info className="h-6 w-6 mb-2 mt-2 text-sky-800 dark:text-sky-200" />
        { message && <span className="ml-2 mt-1">{message}</span> }
      </div>
      <div className="ml-2">{ block }</div>
    </div>
  );
}
